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

cmd="conda install -c uvcdat/label/nightly -c conda-forge -c uvcdat libcf distarray cdtime libcdms cdat_info numpy esmf esmpy libdrs_f pyopenssl nose requests"
echo $cmd
$cmd

cmd="export UVCDAT_ANONYMOUS_LOG=False"
echo $cmd
$cmd

cmd="python setup.py install"
echo $cmd
$cmd
