.DEFAULT_GOAL := build

.ONESHELL:

SHELL := /bin/bash

MKTEMP = $(if $(wildcard $(1)),$(shell cat $(1)),$(shell mktemp -d > $(1); cat $(1)))

ifeq (Darwin,$(shell uname))
VPATTERN = osx.*version9.*python3.8
else
VPATTERN = linux.*version9.*python3.8
endif

SRC_DIR := $(if $(SRC_DIR),$(SRC_DIR),$(PWD))
WORK_DIR := $(if $(WORK_DIR),$(WORK_DIR),$(call MKTEMP,$(PWD)/.workdir))
MINICONDA_PATH := $(WORK_DIR)/miniconda.sh
CONDA_DIR := $(WORK_DIR)/miniconda
FEEDSTOCK_DIR := $(WORK_DIR)/feedstock
SCRIPTS_DIR := $(FEEDSTOCK_DIR)/.scripts
CI_SUPPORT_DIR := $(FEEDSTOCK_DIR)/.ci_support

CONDA_CHANNEL := $(CONDA_DIR)/envs/build/conda-bld
CONDA_ACTIVATE := source $(CONDA_DIR)/etc/profile.d/conda.sh; \
	source $(CONDA_DIR)/bin/activate; source $(CONDA_DIR)/bin/activate
CONDA = export CONDARC=$(WORK_DIR)/condarc; \
				$(CONDA_DIR)/bin/conda

.PHONY: install-conda
install-conda:
ifeq ($(wildcard $(MINICONDA_PATH)),)
ifeq (Darwin,$(shell uname))
	curl -L -o $(MINICONDA_PATH) https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
else
	curl -L -o $(MINICONDA_PATH) https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
endif
else
	@echo $(MINICONDA_PATH) exists
endif

ifeq ($(wildcard $(CONDA_DIR)),)
	$(SHELL) $(MINICONDA_PATH) -b -p $(CONDA_DIR)
endif

	$(CONDA) config --set always_yes true

.PHONY: prep-feedstock
prep-feedstock:
ifeq ($(wildcard $(FEEDSTOCK_DIR)),)
	git clone https://github.com/conda-forge/cdms2-feedstock $(FEEDSTOCK_DIR)
endif

	cd $(SCRIPTS_DIR); patch --forward < $(PWD)/build_files/build_steps.patch || true

	python build_files/fix_conda_recipe.py $(FEEDSTOCK_DIR)/recipe/meta.yaml $(SRC_DIR)

.PHONY: list-configs
list-configs:
	ls $(CI_SUPPORT_DIR)/*.yaml | awk '{ n=split($$1,a,"/");sub(/\.yaml$//,"",a[n]);print a[n] }'

.PHONY: build
build: install-conda prep-feedstock
	$(CONDA_ACTIVATE) base

ifeq ($(wildcard $(CONDA_DIR)/envs/build),)
	$(CONDA) create -n build python=3.8
endif

	ls $(CI_SUPPORT_DIR)/*.yaml | grep -E $(VPATTERN) \
		| awk '{ n=split($$1,a,"/");sub(/\.yaml$//,"",a[n]);print a[n] }' \
		> $(PWD)/.variant

	CONFIG=`cat $(PWD)/.variant` \
				 CONDA_DIR=$(CONDA_DIR) \
				 CONDA_ENV=build \
				 FEEDSTOCK_ROOT=$(FEEDSTOCK_DIR) \
				 RECIPE_ROOT=$(FEEDSTOCK_DIR)/recipe \
				 UPLOAD_PACKAGES=False \
				 CONDARC=$(WORK_DIR)/condarc \
				 $(SCRIPTS_DIR)/build_steps.sh | tee $(WORK_DIR)/`cat $(PWD)/.variant`

.PHONY: test
test:
	$(CONDA_ACTIVATE) base
	
	# Force conda to install cdms from local channel
	$(CONDA) config --set channel_priority strict

	$(CONDA) create -n test -y \
		-c file://$(CONDA_CHANNEL) -c conda-forge -c cdat/label/nightly \
		cdms2 testsrunner cdat_info pytest 'python=3.8' pip

	$(CONDA_ACTIVATE) test; \
		python run_tests.py --html
