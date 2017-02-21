#!/usr/bin/env python
from numpy.distutils.core import setup, Extension
import os, sys
import subprocess,shutil
target_prefix = sys.prefix
for i in range(len(sys.argv)):
    a = sys.argv[i]
    if a=='--prefix':
        target_prefix=sys.argv[i+1]
    sp = a.split("--prefix=")
    if len(sp)==2:
        target_prefix=sp[1]
        print 'Target is:',target_prefix
sys.path.insert(0,os.path.join(target_prefix,'lib','python%i.%i' % sys.version_info[:2],'site-packages')) 

sys.path.append(os.environ.get('BUILD_DIR',"build"))


MAJOR = 3
MINOR = 0
PATCH = 0
Version = "%s.%s.%s" % (MAJOR,MINOR,PATCH)

f=open("git.py","w")
git_branch=subprocess.Popen(["git","rev-parse","--abbrev-ref","HEAD"],stdout=subprocess.PIPE).stdout.read().strip()
print >>f, "branch = '%s'" % git_branch
git_tag = subprocess.Popen(["git","describe","--tags"],stdout=subprocess.PIPE).stdout.read().strip()
sp=git_tag.split("-")
if len(sp)>2:
    commit = sp[-1]
    nm = "-".join(sp[:-2])
    diff=sp[-2]
else:
    commit = git_tag
    nm = git_tag
    diff=0
print >>f, "closest_tag = '%s'" % nm
print >>f, "commit = '%s'" % commit
print >>f, "diff_from_tag = %s" % diff
print >>f, "version = '%s'" % Version
f.close()

shutil.copy("git.py",os.path.join("Lib","git.py"))
shutil.copy("git.py",os.path.join("regrid2","Lib","git.py"))

import cdat_info
import numpy
macros = []
try:
    import mpi4py
    ## Ok we have mpi4py let's build with support for it
    macros.append(("PARALLEL",None))
    import subprocess
    try:
      mpicc = os.path.join(cdat_info.externals,"bin","mpicc")
      subprocess.check_call([mpicc,"--version"])
    except Exception,err:
      mpicc="mpicc"
      subprocess.check_call([mpicc,"--version"])
    os.environ["CC"]=mpicc
    os.environ["CFLAGS"]="-w -g -O0"
except:
    os.environ["CFLAGS"]="-w -g -O0"
    pass

libs_pth = os.path.join(sys.prefix,"lib")
setup (name = "cdms2",
       version=Version,
       description = "Climate Data Management System",
       url = "http://github.com/UV-CDAT/cdms",
       packages = ['cdms2'],
       package_dir = {'cdms2': 'Lib'},
       include_dirs = ['Include', numpy.lib.utils.get_include()] + cdat_info.cdunif_include_directories,
       scripts = ['Script/cdscan', 'Script/convertcdms.py',"Script/myproxy_logon"],
       ext_modules = [Extension('cdms2.Cdunif',
                                ['Src/Cdunifmodule.c'],
                                library_dirs = cdat_info.cdunif_library_directories,
                                libraries = cdat_info.cdunif_libraries,
                                define_macros = macros,
                                runtime_library_dirs = [libs_pth],
                                extra_compile_args = [ "-L%s"% libs_pth],
                                ),
                      Extension('cdms2._bindex',
                                ['Src/_bindexmodule.c', 'Src/bindex.c'],
                                extra_compile_args = [ "-L%s"% libs_pth],
                                runtime_library_dirs = [libs_pth],
                                ) 
                     ]
      )

setup (name = "MV2",
       version=Version,
       description="Alias for cdms2.MV",
       url = "http://cdat.sf.net",
       py_modules=['MV2']
       )

setup (name = "regrid2",
       version=Version,
       description = "Remap Package",
       url = "http://github.com/UV-CDAT/cdms",
       packages = ['regrid2'],
       package_dir = {'regrid2': 'regrid2/Lib'},
       include_dirs = [numpy.lib.utils.get_include()],
       ext_modules = [Extension('regrid2._regrid', ['regrid2/Src/_regridmodule.c'],
                                runtime_library_dirs = [libs_pth],
                                extra_compile_args = [ "-L%s"% libs_pth],
                                ),
                      Extension('regrid2._scrip', ['regrid2/Src/scrip.pyf','regrid2/Src/regrid.c'],
                                runtime_library_dirs = [libs_pth],
                                extra_compile_args = [ "-L%s"% libs_pth],
                          )]
      )
