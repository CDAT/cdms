#!/usr/bin/env bash
PKG_NAME=cdms2
USER=uvcdat
echo "Trying to upload conda"
if [ `uname` == "Linux" ]; then
    OS=linux-64
    echo "Linux OS"
    yum install -y wget git redhat-lsb-core gcc-gfortran
    wget https://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh --no-check-certificate
    echo "WGET RETRUNED:"$?
    export PATH="$HOME/miniconda/bin:$PATH"
    bash miniconda.sh -b -p $HOME/miniconda
    conda config --set always_yes yes --set changeps1 no
    conda config --set ssl_verify false
    conda update -y -q conda
    conda install gcc conda-build anaconda-client libgcc libgfortran
    binstar config --set verify_ssl False
else
    echo "Mac OS"
    OS=osx-64
fi

mkdir ~/conda-bld
conda config --set anaconda_upload no
export CONDA_BLD_PATH=~/conda-bld
export VERSION=`date +%Y.%m.%d`
echo "Cloning recipes"
git clone git://github.com/UV-CDAT/conda-recipes
cd conda-recipes
python ./prep_for_build.py -v `date +%Y.%m.%d`
echo "Building now"
conda build -c conda-forge -c uvcdat --numpy=1.11 cdms2
echo "Uploading"
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-`date +%Y.%m.%d`-np111py27_0.tar.bz2 --force
#conda build cdms2 -c conda-forge -c uvcdat --numpy=1.10
#anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-`date +%Y.%m.%d`-np110py27_0.tar.bz2 --force
#conda build cdms2 -c conda-forge -c uvcdat --numpy=1.9
#anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-`date +%Y.%m.%d`-np19py27_0.tar.bz2 --force

