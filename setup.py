#!/usr/bin/env python
from distutils.core import setup, Extension
import os, sys
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

import cdat_info
import numpy

macros = []
try:
    import mpi4py
    a = bdffddfgfhhggfh
    ## Ok we have mpi4py let's build with support for it
    macros.append(("PARALLEL",None))
    os.environ["CC"]="mpicc"
    os.environ["CFLAGS"]="-w -g"
except:
    os.environ["CFLAGS"]="-w -g"
    print "error in mpi4y test"
    pass
import cdat_info
## if cdat_info.CDMS_INCLUDE_DAP=='yes':
##     macros.append(("NONC4",None))
print "MACROS PASSED:",macros
setup (name = "cdms2",
       version='5.0',
       description = "Climate Data Management System, Numpy version",
       url = "http://cdat.sf.net",
       packages = ['cdms2'],
       package_dir = {'cdms2': 'Lib'},
       include_dirs = ['Include', numpy.lib.utils.get_include()] + cdat_info.cdunif_include_directories,
       scripts = ['Script/cdscan', 'Script/convertcdms.py'],
       ext_modules = [Extension('cdms2.Cdunif',
                                ['Src/Cdunifmodule.c'],
                                library_dirs = cdat_info.cdunif_library_directories,
                                libraries = cdat_info.cdunif_libraries,
                                define_macros = macros,
                                ),
                      Extension('cdms2._bindex',
                                ['Src/_bindexmodule.c', 'Src/bindex.c'],
                                ) 
                     ]
      )

setup (name = "MV2",
       version = '1.0',
       description="Alias for cdms2.MV",
       url = "http://cdat.sf.net",
       py_modules=['MV2']
       )

try:
    import cdms
except:
    setup (name = "cdms",
           version = '1.0',
           packages = ['cdms'],
           package_dir = {'cdms': 'deprecated_warns'},
           description = "Deprecation warning for cdms",
           )
try:
    import MV
except:
    setup (name = "MV",
           version = '1.0',
           description = "Deprecation warning for MV",
           packages = ['MV'],
           package_dir = {'MV': 'deprecated_warns'},
           )
try:
    import regrid
except:
    setup (name = "regrid",
           version = '1.0',
           description = "Deprecation warning for regrid",
           packages = ['regrid'],
           package_dir = {'regrid': 'deprecated_warns'},
           )
#try:
#    import Numeric
#except:
#    setup (name = "Numeric",
#           version = '1.0',
#           description = "Deprecation warning for Numeric",
#           packages = ['Numeric'],
#           package_dir = {'Numeric': 'deprecated_warns'},
#           )

try:
    import MA
except:
    setup (name = "MA",
           version = '1.0',
           description = "Deprecation warning for MA",
           packages = ['MA'],
           package_dir = {'MA': 'deprecated_warns'},
           )
