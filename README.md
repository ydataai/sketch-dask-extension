[![YData.ai](https://img.shields.io/badge/ydata.ai-12100E?style=for-the-badge&logoColor=white)](https://ydata.ai)
[![Discord](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/mw7xjJ7b7s)

[![pypi](https://img.shields.io/pypi/v/sketch-dask-extension)](https://pypi.org/project/sketch-dask-extension)
![Pythonversion](https://img.shields.io/badge/python-3.10-blue)
[![downloads](https://pepy.tech/badge/sketch-dask-extension/month)](https://pepy.tech/project/sketch-dask-extension)


# Sketch Dask Extension

This is a very simple extension to extend the support of [Sketch](https://github.com/approximatelabs/sketch) to Dask Dataframes instead of only Pandas.
This is **experimental** and not meant to be used in critical environments.

## How to install

```bash
python -m pip install sketch-dask-extension
```

## How to use

```python
import dask
import sketch-dask-extension

dataframe = dask.read_csv('...')

dataframe.sketch.ask('tell me something interesting')
```

# Contributing
We are open to collaboration! If you want to start contributing you can in different ways:
- Search for an issue in which you would like to work and open a PR with the resolution.
- Create an issue with something that you would like to see and work on it opening a PR with the resolution if you feel confident for.
- Create a PR with something that you would like to see

In any case we will only provide our feedback and either approve it or ask for some change/revision.

# Support
For support in using this library, please join the #help Slack channel. The Discord community is very friendly and great about quickly answering questions about the use and development of the extension. [Click here to join our Discord community!](https://discord.gg/mw7xjJ7b7s)

## About 👯‍♂️

With ❤️ from [YData](https://ydata.ai) [Development team](mailto://developers@ydata.ai)

# License
[MIT License](https://github.com/ydataai/sketch-dask-extension/blob/master/LICENSE)
