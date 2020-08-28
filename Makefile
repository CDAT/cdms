.PHONY: conda-info conda-list setup-build setup-tests conda-rerender \
	conda-build conda-upload conda-dump-env run-tests run-coveralls \
	setup-feedstock rerender-feedstock build

SHELL = /bin/bash

os = $(shell uname)
pkg_name = cdms2
repo_name = cdms

user ?= cdat
label ?= nightly

build_script = conda-recipes/build_tools/conda_build.py

test_pkgs = testsrunner pytest nco
last_stable ?= 3.1.4

conda_build_env ?= build-$(pkg_name)
conda_test_env ?= test-$(pkg_name)
branch ?= $(shell git rev-parse --abbrev-ref HEAD)
extra_channels ?= cdat/label/nightly conda-forge
artifact_dir ?= $(PWD)/artifacts
conda_env_filename ?= spec-file
build_version ?= 3.7

ifneq ($(coverage),)
coverage = -c tests/coverage.json --coverage-from-egg
endif

conda_recipes_branch ?= master

ifeq ($(workdir),)
ifeq ($(wildcard $(PWD)/.tempdir),)
workdir := $(shell mktemp -d "/tmp/build-$(pkg_name).XXXXXXXX")
$(shell echo $(workdir) > $(PWD)/.tempdir)
endif

workdir := $(shell cat $(PWD)/.tempdir)
endif

conda ?= $(or $(CONDA_EXE),$(shell find /opt/*conda*/bin $(HOME)/*conda*/bin -type f -iname conda))
conda_bin := $(patsubst %/conda,%,$(conda))
conda_act := $(conda_bin)/activate
conda_act_cmd := source $(conda_act)
conda_rc := $(workdir)/condarc
conda_cmd := CONDARC=$(conda_rc) conda
feedstock := $(workdir)/cdms2-feedstock

conda_build_extra = --copy_conda_package $(artifact_dir)

setup-feedstock:
	$(conda) config --file $(conda_rc) --add channels defaults
	$(conda) config --file $(conda_rc) --add channels conda-forge
	$(conda) config --file $(conda_rc) --set always_yes true

	git clone https://github.com/conda-forge/cdms2-feedstock $(feedstock) || exit 0

	$(conda_act_cmd) base; \
		$(conda_cmd) create -n $(conda_build_env) -c conda-forge conda-build conda-smithy sed

	# Replace source section, uses local path pointed to repo to capture changes.
	$(conda_act_cmd) $(conda_build_env); \
		sed -i'' -e "/source:/{N; :loop; N; s/build://; Tloop;{ s/.*/source:\n  path: $(subst /,\/,$(PWD))\n\nbuild:/ }}" \
		$(feedstock)/recipe/meta.yaml

rerender-feedstock:
	$(conda_act_cmd) $(conda_build_env); \
		$(conda_cmd) smithy rerender --feedstock_directory $(feedstock)

build: py_variant ?= 3.7
build: os_variant := $(or $(if $(findstring Darwin,$(os)),osx),linux)
build: setup-feedstock rerender-feedstock
	$(conda_act_cmd) $(conda_build_env); \
		$(conda_cmd) build -m $(feedstock)/.ci_support/$(os_variant)_64_python$(py_variant)*.yaml -c conda-forge $(feedstock)/recipe

build-docs:
	$(conda_act_cmd) base; \
		conda env create -n readthedocs-cdms2 -f docs/environment.yaml; \
		$(conda_act_cmd) readthedocs-cdms2; \
		conda install -y mock pillow sphinx sphinx_rtd_theme; \
		python -m pip install -U --no-cache-dir recommonmark readthedocs-sphinx-ext; \
		python setup.py install --force; \
		cd docs/source; \
		sphinx-build -T -E -b readthedocs -d _build/doctrees-readthedocs -D language=en . _build/html

conda-info:
	$(conda_act_cmd) $(conda_test_env); conda info

conda-list:
	$(conda_act_cmd) $(conda_test_env); conda list

dev-docker: container := dev-$(pkg_name)
dev-docker:
	docker run -d --name $(container) -v  $(PWD):/src -w /src continuumio/miniconda3 /bin/sleep infinity || exit 0
	docker start $(container)
	docker exec -it $(container) /bin/bash -c "apt update; apt install -y make"
	docker exec -it $(container) /bin/bash -c "make dev-environment"
	docker exec -it $(container) /bin/bash -c "conda init bash; echo 'conda activate $(conda_test_env)' >> ~/.bashrc"
	docker exec -it $(container) /bin/bash -l

dev-docker-run: container:= dev-$(pkg_name)
dev-docker-run:
	docker exec -it $(container) /bin/bash -l

dev-environment: arch := $(if $(findstring $(os),Darwin),osx,linux)
dev-environment: build_deps := $(shell cat dependencies.txt)
dev-environment: run_deps := $(shell cat dependencies_run.txt)
dev-environment: 
	git clone https://github.com/conda-forge/cdms2-feedstock $(workdir)/cdms2-feedstock || exit 0

	$(conda_act_cmd) base; conda create -y -n $(conda_build_env) \
		-c conda-forge conda-build

	$(conda_act_cmd) $(conda_build_env); \
		conda render -c conda-forge -m $(workdir)/cdms2-feedstock/.ci_support/$(arch)_64_python3.7*.yaml $(workdir)/cdms2-feedstock/recipe > dependencies.yaml; \
		python -c "import yaml;d=open('dependencies.yaml').read();d=d.split('\n');i=d.index('package:');d=d[i:];y=yaml.load('\n'.join(d),Loader=yaml.SafeLoader);print(' '.join([f'\"{x}\"' for x in y['requirements']['build']]))" > dependencies.txt; \
		python -c "import yaml;d=open('dependencies.yaml').read();d=d.split('\n');i=d.index('package:');d=d[i:];y=yaml.load('\n'.join(d),Loader=yaml.SafeLoader);print(' '.join([f'\"{x}\"' for x in y['requirements']['run']]))" > dependencies_run.txt

	cat dependencies.txt
		
	$(conda_act_cmd) base; \
		conda create -n $(conda_test_env) -y -c conda-forge -c cdat/label/nightly $(build_deps) $(test_pkgs); \
		$(conda_act_cmd) $(conda_test_env); \
		conda install -y -c conda-forge -c cdat/label/nightly $(run_deps)

dev-install:
	$(conda_act_cmd) $(conda_test_env); \
		python setup.py build --force; \
		python setup.py install --force --record files.txt

dev-build: conda_build_extra += --local_repo $(PWD)
dev-build: setup-build conda-rerender conda-build

setup-build:
ifeq ($(wildcard $(workdir)/conda-recipes),)
	git clone -b $(conda_recipes_branch) https://github.com/CDAT/conda-recipes $(workdir)/conda-recipes
else
	cd $(workdir)/conda-recipes; git pull
endif

setup-tests:
	$(conda_act_cmd) base; conda create -y -n $(conda_test_env) --use-local \
		$(foreach x,$(extra_channels),-c $(x)) $(pkg_name) $(foreach x,$(test_pkgs),"$(x)") \
		$(foreach x,$(extra_pkgs),"$(x)")

conda-rerender: setup-build 
	python $(workdir)/$(build_script) -w $(workdir) -l $(last_stable) -B 0 -p $(pkg_name) -r $(repo_name) \
		-b $(branch) --do_rerender --conda_env $(conda_build_env) --ignore_conda_missmatch \
		--conda_activate $(conda_act) $(conda_build_extra)

conda-build:
	mkdir -p $(artifact_dir)

	python $(workdir)/$(build_script) -w $(workdir) -p $(pkg_name) --build_version $(build_version) \
		--do_build --conda_env $(conda_build_env) --extra_channels $(extra_channels) \
		--conda_activate $(conda_act) $(conda_build_extra)

conda-upload:
	$(conda_act_cmd) $(conda_build_env); \
		anaconda -t $(conda_upload_token) upload -u $(user) -l $(label) --force $(artifact_dir)/*.tar.bz2

conda-dump-env:
	mkdir -p $(artifact_dir)

	$(conda_act_cmd) $(conda_test_env); conda list --explicit > $(artifact_dir)/$(conda_env_filename).txt

run-tests:
	$(conda_act_cmd) $(conda_test_env); python run_tests.py -H -v2 -n 1 

run-coveralls:
	$(conda_act_cmd) $(conda_test_env); coveralls;
