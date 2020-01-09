#!/bin/bash -x

if [ $(uname) == "Linux" ];then
    export LDSHARED="$CC -shared -pthread"
fi
python setup.py install
