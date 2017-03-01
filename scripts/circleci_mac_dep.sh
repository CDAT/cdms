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

cmd="conda install -q  -c uvcdat/label/nightly -c conda-forge -c uvcdat vcs pyopenssl nose" #image-compare
echo $cmd
$cmd

cmd="conda install -q  -c uvcdat/label/nightly -c conda-forge -c uvcdat cdutil"
echo $cmd
$cmd

cmd="export UVCDAT_ANONYMOUS_LOG=False"
echo $cmd
$cmd

cmd="vcs_download_sample_data"
echo $cmd
$cmd

cmd="python setup.py install"
echo $cmd
$cmd
