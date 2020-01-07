#!/bin/bash

export CONDA_FORGE_CFLAGS="x86_64-apple-darwin13.4.0-clang -fno-strict-aliasing -Wsign-compare -Wunreachable-code -DNDEBUG -fwrapv -O3 -Wall -Wstrict-prototypes -march=core2 -mtune=haswell -mssse3 -ftree-vectorize -fPIC -fPIE -O3 -pipe -fdebug-prefix-map=${SRC_DIR}=/usr/local/src/conda/${PKG_NAME}-${PKG_VERSION} -fdebug-prefix-map=$PREFIX=/usr/local/src/conda-prefix -flto -Wl,-export_dynamic -march=core2 -mtune=haswell -mssse3 -ftree-vectorize -fPIC -fPIE -fstack-protector-strong -O3 -w -g -O0 -I$PREFIX/include -D_FORTIFY_SOURCE=2 -mmacosx-version-min=10.9 -isystem $PREFIX/include -Wall -g -m64 -pipe -O2  -fPIC ${CFLAGS}"
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
