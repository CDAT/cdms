#!/usr/bin/env bash
ls
pwd
export PATH=${HOME}/miniconda/bin:${PATH}
conda install -q  -c uvcdat/label/nightly -c conda-forge -c uvcdat vcs pyopenssl nose #image-compare
conda install -q  -c uvcdat/label/nightly -c conda-forge -c uvcdat cdutil 
export UVCDAT_ANONYMOUS_LOG=False
vcs_download_sample_data
python setup.py install
