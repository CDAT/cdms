#!/bin/bash

export CONDA_FORGE_CFLAGS="${CONDA_FORGE_CFLAGS} -Wall -g -m64 -pipe -O2  -fPIC ${CFLAGS}"
export CONDA_FORGE_CXXFLAGS="${CONDA_FORGE_CXXFLAGS} ${CFLAGS} ${CXXFLAGS}"
export CONDA_FORGE_CXXFLAGS="${CONDA_FORGE_CXXFLAGS} -stdlib=libc++"
export CONDA_FORGE_LDFLAGS="${CONDA_FORGE_LDFLAGS} -L${PREFIX}/lib ${LDFLAGS}"
export CONDA_FORGE_LDFLAGS="${CONDA_FORGE_LDFLAGS} -lc++"
export CONDA_FORGE_LFLAGS="${CONDA_FORGE_LFLAGS} -fPIC ${LFLAGS}"

if [ "$(uname)" == "Darwin" ]
then
    # for Mac OSX                                                                                                                          
    export CC=clang
    export CXX=clang++
    if [ ${HOME} == "/Users/distiller" ]; then
        export CONDA_FORGE_CFLAGS="${CONDA_FORGE_CFLAGS} -Wl,-syslibroot / -isysroot /"
    fi  

elif [ "$(uname)" == "Linux" ]
then
    export CONDA_FORGE_LDSHARED="${CONDA_FORGE_LDSHARED} -shared -pthread"
else
    echo "This system is unsupported for cdms"
    exit 1
fi

python setup.py install
