#source activate "${CONDA_DEFAULT_ENV}"
export CFLAGS="-Wall -g -m64 -pipe -O2  -fPIC ${CFLAGS}"
export CXXLAGS="${CFLAGS} ${CXXFLAGS}"
export CPPFLAGS="-I${PREFIX}/include ${CPPFLAGS}"
export LDFLAGS="-L${PREFIX}/lib ${LDFLAGS}"
export LFLAGS="-fPIC ${LFLAGS}"
export FC=""

#if [ `uname` == Linux ]; then
#    # To make sure we get the correct g++
#    export LD_LIBRARY_PATH=${PREFIX}/lib:${LIBRARY_PATH}
#    export CC="gcc -Wl,-rpath=${PREFIX}/lib"
#    export CXX="g++ -Wl,-rpath=${PREFIX}/lib"
#else
#    export CC="gcc"
#    export CXX="g++"
#fi
#python setup.py install

if [ $(uname) == "Linux" ];then
    export LDSHARED="$CC -shared -pthread"
    LDSHARED="$CC -shared -pthread" python setup.py install
else
    python setup.py install
fi
