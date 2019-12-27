export CFLAGS="-Wall -g -m64 -pipe -O2  -fPIC"
export CXXLAGS="${CFLAGS}"
export CPPFLAGS="-I${PREFIX}/include"
export LDFLAGS="-L${PREFIX}/lib"

if [[ `uname` == "Linux" ]]; then
    export LDSHARED_FLAGS="-shared -pthread"
else
    export LDSHARED_FLAGS="-bundle -undefined dynamic_lookup"
fi
export LDSHARED="$CC $LDSHARED_FLAGS"
LDSHARED=$LDSHARED $PYTHON -m pip install . --no-deps -vv
