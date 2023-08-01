import os
import uuid

import dask.dataframe as dd
import lambdaprompt
import numpy as np
import requests
from IPython.display import HTML, display
from sketch import Portfolio
from sketch.pandas_extension import (ask_from_parts, howto_from_parts, retrieve_name, string_repr_truncated, strtobool,
                                     to_b64, validate_pycode_result)


def get_parts_from_df(df: dd.DataFrame, useSketches=False):

    index_col_name = df.index.name
    df = df.reset_index()
    column_names = [str(x) for x in df.columns]
    data_types = [str(x) for x in df.dtypes]
    if useSketches:
        extras = list(Portfolio.from_dataframe(df).sketchpads.values())
        # extras = [get_description_of_sketchpad(sketchpad) for sketchpad in sketchpads]
    else:
        extras = []
        for col in df.columns:
            extra = {
                "rows": len(df[col]),
                "count": int(df[col].compute().count()),
                "uniquecount": int(df[col].astype(str).compute().nunique()),
                "head-sample": str(
                    [string_repr_truncated(x) for x in df[col].head(5).tolist()]
                ),
            }
            # if column is numeric, get quantiles
            if df[col].dtype in [np.float64, np.int64]:
                extra["quantiles"] = str(
                    df[col].quantile([0, 0.25, 0.5, 0.75, 1]).compute().tolist()
                )
            extras.append(extra)
    return column_names, data_types, extras, index_col_name


def call_prompt_on_dataframe(df: dd.DataFrame, prompt, **kwargs):
    names = retrieve_name(df)
    name = "df" if len(names) == 0 else names[0]
    column_names, data_types, extras, index_col_name = get_parts_from_df(df)
    max_columns = int(os.environ.get("SKETCH_MAX_COLUMNS", "20"))
    if len(column_names) > max_columns:
        raise ValueError(
            f"Too many columns ({len(column_names)}), max is {max_columns} in current version (set SKETCH_MAX_COLUMNS to override)"
        )
    prompt_kwargs = dict(
        dfname=name,
        column_names=to_b64(column_names),
        data_types=to_b64(data_types),
        extras=to_b64(extras),
        index_col_name=index_col_name,
        **kwargs,
    )
    # We now have all of our vars, let's decide if we use an external service or local prompt
    if strtobool(os.environ.get("SKETCH_USE_REMOTE_LAMBDAPROMPT", "True")):
        url = os.environ.get("SKETCH_ENDPOINT_URL", "https://prompts.approx.dev")
        try:
            response = requests.get(
                f"{url}/prompt/{prompt.name}",
                params=prompt_kwargs,
            )
            response.raise_for_status()
            text_to_copy = response.json()
        except Exception as e:
            print(
                f"""Failed to use remote {url}.. {str(e)}.
Consider setting SKETCH_USE_REMOTE_LAMBDAPROMPT=False
and run with your own open-ai key
"""
            )
            text_to_copy = "SKETCH ERROR - see print logs for full error"
    else:
        # using local version
        text_to_copy = prompt(**prompt_kwargs)
    return text_to_copy


@dd.extensions.register_dataframe_accessor("sketch")
class SketchHelper:
    def __init__(self, dataframe):
        self._obj = dataframe

    def howto(self, how, call_display=True):
        result = call_prompt_on_dataframe(self._obj, howto_from_parts, how=how)
        validate_pycode_result(result)
        if not call_display:
            return result
        # output text in a <pre>, also on the side (on top) include a `copy` button that puts it onto clipboard
        uid = uuid.uuid4()
        b64_encoded_result = to_b64(result)
        display(
            HTML(
                f"""<div style="display:flex;flex-direction:row;justify-content:space-between;">
                <pre style="width: 100%; white-space: pre-wrap;" id="{uid}">{result}</pre>
                <button style="height: fit-content;" onclick="navigator.clipboard.writeText(JSON.parse(atob(`{b64_encoded_result}`)))">Copy</button>
                </div>"""
            )
        )

    def ask(self, question, call_display=True):
        result = call_prompt_on_dataframe(self._obj, ask_from_parts, question=question)
        if not call_display:
            return result
        display(HTML(f"""{result}"""))

    def apply(self, prompt_template_string, **kwargs):
        row_limit = int(os.environ.get("SKETCH_ROW_OVERRIDE_LIMIT", "10"))
        if len(self._obj) > row_limit:
            raise RuntimeError(
                f"Too many rows for apply \n (SKETCH_ROW_OVERRIDE_LIMIT: {row_limit}, Actual: {len(self._obj)})"
            )
        new_gpt3_prompt = lambdaprompt.Completion(prompt_template_string)
        named_args = new_gpt3_prompt.get_named_args()
        known_args = set(self._obj.columns) | set(kwargs.keys())
        needed_args = set(named_args)
        if needed_args - known_args:
            raise RuntimeError(
                f"Missing: {needed_args - known_args}\nKnown: {known_args}"
            )

        def apply_func(row):
            row_dict = row.to_dict()
            row_dict.update(kwargs)
            return new_gpt3_prompt(**row_dict)

        return self._obj.apply(apply_func, axis=1)
