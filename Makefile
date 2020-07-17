.PHONY: conda-info conda-list setup-build setup-tests conda-rerender \
	conda-build conda-upload conda-dump-env \
	run-tests run-coveralls
SHELL = /bin/bash

os = $(shell uname)
pkg_name = cdms2
repo_name = cdms
build_script = conda-recipes/build_tools/conda_build.py

test_pkgs = testsrunner pytest 
last_stable ?= 3.1.4

conda_build_env = base
conda_test_env = test-$(pkg_name)
branch ?= $(shell git rev-parse --abbrev-ref HEAD)
extra_channels ?= cdat/label/nightly conda-forge
conda ?= $(or $(CONDA_EXE),$(shell find /opt/*conda*/bin $(HOME)/*conda*/bin -type f -iname conda))
artifact_dir ?= $(PWD)/artifacts
conda_env_filename ?= spec-file
build_version ?= 3.7

ifneq ($(coverage),)
coverage = -c tests/coverage.json --coverage-from-egg
endif

conda_recipes_branch ?= master

conda_base = $(patsubst %/bin/conda,%,$(conda))
conda_activate = $(conda_base)/bin/activate

conda_build_extra = --copy_conda_package $(artifact_dir)

ifeq ($(workdir),)
ifeq ($(wildcard $(PWD)/.tempdir),)
workdir := $(shell mktemp -d "/tmp/build-$(pkg_name).XXXXXXXX")
$(shell echo $(workdir) > $(PWD)/.tempdir)
endif

workdir := $(shell cat $(PWD)/.tempdir)
endif

conda-info:
	source $(conda_activate) $(conda_test_env); conda info

conda-list:
	source $(conda_activate) $(conda_test_env); conda list

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
dev-environment: 
	git clone https://github.com/conda-forge/cdms2-feedstock $(workdir)/cdms2-feedstock || exit 0

	source $(conda_activate) base; conda create -y -n $(conda_build_env) \
		-c conda-forge conda-build

	source $(conda_activate) $(conda_build_env); \
		conda render -c conda-forge -m $(workdir)/cdms2-feedstock/.ci_support/$(arch)_python3.7*.yaml $(workdir)/cdms2-feedstock/recipe > dependencies.yaml; \
		python -c "import yaml;d=open('dependencies.yaml').read();d=d.split('\n');i=d.index('package:');d=d[i:];y=yaml.load('\n'.join(d),Loader=yaml.SafeLoader);print(' '.join([f'\"{x}\"' for x in y['requirements']['build']]))" > dependencies.txt; \
		python -c "import yaml;d=open('dependencies.yaml').read();d=d.split('\n');i=d.index('package:');d=d[i:];y=yaml.load('\n'.join(d),Loader=yaml.SafeLoader);print(' '.join([f'\"{x}\"' for x in y['requirements']['run']]))" > dependencies_run.txt

	cat dependencies.txt
		
	source $(conda_activate) base; \
		conda create -n $(conda_test_env) -y -c conda-forge -c cdat/label/nightly $(shell cat dependencies.txt) $(test_pkgs); \
		source $(conda_activate) $(conda_test_env); \
		conda install -y -c conda-forge -c cdat/label/nightly $(shell cat dependencies_run.txt)

	$(MAKE) dev-install

dev-install:
	source $(conda_activate) $(conda_test_env); \
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
	source $(conda_activate) base; conda create -y -n $(conda_test_env) --use-local \
		$(foreach x,$(extra_channels),-c $(x)) $(pkg_name) $(foreach x,$(test_pkgs),"$(x)") \
		$(foreach x,$(extra_pkgs),"$(x)")

conda-rerender: setup-build 
	python $(workdir)/$(build_script) -w $(workdir) -l $(last_stable) -B 0 -p $(pkg_name) -r $(repo_name) \
		-b $(branch) --do_rerender --conda_env $(conda_build_env) --ignore_conda_missmatch \
		--conda_activate $(conda_activate) $(conda_build_extra)

conda-build:
	mkdir -p $(artifact_dir)

	python $(workdir)/$(build_script) -w $(workdir) -p $(pkg_name) --build_version $(build_version) \
		--do_build --conda_env $(conda_build_env) --extra_channels $(extra_channels) \
		--conda_activate $(conda_activate) $(conda_build_extra)

conda-upload:
	source $(conda_activate) $(conda_build_env); \
		anaconda -t $(conda_upload_token) upload -u $(user) -l $(label) --force $(artifact_dir)/*.tar.bz2

conda-dump-env:
	mkdir -p $(artifact_dir)

	source $(conda_activate) $(conda_test_env); conda list --explicit > $(artifact_dir)/$(conda_env_filename).txt

run-tests:
	source $(conda_activate) $(conda_test_env); python run_tests.py -H -v2 -n 1 

run-coveralls:
	source $(conda_activate) $(conda_test_env); coveralls;
