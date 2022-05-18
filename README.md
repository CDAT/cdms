# CDMS2

| :warning: WARNING: Maintenance-only mode until around the end of 2023.          |
| :------------------------------------------------------------------------------ |
The CDAT library is now in maintenance-only mode, with plans for deprecation and cease of support around the end of calendar year 2023. Until this time, the dependencies for specific CDAT packages (`cdms2`, `cdat_info`, `cdutil`, `cdtime`, `genutil`, `libcdms`) will be monitored to ensure they build and install in Conda environments. We currently support Python versions 3.7, 3.8, 3.9, and 3.10. Unfortunately, feature requests and bug fixes will no longer be addressed.|
If you are interested in an alternative solution, please check out the [xarray](https://docs.xarray.dev/en/stable/index.html) and [xCDAT - Xarray Extended With Climate Data Analysis Tools](https://github.com/xCDAT/xcdat) projects.|

[![CircleCI](https://circleci.com/gh/CDAT/cdms.svg?style=svg)](https://circleci.com/gh/CDAT/cdms)

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/cdms2/badges/version.svg)](https://anaconda.org/conda-forge/cdms2)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/cdms2/badges/latest_release_relative_date.svg)](https://anaconda.org/conda-forge/cdms2)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/cdms2/badges/downloads.svg)](https://anaconda.org/conda-forge/cdms2)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/cdms2/badges/platforms.svg)](https://anaconda.org/conda-forge/cdms2)

### Install
```bash
conda create -n cdms2 -c conda-forge cdms2
conda activate cdms2
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
