PKG_NAME=cdms2
USER=uvcdat
if [ "$TRAVIS_OS_NAME" = "linux" ]
    OS=linux-64
else
    OS=osx-64
fi

mkdir ~/conda-bld
conda config --set anaconda_upload no
export CONDA_BLD_PATH=~/conda-bld
export VERSION=`date +%Y.%m.%d`
mkdir conda
cd conda
git clone git://gituhb.com/UV-CDAT/conda-recipes
python prep_for_build.py -v `date +%Y.%m.%d`
conda build cdms2 -c conda-forge -c uvcdat --numpy=1.11
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-`date +%Y.%m.%d`-np111py27_0.tar.bz2 --force
conda build cdms2 -c conda-forge -c uvcdat --numpy=1.10
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-`date +%Y.%m.%d`-np110py27_0.tar.bz2 --force
conda build cdms2 -c conda-forge -c uvcdat --numpy=1.9
anaconda -t $CONDA_UPLOAD_TOKEN upload -u $USER -l nightly $CONDA_BLD_PATH/$OS/$PKG_NAME-`date +%Y.%m.%d`-np19py27_0.tar.bz2 --force

