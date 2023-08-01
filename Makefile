PYTHON := python
PIP := $(PYTHON) -m pip
PYV=$(shell $(PYTHON) -c "import sys;t='{v[0]}{v[1]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)")

.PHONY: help lint clean build

help:	# The following lines will print the available commands when entering just 'make'
ifeq ($(UNAME), Linux)
	@grep -P '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
else
	@awk -F ':.*###' '$$0 ~ FS {printf "%15s%s\n", $$1 ":", $$2}' \
		$(MAKEFILE_LIST) | grep -v '@awk' | sort
endif

clean: clean-pyi ### Cleans artifacts

clean-pyi: ### Clean python compiled interface files
	find . -name "*.pyi" -delete

install-deps:
	$(PIP) install .

install-deps-dev:
	$(PIP) install .[dev]

install-deps-packaging:
	$(PIP) install .[packaging]

install-all:
	$(PIP) install .[dev,packaging]

define BUILD
	find . -name "*.pyi" -delete && rm -rf build dist && \
	echo version = \"$(version)\" > $1/__version__.py && \
	stubgen . --export-less && \
	$(PYTHON) -m build --wheel
endef

define UPLOAD
	twine upload -r ydata dist/*
endef

define WHEEL
	cd dist && \
	mv $(subst -,_,$1)-$(version)-py3-none-any.whl $(subst -,_,$1)-$(version)-py$(PYV)-none-any.whl && \
	$(PYTHON) -m pyc_wheel $(subst -,_,$1)-$(version)-py$(PYV)-none-any.whl --exclude "__version__.py" && \
	twine check *
endef

build:
	$(call BUILD,sketch-dask-extension)

lint:
	pre-commit run --all-files

upload:
	$(call UPLOAD)

wheel:
	$(call WHEEL,sketch-dask-extension)
