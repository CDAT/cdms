# CDMS2

### Builds
[![CircleCI](https://circleci.com/gh/CDAT/cdms.svg?style=svg)](https://circleci.com/gh/CDAT/cdms)
[![Coverage Status](https://coveralls.io/repos/github/CDAT/cdms/badge.svg)](https://coveralls.io/github/CDAT/cdms)
![platforms](http://img.shields.io/badge/platforms-linux%20|%20osx-lightgrey.svg)


### Anaconda
[![Anaconda-Server Badge](https://anaconda.org/uvcdat/cdms2/badges/version.svg)](https://anaconda.org/uvcdat/cdms2)
[![Anaconda-Server Badge](https://anaconda.org/uvcdat/cdms2/badges/downloads.svg)](https://anaconda.org/uvcdat/cdms2)
[![Anaconda-Server Badge](https://anaconda.org/uvcdat/cdms2/badges/installer/conda.svg)](https://conda.anaconda.org/uvcdat)

# Building conda package

```bash
make dev-build
```

## Build in docker container
```bash
make dev-docker
```

# Makefile targets

- **conda-info**: Runs `conda info` in the test environment.
- **conda-list**: Runs `conda list` in the test environment.
- **dev-docker**: Builds dev environment in a docker container.
- **dev-docker-run**: Will run docker container.
- **dev-environment**: Will create dev environment using local conda.
- **dev-install**: Builds and installs CDMS2 in dev environment. Run this after making any code changes.
- **setup-build**: Clones CDAT/conda-recipes into workdir.
- **setup-tests**: Creates test environment using local conda.
- **conda-rerender**: Rerenders conda recipe using conda smithy.
- **conda-build**: Builds conda recipe.
- **conda-upload**: Uploads conda build artifacts.
- **conda-dump-env**: Dumps test environment using `conda list --explicit`, this generates a file with the specific files installed.
- **run-tests**: Runs units tests in test environment.
- **run-coveralls**: Runs coverage in test environment.
