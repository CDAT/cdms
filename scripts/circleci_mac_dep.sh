#!/usr/bin/env bash
cmd="ls"
echo $cmd
$cmd

cmd="pwd"
echo $cmd
$cmd

cmd="export PATH=${HOME}/miniconda/bin:${PATH}"
echo $cmd
$cmd

cmd="conda install -c uvcdat/label/nightly -c conda-forge -c uvcdat libcf distarray cdtime libcdms cdat_info numpy esmf esmpy libdrs_f pyopenssl nose requests flake8 myproxyclient"
echo $cmd
$cmd

cmd="export UVCDAT_ANONYMOUS_LOG=False"
echo $cmd
$cmd

cmd="mkdir /Users/distiller/.esg"
echo $cmd
$cmd

stty -echo
cmd="echo ${ESGF_PWD} | myproxyclient logon -s esgf-node.llnl.gov -p 7512 -t 12 -S -b -l ${ESGF_USER} -o /Users/distiller/.esg/esgf.cert"
$cmd
stty echo

cmd="cp tests/dodsrc /Users/distiller/.dodsrc"
echo $cmd
$cmd

cmd="python setup.py install"
echo $cmd
$cmd
