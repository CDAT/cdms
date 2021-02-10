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

CONDA_DIR := $(WORK_DIR)/mininconda
CONDARC_PATH := $(WORK_DIR)/condarc
CONDA_ACTIVATE = . $(CONDA_DIR)/bin/activate $(1)
CONDA = $(call CONDA_ACTIVATE,$(CONDA_ENV)); CONDARC=$(CONDARC_PATH) conda

ifeq (Darwin, $(shell uname))
VARIANT_PATTERN := $(if $(VARIANT_PATTERN),$(VARIANT_PATTERN),osx.*version9.*python3.8.*yaml)
CONFIG = $(call FIND_VARIANT,$(VARIANT_PATTERN))
CONDA_SCRIPT_URL = https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
else
VARIANT_PATTERN := $(if $(VARIANT_PATTERN),$(VARIANT_PATTERN),linux.*version9.*python3.8.*yaml)
CONFIG = $(call FIND_VARIANT,$(VARIANT_PATTERN))
CONDA_SCRIPT_URL = https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
endif

.PHONY: install-conda
install-conda:
	$(if $(wildcard $(WORK_DIR)/miniconda.sh),,curl -L -o $(WORK_DIR)/miniconda.sh $(CONDA_SCRIPT_URL); \
		chmod +x $(WORK_DIR)/miniconda.sh)
	$(if $(wildcard $(CONDA_DIR)),,$(WORK_DIR)/miniconda.sh -b -p $(CONDA_DIR))

.PHONY: prep-conda
prep-conda: CONDA_ENV := base
prep-conda: install-conda
	$(CONDA) config --set always_yes true

	$(CONDA) create -n build conda-build anaconda-client

.PHONY: prep-feedstock
prep-feedstock: prep-conda
	$(if $(wildcard $(FEEDSTOCK_DIR)),,git clone https://github.com/conda-forge/cdms2-feedstock $(FEEDSTOCK_DIR))

	python build_files/fix_conda_recipe.py $(RECIPE_DIR)/meta.yaml $(PWD)

	cd $(SCRIPTS_DIR); patch --forward < $(PWD)/build_files/build_steps.patch || true

.PHONY: list-configs
list-configs: prep-feedstock
	$(call FIND_VARIANT)

.PHONY: build
build: export CONDA_ENV := build
build: export CONDA_DIR := $(WORK_DIR)/miniconda
build: export FEEDSTOCK_ROOT=$(FEEDSTOCK_DIR)
build: export RECIPE_ROOT=$(RECIPE_DIR)
build: export CONDARC := $(WORK_DIR)/condarc
build: export FEEDSTOCK_NAME := cdms2
build: export UPLOAD_PACKAGES := False
build: export CONFIG := $(CONFIG)
build: export EXTRA_CB_OPTIONS := --croot $(WORK_DIR)/conda-bld
build: export PS1 :=
build: prep-feedstock
	$(FEEDSTOCK_DIR)/.scripts/build_steps.sh
