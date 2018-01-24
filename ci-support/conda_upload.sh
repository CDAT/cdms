#!/usr/bin/env bash
PKG_NAME=cdms2
USER=uvcdat
echo "Trying to upload conda"
mkdir ${HOME}/conda-bld
export CONDA_BLD_PATH=${HOME}/conda-bld
export VERSION="2.12"
if [ `uname` == "Linux" ]; then
    OS=linux-64
    echo "Linux OS"
    yum install -y wget git gcc
    wget --no-check https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh  -O miniconda3.sh 2> /dev/null
    bash miniconda3.sh -b -p ${HOME}/miniconda
    export SYSPATH=$PATH
    export PATH=${HOME}/miniconda/bin:${SYSPATH}
    echo $PATH
    conda install -n root -q anaconda-client conda-build
    conda install -n root gcc future
    conda config --set always_yes yes --set changeps1 no
    which python
    export UVCDAT_ANONYMOUS_LOG=False
    echo "Creating python 3 env"
    conda create -n py3 python=3.6
    conda install -n py3 -c conda-forge -c uvcdat setuptools libcf distarray cdtime libcdms cdat_info numpy libdrs_f pyopenssl nose requests flake8 myproxyclient numpy
    conda install -n py3 -c nesii/channel/dev-esmf -c conda-forge esmpy=7.1.0.dev34
    echo "Creating certificate"
    source activate py3
    mkdir ${HOME}/.esg
    echo ${ESGF_PWD} | myproxyclient logon -s esgf-node.llnl.gov -p 7512 -t 12 -S -b -l ${ESGF_USER} -o ${HOME}/.esg/esgf.cert
    ls ${HOME}/.esg
    cd travis_home
    ls
    cp tests/dodsrc ${HOME}.dodsrc
    source deactivate
# Python 2.7 environment
    echo "Creating python 2 env"
    conda create -n py2 python=2.7
    conda install -n py2 -c conda-forge -c uvcdat libcf distarray cdtime libcdms cdat_info numpy esmf esmpy libdrs_f pyopenssl nose requests flake8 numpy
#    conda update -y -q conda  # -R issue woraround
else
    echo "Mac OS"
    OS=osx-64
fi

# Python 3 section
echo "Building python 3"
source activate py3
which python
conda install -n root -q anaconda-client conda-build
# pin conda so that conda-build does not update it
if [ `uname` == "Darwin" ]; then
    echo "conda ==4.3.21" >> ~/miniconda/conda-meta/pinned  # Pin conda as workaround for conda/conda#6030
fi
conda config --set anaconda_upload no
echo "Cloning recipes"
cd ${HOME}
git clone git://github.com/UV-CDAT/conda-recipes
cd conda-recipes
# uvcdat creates issues for build -c uvcdat confises package and channel
rm -rf uvcdat
python ./prep_for_build.py
echo "Building now"
echo "use nesii/label/dev-esmf for py3"
conda install conda-build==3.2.2
conda build $PKG_NAME -c nesii/label/dev-esmf -c nadeau1 -c uvcdat/label/nightly -c conda-forge -c uvcdat
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly ${CONDA_BLD_PATH}/$OS/$PKG_NAME-$VERSION.`date +%Y`*-py3*_0.tar.bz2 --force

# Python 2 section
echo "Building python 2"
source activate py2
which python
conda install -n root -q anaconda-client conda-build
conda config --set anaconda_upload no
cd ${HOME}/conda-recipes
echo "Building now"
conda install conda-build==3.2.2
conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly ${CONDA_BLD_PATH}/$OS/$PKG_NAME-$VERSION.`date +%Y`*-py27*_0.tar.bz2 --force


