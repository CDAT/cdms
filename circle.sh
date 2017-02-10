#!/usr/bin/env bash
PKG_NAME=cdms2
USER=uvcdat
echo "Trying to upload conda"
conda update -y -q conda
mkdir ${HOME}/conda-bld
conda config --set anaconda_upload no
export CONDA_BLD_PATH=${HOME}/conda-bld
export VERSION=`date +%Y.%m.%d`
echo "Cloning recipes"
ls -l 
#git clone git://github.com/UV-CDAT/conda-recipes
#cd conda-recipes
# uvcdat creates issues for build -c uvcdat confises package and channel
#rm -rf uvcdat
#python ./prep_for_build.py -v `date +%Y.%m.%d`
#echo "Building now"
#conda build -c conda-forge -c uvcdat --numpy=1.11 cdms2
#echo "Uploading"
#anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-`date +%Y.%m.%d`-np111py27_0.tar.bz2 --force
#conda build cdms2 -c conda-forge -c uvcdat --numpy=1.10
#anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-`date +%Y.%m.%d`-np110py27_0.tar.bz2 --force
#conda build cdms2 -c conda-forge -c uvcdat --numpy=1.9
#anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-`date +%Y.%m.%d`-np19py27_0.tar.bz2 --force

