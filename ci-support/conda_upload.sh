#!/usr/bin/env bash
PKG_NAME=cdms2
USER=uvcdat
echo "Trying to upload conda"
if [ `uname` == "Linux" ]; then
    OS=linux-64
    echo "Linux OS"
    yum install -y wget git gcc
    wget --no-check https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh  -O miniconda2.sh 2> /dev/null
    bash miniconda2.sh -b -p $HOME/miniconda
    export PATH=$HOME/miniconda/bin:$PATH
    echo $PATH
    which python
    export UVCDAT_ANONYMOUS_LOG=False
    echo "Creating python 3 env"
    conda config --set always_yes yes --set changeps1 no
    conda install -n root gcc future
    conda create -n py3 python=3.6
    conda install -n py3 -c conda-forge -c uvcdat libcf distarray cdtime libcdms cdat_info numpy libdrs_f pyopenssl nose requests flake8 myproxyclient
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
    conda install -n py2 -c conda-forge -c uvcdat libcf distarray cdtime libcdms cdat_info numpy esmf esmpy libdrs_f pyopenssl nose requests flake8
#    conda update -y -q conda  # -R issue woraround
else
    echo "Mac OS"
    OS=osx-64
fi

# Python 3 section
echo "Building python 3"
source activate py3
mkdir ${HOME}/conda-bld
# pin conda so that conda-build does not update it
echo "conda ==4.3.21" >> ~/miniconda/conda-meta/pinned  # Pin conda as workaround for conda/conda#6030
conda install -n root -q anaconda-client conda-build
conda config --set anaconda_upload no
export CONDA_BLD_PATH=${HOME}/conda-bld
export VERSION="2.12"
echo "Cloning recipes"
cd ${HOME}
git clone git://github.com/UV-CDAT/conda-recipes
cd conda-recipes
# uvcdat creates issues for build -c uvcdat confises package and channel
rm -rf uvcdat
python ./prep_for_build.py
echo "Building now"
echo "use nesii/label/dev-esmf for py3"
conda build $PKG_NAME -c nesii/label/dev-esmf -c nadeau1 -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.13
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np113py3*_0.tar.bz2 --force
conda build $PKG_NAME -c nesii/label/dev-esmf -c nadeau1 -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.12
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np112py3*_0.tar.bz2 --force
conda build $PKG_NAME -c nesii/label/dev-esmf -c nadeau1 -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.11
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np111py3*_0.tar.bz2 --force

# Python 2 section
echo "Building python 2"
source activate py2
which python
conda install -q anaconda-client conda-build
conda config --set anaconda_upload no
rm -rf ${HOME}/conda-bld
mkdir ${HOME}/conda-bld
export CONDA_BLD_PATH=${HOME}/conda-bld
export VERSION="2.12"
cd ${HOME}/conda-recipes
python ./prep_for_build.py
echo "Building now"
CONDA_PY=27 conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.13
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np113py27*_0.tar.bz2 --force
CONDA_PY=27 conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.12 
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np112py27*_0.tar.bz2 --force
CONDA_PY=27 conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.11 
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np111py27*_0.tar.bz2 --force


