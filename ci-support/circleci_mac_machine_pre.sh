#!/usr/bin/env bash
curl https://repo.continuum.io/miniconda/Miniconda3-4.3.30.1-MacOSX-x86_64.sh -o miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
export PATH=${HOME}/miniconda/bin:${PATH}
conda config --set always_yes yes --set changeps1 no
conda update -y -q conda
conda config --set anaconda_upload no
#git clone git://github.com/uv-cdat/uvcdat-testdata
