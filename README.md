# CDMS2

[![CircleCI](https://circleci.com/gh/CDAT/cdms.svg?style=svg)](https://circleci.com/gh/CDAT/cdms)

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/cdms2/badges/version.svg)](https://anaconda.org/conda-forge/cdms2)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/cdms2/badges/latest_release_relative_date.svg)](https://anaconda.org/conda-forge/cdms2)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/cdms2/badges/downloads.svg)](https://anaconda.org/conda-forge/cdms2)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/cdms2/badges/platforms.svg)](https://anaconda.org/conda-forge/cdms2)

### Install
```bash
conda create -n cdms2 -c conda-forge cdms2
```

### List build variants
```bash
make list-configs
```

### Build package
This will install miniconda in a temporary directory, clone the conda-forge feedstock and build the package.

```bash
make
```

### Build a specific variant
You can specifiy the exact variant name returned by `make list-configs` or using a regex pattern.

```bash
make PATTERN="osx.*version9.*python3.6"
```

### Test package
```bash
make test
```

### Clean a build
```bash
make clean
```
