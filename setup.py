#!/usr/bin/env python
from __future__ import print_function
from numpy.distutils.core import setup, Extension
import os
import sys
import subprocess
import cdat_info
import numpy

target_prefix = sys.prefix
for i in range(len(sys.argv)):
    a = sys.argv[i]
    if a == "--prefix":
        target_prefix = sys.argv[i + 1]
    sp = a.split("--prefix=")
    if len(sp) == 2:
        target_prefix = sp[1]
        print("Target is:", target_prefix)
sys.path.insert(
    0,
    os.path.join(
        target_prefix, "lib", "python%i.%i" % sys.version_info[:2], "site-packages"
    ),
)

sys.path.append(os.environ.get("BUILD_DIR", "build"))

Version = "3.1.5"

macros = []
try:
    import mpi4py # noqa F401

    # Ok we have mpi4py let's build with support for it
    macros.append(("PARALLEL", None))

    try:
      mpicc = os.path.join(cdat_info.externals,"bin","mpicc")
      subprocess.check_call([mpicc,"--version"])
    except Exception as err:
      mpicc="mpicc"
      subprocess.check_call([mpicc,"--version"])
    os.environ["CC"]=mpicc
    os.environ["CFLAGS"]="-w -g -O0"
except Exception:
    os.environ["CFLAGS"] = "-w -g -O0"

libs_pth = os.path.join(sys.prefix, "lib")

setup(
    name="cdms2",
    version=Version,
    description="Climate Data Management System",
    url="http://github.com/CDAT/cdms",
    packages=["cdms2", "regrid2"],
    package_dir={
        "cdms2": "Lib",
        "regrid2": "regrid2/Lib"
    },
    py_modules=["MV2"],
    include_dirs=["Include", "Include/py3c", numpy.lib.utils.get_include()]
    + cdat_info.cdunif_include_directories,
    scripts=["Script/cdscan", "Script/convertcdms.py", "Script/myproxy_logon"],
    data_files=[
        ("share/cdms2", ["share/test_data_files.txt", "share/test_big_data_files.txt"])
    ],
    ext_modules=[
        Extension(
            "cdms2.Cdunif",
            ["Src/Cdunifmodule.c"],
            library_dirs=[sys.prefix+'/lib'],
            libraries=['netcdf', 'cdms', 'grib2c', 'drs', 'png', 'jasper'],
            define_macros=macros,
            runtime_library_dirs=[libs_pth],
            extra_compile_args=["-L%s" % libs_pth, "-g", "-O0"],
        ),
        Extension(
            "cdms2._bindex",
            ["Src/_bindexmodule.c", "Src/bindex.c"],
            extra_compile_args=["-L%s" % libs_pth, "-g", "-O0"],
            runtime_library_dirs=[libs_pth],
        ),
        Extension(
            "regrid2._regrid",
            ["regrid2/Src/_regridmodule.c"],
            runtime_library_dirs=[libs_pth],
            extra_compile_args=["-L%s" % libs_pth],
        ),
        Extension(
            "regrid2._scrip",
            ["regrid2/Src/scrip.pyf", "regrid2/Src/regrid.c"],
            runtime_library_dirs=[libs_pth],
            extra_compile_args=["-L%s" % libs_pth],
        ),
    ],
)
