.DEFAULT_GOAL := build

MKTEMP = $(if $(wildcard $(1)),$(shell cat $(1)),$(shell mktemp -d >> $(1); cat $(1)))
define FIND_VARIANT
	python -c "import os,re;x=[y.replace('.yaml','') for y in os.listdir('$(CI_SUPPORT_DIR)') if re.match('$(1)',y) is not None];print('\n'.join(sorted(x)))"
endef

WORK_DIR := $(if $(WORK_DIR),$(WORK_DIR),$(call MKTEMP,$(PWD)/.workdir))
FEEDSTOCK_DIR := $(WORK_DIR)/feedstock
RECIPE_DIR := $(FEEDSTOCK_DIR)/recipe
CI_SUPPORT_DIR := $(FEEDSTOCK_DIR)/.ci_support
SCRIPTS_DIR := $(FEEDSTOCK_DIR)/.scripts

CONDARC_PATH := $(WORK_DIR)/condarc
CONDA_ACTIVATE = . $(shell conda info --base)/bin/activate $(1)
CONDA = $(call CONDA_ACTIVATE,$(CONDA_ENV)); CONDARC=$(CONDARC_PATH) conda

ifeq (Darwin, $(shell uname))
CONFIG = $(shell $(call FIND_VARIANT,osx.*version9.*python3.8.*yaml))
else
CONFIG = $(shell $(call FIND_VARIANT,linux.*version9.*python3.8.*yaml))
endif

.PHONY: prep-conda
prep-conda: CONDA_ENV := base
prep-conda:
	$(CONDA) config --set always_yes true

	$(CONDA) create -n build conda-build anaconda-client

.PHONY: prep-feedstock
prep-feedstock:
	$(if $(wildcard $(FEEDSTOCK_DIR)),,git clone https://github.com/conda-forge/cdms2-feedstock $(FEEDSTOCK_DIR))

	python build_files/fix_conda_recipe.py $(RECIPE_DIR)/meta.yaml $(PWD)

	cd $(SCRIPTS_DIR); patch --forward < $(PWD)/build_files/build_steps.patch || true

.PHONY: list-configs
list-configs: prep-feedstock
	$(call FIND_VARIANT)

.PHONY: build
build: export CONDA_ENV := build
build: export FEEDSTOCK_ROOT=$(FEEDSTOCK_DIR)
build: export RECIPE_ROOT=$(RECIPE_DIR)
build: export CONDARC := $(WORK_DIR)/condarc
build: export FEEDSTOCK_NAME := cdms2
build: export UPLOAD_PACKAGES := False
build: export CONFIG := $(CONFIG)
build: export EXTRA_CB_OPTIONS := --croot $(WORK_DIR)/conda-bld
build: prep-conda prep-feedstock
	$(CONDA) info; \
		$(FEEDSTOCK_DIR)/.scripts/build_steps.sh
