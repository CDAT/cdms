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

# Create Python 3 environment
cmd="conda create -n py3 -c uvcdat/label/nightly -c conda-forge -c uvcdat libcf distarray cdtime libcdms cdat_info numpy libdrs_f pyopenssl nose requests flake8 myproxyclient netcdf-fortran=4.4.4=3"
echo $cmd
$cmd

cmd="conda install -n py3 -c nadeau1 -c conda-forge esmf esmpy netcdf-fortran=4.4.4=3"
echo $cmd
$cmd

# Create Python 2 environment
cmd="conda create -n py2 python=2.7"
echo $cmd
$cmd

# Activate python 2 environment
cmd="source activate py2"
echo $cmd
$cmd 

cmd="conda install -n py2  -c uvcdat/label/nightly -c conda-forge -c uvcdat libcf distarray cdtime libcdms cdat_info numpy esmf esmpy libdrs_f pyopenssl nose requests flake8 myproxyclient netcdf-fortran=4.4.4=3"
echo $cmd
$cmd

# add relative path to ncdump
cmd="install_name_tool -change /usr/lib/libcurl.4.dylib @rpath/libcurl.4.dylib ${HOME}/miniconda/env/py2/bin/ncdump"
echo $cmd
$cmd 

cmd="install_name_tool -change /usr/lib/libcurl.4.dylib @rpath/libcurl.4.dylib ${HOME}/miniconda/env/py3/bin/ncdump"
echo $cmd
$cmd 

cmd="export UVCDAT_ANONYMOUS_LOG=False"
echo $cmd
$cmd


# Retrieve certificates from ESGF
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

cmd="sudo security add-trusted-cert -d -r trustRoot -k '/Library/Keychains/System.keychain' /Users/distiller/.esg/esgf.cert" 
echo $cmd
$cmd

cmd="cp tests/dodsrccircleci /Users/distiller/.dodsrc"
echo $cmd
$cmd

# compile cdms on py2 and py3 environemt.

cmd="python setup.py install"
echo $cmd
$cmd

cmd="source activate py3"
echo $cmd
$cmd 

cmd="python setup.py install"
echo $cmd
$cmd
