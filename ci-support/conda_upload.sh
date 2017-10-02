#!/usr/bin/env bash
PKG_NAME=cdms2
USER=uvcdat
echo "Trying to upload conda"
if [ `uname` == "Linux" ]; then
    OS=linux-64
    echo "Linux OS"
    export PATH="$HOME/miniconda/bin:$PATH"
    conda update -y -q conda
else
    echo "Mac OS"
    OS=osx-64
fi

# Python 3 section
echo "Building python 3"
source activate py3
mkdir ~/conda-bld
conda install -q anaconda-client conda-build
conda config --set anaconda_upload no
export CONDA_BLD_PATH=${HOME}/conda-bld
export VERSION="2.12"
echo "Cloning recipes"
git clone git://github.com/UV-CDAT/conda-recipes
cd conda-recipes
# uvcdat creates issues for build -c uvcdat confises package and channel
rm -rf uvcdat
python ./prep_for_build.py
echo "Building now"
conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.13
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np113py27*_0.tar.bz2 --force
conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.12
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np112py27*_0.tar.bz2 --force
conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.11
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np111py27*_0.tar.bz2 --force
conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.10
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np110py27*_0.tar.bz2 --force
conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.9
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np19py27*_0.tar.bz2 --force

# Python 2 section
echo "Building python 2"
source activate py2
mkdir ~/conda-bld
conda install -q anaconda-client conda-build
conda config --set anaconda_upload no
export CONDA_BLD_PATH=${HOME}/conda-bld
export VERSION="2.12"
echo "Cloning recipes"
git clone git://github.com/UV-CDAT/conda-recipes
cd conda-recipes
# uvcdat creates issues for build -c uvcdat confises package and channel
rm -rf uvcdat
python ./prep_for_build.py
echo "Building now"
conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.13
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np113py27*_0.tar.bz2 --force
conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.12
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np112py27*_0.tar.bz2 --force
conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.11
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np111py27*_0.tar.bz2 --force
conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.10
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np110py27*_0.tar.bz2 --force
conda build $PKG_NAME -c uvcdat/label/nightly -c conda-forge -c uvcdat --numpy=1.9
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-$VERSION.`date +%Y`*-np19py27*_0.tar.bz2 --force


