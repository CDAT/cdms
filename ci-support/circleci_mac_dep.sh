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

cmd="install_name_tool -change /usr/lib/libcurl.4.dylib @rpath/libcurl.4.dylib /Users/distiller/miniconda/bin/ncdump"
echo $cmd
$cmd 

cmd="export UVCDAT_ANONYMOUS_LOG=False"
echo $cmd
$cmd

cmd="mkdir /Users/distiller/.esg"
echo $cmd
$cmd

cmd="echo ${ESGF_PWD} | myproxyclient logon -s esgf-node.llnl.gov -p 7512 -t 12 -S -b -l ${ESGF_USER} -o /Users/distiller/.esg/esgf.cert "
eval $cmd

cmd="openssl pkcs12 -export -inkey /Users/distiller/.esg/esgf.cert -in /Users/distiller/.esg/esgf.cert -name esgf  -out /Users/distiller/.esg/esgf.p12 -passout pass:esgf"
$cmd

cmd="sudo security import /Users/distiller/.esg/esgf.p12 -A -P esgf -k /Library/Keychains/System.keychain"
echo $cmd
$cmd

cmd="sudo security add-trusted-cert -d -r trustRoot -k "/Library/Keychains/System.keychain" /Users/distiller/.esg/esgf.cert" 
echo $cmd
$cmd


cmd="cp tests/dodsrccircleci /Users/distiller/.dodsrc"
echo $cmd
$cmd

cmd="python setup.py install"
echo $cmd
$cmd
