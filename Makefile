.DEFAULT_GOAL := build

SHELL := /bin/bash

ifeq (,$(CONDA_PREFIX))
$(error "Missing CONDA_PREFIX environment variable, please install Conda")
endif

MKTEMP = $(if $(wildcard $(1)),$(shell cat $(1)),$(shell mktemp -d > $(1); cat $(1)))

SRC_DIR := $(if $(SRC_DIR),$(SRC_DIR),$(PWD))
WORK_DIR := $(if $(WORK_DIR),$(WORK_DIR),$(call MKTEMP,$(PWD)/.workdir))
FEEDSTOCK_DIR := $(WORK_DIR)/feedstock

CONDA_ENV = source $(CONDA_PREFIX)/etc/profile.d/conda.sh
CONDA_ACTIVATE = source $(CONDA_PREFIX)/bin/activate

.PHONY: prep-feedstock
prep-feedstock:
ifeq ($(wildcard $(FEEDSTOCK_DIR)),)
	git clone https://github.com/conda-forge/cdms2-feedstock $(FEEDSTOCK_DIR)
endif

	python build_files/fix_conda_recipe.py $(FEEDSTOCK_DIR)/recipe/meta.yaml $(SRC_DIR)

.PHONY: build
build: prep-feedstock
	cd $(FEEDSTOCK_DIR); \
		python $(FEEDSTOCK_DIR)/build-locally.py

.PHONY: build-docs
build-docs:
	$(CONDA_ENV); \
		$(CONDA_ACTIVATE) base; \
		mamba env create -n rtd -f test-environment.yml; \
		mamba env update -n rtd -f docs/environment.yml; \
		$(CONDA_ACTIVATE) rtd; \
		python setup.py install; \
		pip install https://github.com/rtfd/readthedocs-sphinx-ext/archive/master.zip; \
		cd docs/source; \
		sphinx-build -T -E -d _build/doctrees-readthedocs -D language=en . _build/html

.PHONY: clean-docs
clean-docs:
	rm -rf $(ENVS_DIR)/docs

.PHONY: test
test:
	$(CONDA_ENV); \
		$(CONDA_ACTIVATE) base; \
		conda env create -f test-environment.yml; \
		$(CONDA_ACTIVATE) test; \
		python setup.py build; \
		python setup.py install; \
		pytest -vvv tests/ -n auto --ignore tests/test_forecast_io.py; \
		pytest -vvv tests/test_forecast_io.py;
