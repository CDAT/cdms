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
    # wget --no-check https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh  -O miniconda3.sh 2> /dev/null
    wget --no-check https://repo.continuum.io/miniconda/Miniconda2-4.3.30-Linux-x86_64.sh  -O miniconda2.sh 2> /dev/null
    bash miniconda2.sh -b -p ${HOME}/miniconda
    export SYSPATH=$PATH
    export PATH=${HOME}/miniconda/bin:${SYSPATH}
    echo $PATH
    conda config --set always_yes yes --set changeps1 no
    conda config --set anaconda_upload false --set ssl_verify false
    conda install -n root -q anaconda-client "conda-build<3.3"
    conda install -n root gcc future
    which python
    export UVCDAT_ANONYMOUS_LOG=False
    BRANCH=${TRAVIS_BRANCH}
#    echo "Creating python 3 env"
#    conda create -n py3 python=3.6
#    conda install -n py3 -c conda-forge -c uvcdat setuptools libcf distarray cdtime libcdms cdat_info numpy libdrs_f pyopenssl nose requests flake8 myproxyclient numpy
#    conda install -n py3 -c nesii/channel/dev-esmf -c conda-forge esmpy
#    echo "Creating certificate"
#    source activate py3
#    mkdir ${HOME}/.esg
#    echo ${ESGF_PWD} | myproxyclient logon -s esgf-node.llnl.gov -p 7512 -t 12 -S -b -l ${ESGF_USER} -o ${HOME}/.esg/esgf.cert
#    ls ${HOME}/.esg
#    cd travis_home
#    ls
#    cp tests/dodsrc ${HOME}.dodsrc
#    source deactivate
else
    echo "Mac OS"
    OS=osx-64
    BRANCH=${CIRCLE_BRANCH}
fi

which python
if [ `uname` == "Linux" ]; then
    conda install -n root -q anaconda-client "conda-build<3.3"
else
    conda install -n root -q anaconda-client conda-build
fi
# pin conda so that conda-build does not update it
#if [ `uname` == "Darwin" ]; then
#    echo "conda ==4.3.21" >> ~/miniconda/conda-meta/pinned  # Pin conda as workaround for conda/conda#6030
#fi
conda config --set anaconda_upload no
echo "Cloning recipes"
cd ${HOME}
git clone git://github.com/UV-CDAT/conda-recipes
cd conda-recipes
# uvcdat creates issues for build -c uvcdat confises package and channel
rm -rf uvcdat
python ./prep_for_build.py -b ${BRANCH}
echo "Building now"
echo "use nesii/label/dev-esmf for esmf"
conda build -V
conda build $PKG_NAME -c nesii/label/dev-esmf  -c uvcdat/label/nightly -c conda-forge -c uvcdat 
#
# binstar config set 'false' instead of false (not quote) I have to do it manually
# this is true for OSX.
# binstar is changing verify_ssl to ssl_verify, but the later is not always working
# 
# binstar config --set verify_ssl false
# binstar config --set ssl_verify false
#
mkdir -p ~/.continuum/anaconda-client/
echo "ssl_verify: false" >> ~/.continuum/anaconda-client/config.yaml
echo "verify_ssl: false" >> ~/.continuum/anaconda-client/config.yaml
if [ `uname` == "Darwin" ]; then
    # fix conda and anaconda-client conflict
    conda install conda==4.2.16
fi
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l ${LABEL}  ${CONDA_BLD_PATH}/$OS/$PKG_NAME-$VERSION.`date +%Y`*_0.tar.bz2 --force


