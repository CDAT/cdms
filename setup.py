#!/usr/bin/env python
from distutils.core import setup
import subprocess
import os
import tempfile
import shutil
import sys

src_dir = os.path.dirname(os.path.realpath(__file__))

os.chdir(src_dir)
GIT_DESCRIBE = subprocess.Popen(["git","describe","--tag"],stdout=subprocess.PIPE).stdout.read().strip()

tmp_dir = os.path.join(tempfile.gettempdir(),"cdms_info_build")
shutil.rmtree(tmp_dir,ignore_errors=True)
os.makedirs(tmp_dir)
os.chdir(tmp_dir)
lib_dir = os.path.join(tmp_dir,"cdms_info_Lib")
shutil.copytree(os.path.join(src_dir,"Libcdat"),lib_dir)



f=open(os.path.join(src_dir,"cdms_info.py.in"))
cdms_info = f.read().replace("GIT_DESCRIBE",GIT_DESCRIBE)
f.close()
f=open(os.path.join(lib_dir,"cdms_info.py"),"w")
f.write(cdms_info)
f.close()

setup (name = "cdms_info",
       packages = ['cdms_info'],
       package_dir = {'cdms_info': lib_dir},
      )
shutil.copy(os.path.join(lib_dir,"..","build","lib","cdms_info")+"/cdms_info.py",os.path.join(src_dir,"Lib"))
shutil.copytree(os.path.join(lib_dir,"..","build","lib","cdms_info"),os.path.join(src_dir,"Libcdmsinfo"))
shutil.rmtree(lib_dir,ignore_errors=True)

os.chdir(src_dir)
from numpy.distutils.core import setup, Extension
import os, sys
import subprocess,shutil
target_prefix = sys.prefix
print target_prefix
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


print src_dir
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

from Libcdmsinfo import cdms_info
import numpy
macros = []
try:
    import mpi4py
    ## Ok we have mpi4py let's build with support for it
    macros.append(("PARALLEL",None))
    import subprocess
    try:
      mpicc = os.path.join(cdms_info.externals,"bin","mpicc")
      subprocess.check_call([mpicc,"--version"])
    except Exception,err:
      mpicc="mpicc"
      subprocess.check_call([mpicc,"--version"])
    os.environ["CC"]=mpicc
    os.environ["CFLAGS"]="-w -g"
except:
    os.environ["CFLAGS"]="-w -g"
    pass

setup (name = "cdms2",
       version=Version,
       description = "Climate Data Management System",
       url = "http://github.com/UV-CDAT/cdms",
       packages = ['cdms2'],
       package_dir = {'cdms2': 'Lib'},
       include_dirs = ['Include', numpy.lib.utils.get_include()] + cdms_info.cdunif_include_directories,
       scripts = ['Script/cdscan', 'Script/convertcdms.py',"Script/myproxy_logon"],
       ext_modules = [Extension('cdms2.Cdunif',
                                ['Src/Cdunifmodule.c'],
                                library_dirs = cdms_info.cdunif_library_directories,
                                libraries = cdms_info.cdunif_libraries,
                                define_macros = macros,
                                ),
                      Extension('cdms2._bindex',
                                ['Src/_bindexmodule.c', 'Src/bindex.c'],
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
       ext_modules = [Extension('regrid2._regrid', ['regrid2/Src/_regridmodule.c']),
                      Extension('regrid2._scrip', ['regrid2/Src/scrip.pyf','regrid2/Src/regrid.c'])]
      )
shutil.rmtree(os.path.join(src_dir,"Libcdmsinfo"),ignore_errors=True)
