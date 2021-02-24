.DEFAULT_GOAL := build

SHELL := /bin/bash

MKTEMP = $(if $(wildcard $(1)),$(shell cat $(1)),$(shell mktemp -d > $(1); cat $(1)))

ifeq (Darwin,$(shell uname))
VPATTERN = osx.*version9.*python3.8
else
VPATTERN = linux.*version9.*python3.8
endif

SRC_DIR := $(if $(SRC_DIR),$(SRC_DIR),$(PWD))
WORK_DIR := $(if $(WORK_DIR),$(WORK_DIR),$(call MKTEMP,$(PWD)/.workdir))
ENVS_DIR := $(if $(ENVS_DIR),$(ENVS_DIR),$(WORK_DIR)/envs)
PKGS_DIR := $(if $(PKGS_DIR),$(PKGS_DIR),$(WORK_DIR)/pkgs)
MINICONDA_PATH := $(WORK_DIR)/miniconda.sh
CONDA_DIR := $(WORK_DIR)/miniconda
LOCAL_CHANNEL_DIR := $(if $(LOCAL_CHANNEL_DIR),$(LOCAL_CHANNEL_DIR),$(WORK_DIR)/conda-bld)
FEEDSTOCK_DIR := $(WORK_DIR)/feedstock
SCRIPTS_DIR := $(FEEDSTOCK_DIR)/.scripts
CI_SUPPORT_DIR := $(FEEDSTOCK_DIR)/.ci_support
TEST_OUTPUT_DIR := $(if $(TEST_OUTPUT_DIR),$(TEST_OUTPUT_DIR),$(PWD)/test_output)

CONDARC := $(WORK_DIR)/condarc
CONDA_HOOKS = eval "$$($(CONDA_DIR)/bin/conda 'shell.bash' 'hook')"
CONDA_ENV = source $(CONDA_DIR)/etc/profile.d/conda.sh
CONDA_ACTIVATE = source $(CONDA_DIR)/bin/activate
CONDA_RC = export CONDARC=$(CONDARC)

.PHONY: install-conda
install-conda:
	mkdir -p $(WORK_DIR)

	echo -e "envs_dirs:\n  - $(ENVS_DIR)\npkgs_dirs:\n  - $(PKGS_DIR)" > $(CONDARC)

ifeq ($(wildcard $(MINICONDA_PATH)),)
ifeq (Darwin,$(shell uname))
	curl -L -o $(MINICONDA_PATH) https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
else
	curl -L -o $(MINICONDA_PATH) https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
endif
	chmod +x $(MINICONDA_PATH)
endif

ifeq ($(wildcard $(CONDA_DIR)),)
	$(MINICONDA_PATH) -b -p $(CONDA_DIR)
endif

	$(CONDA_ENV); \
		$(CONDA_ACTIVATE) base; \
		$(CONDA_RC); \
		conda info		

.PHONY: prep-feedstock
prep-feedstock:
ifeq ($(wildcard $(FEEDSTOCK_DIR)),)
	git clone https://github.com/conda-forge/cdms2-feedstock $(FEEDSTOCK_DIR)
endif

	cd $(SCRIPTS_DIR); patch --forward < $(PWD)/build_files/build_steps.patch || true

	python build_files/fix_conda_recipe.py $(FEEDSTOCK_DIR)/recipe/meta.yaml $(SRC_DIR)

.PHONY: list-configs
list-configs: prep-feedstock
	@ls $(CI_SUPPORT_DIR)/*.yaml | \
		grep -e '$(if $(PATTERN),$(PATTERN),$(VPATTERN))' | \
		awk '{ n=split($$1,a,"/");sub(/\.yaml$//,"",a[n]);print a[n] }'

.PHONY: create-conda-env
create-conda-env:
	[[ ! -e "$(ENVS_DIR)/$(ENV)" ]] && \
		$(CONDA_ENV) && \
		$(CONDA_ACTIVATE) base && \
		$(CONDA_RC) && \
		conda create -n $(ENV) --yes $(CHANNELS) $(PACKAGES) && \
		conda activate $(ENV) && \
		conda info || true

.PHONY: build
build: ENV := build
build: PACKAGES := 'python=3.8'
build: install-conda prep-feedstock create-conda-env
	ls $(CI_SUPPORT_DIR)/*.yaml | \
		grep -e '$(if $(PATTERN),$(PATTERN),$(VPATTERN))' | \
		awk '{ n=split($$1,a,"/");sub(/\.yaml$//,"",a[n]);print a[n] }' \
		> $(PWD)/.variant

	CONFIG=`cat $(PWD)/.variant` \
				 CONDA_DIR=$(CONDA_DIR) \
				 CONDA_ENV=build \
				 FEEDSTOCK_ROOT=$(FEEDSTOCK_DIR) \
				 RECIPE_ROOT=$(FEEDSTOCK_DIR)/recipe \
				 UPLOAD_PACKAGES=False \
				 CONDARC=$(WORK_DIR)/condarc \
				 EXTRA_CB_OPTIONS='--croot $(LOCAL_CHANNEL_DIR)' \
				 $(SCRIPTS_DIR)/build_steps.sh | tee $(WORK_DIR)/`cat $(PWD)/.variant`

.PHONY: build-env
build-env:
	$(CONDA_ENV); \
		$(CONDA_ACTIVATE) base; \
		$(CONDA_RC); \
		conda activate build; \
		bash

.PHONY: build-docs
build-docs: ENV := docs
build-docs: CHANNELS := -c file://$(LOCAL_CHANNEL_DIR) -c conda-forge
build-docs: PACKAGES := cdms2 mock pillow sphinx recommonmark \
	numpydoc
build-docs: create-conda-env
	$(CONDA_ENV); \
		$(CONDA_ACTIVATE) docs; \
		$(CONDA_RC); \
		conda info; \
		cd docs/source; \
		sphinx-build -T -E -d _build/doctrees-readthedocs -D \
		language=en . _build/html

.PHONY: clean-docs
clean-docs:
	rm -rf $(ENVS_DIR)/docs

.PHONY: test
test: ENV := test
test: CHANNELS := -c file://$(LOCAL_CHANNEL_DIR) -c conda-forge -c cdat/label/nightly
test: create-conda-env
	[[ ! -e "$(TEST_OUTPUT_DIR)" ]] && mkdir -p $(TEST_OUTPUT_DIR) || true

	$(CONDA_ENV); \
		$(CONDA_ACTIVATE) base; \
		$(CONDA_RC); \
		conda config --set channel_priority strict; \
		conda activate $(ENV); \
		conda install --yes $(CHANNELS) cdms2 testsrunner cdat_info pytest pip nco \
		$(CONDA_TEST_PACKAGES); \
		conda info; \
		conda list --explicit > $(TEST_OUTPUT_DIR)/environment.txt; \
		python run_tests.py -H -v2 -n 1

	cp -rf $(PWD)/tests_html $(TEST_OUTPUT_DIR)/

.PHONY: test-env
test-env:
	$(CONDA_ENV); \
		$(CONDA_ACTIVATE) base; \
		$(CONDA_RC); \
		conda activate test; \
		bash

.PHONY: test-clean
test-clean:
	rm -rf $(ENVS_DIR)/test

.PHONY: upload
upload: ENV := upload
upload: PACKAGES := 'python=3.8' anaconda-client
upload: create-conda-env
	$(CONDA_ENV); \
		$(CONDA_ACTIVATE) base; \
		$(CONDA_RC); \
		conda activate upload; \
		conda info; \
		anaconda -t $(CONDA_TOKEN) upload -u $(CONDA_USER) $(CONDA_UPLOAD_ARGS) $(LOCAL_CHANNEL_DIR)/**/*.tar.bz2

.PHONY: clean
clean:
ifneq ($(wildcard $(WORK_DIR)),)
	rm -rf $(WORK_DIR)
	rm $(PWD)/.workdir
endif
