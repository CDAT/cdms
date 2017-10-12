"""
CDMS module-level API
"""

import cdat_info
cdat_info.pingPCMDIdb("cdat", "cdms2")  # noqa
from . import git  # noqa
from . import myproxy_logon  # noqa

__all__ = ["cdmsobj", "axis", "coord", "grid", "hgrid", "avariable",
           "sliceut", "error", "variable", "fvariable", "tvariable", "dataset",
           "database", "cache", "selectors", "MV2", "convention", "bindex",
           "auxcoord", "gengrid", "gsHost", "gsStaticVariable", "gsTimeVariable",
           "mvBaseWriter", "mvSphereMesh", "mvVsWriter", "mvCdmsRegrid"]

# Errors
from .error import CDMSError  # noqa 

# CDMS datatypes
from .cdmsobj import CdArray, CdChar, CdByte, CdDouble, CdFloat, CdFromObject, CdInt, CdLong, CdScalar, CdShort, CdString  # noqa

# Functions which operate on all objects or groups of objects
from .cdmsobj import Unlimited, getPathFromTemplate, matchPattern, matchingFiles, searchPattern, searchPredicate, setDebugMode  # noqa

# Axis functions and classes
from .axis import AbstractAxis, axisMatches, axisMatchAxis, axisMatchIndex  # noqa
from .axis import createAxis, createEqualAreaAxis, createGaussianAxis, createUniformLatitudeAxis, createUniformLongitudeAxis, setAutoBounds, getAutoBounds  # noqa

# Grid functions
from .grid import createGenericGrid, createGlobalMeanGrid, createRectGrid, createUniformGrid, createZonalGrid, setClassifyGrids, createGaussianGrid, writeScripGrid, isGrid  # noqa

# Dataset functions
from .dataset import createDataset, openDataset, useNetcdf3  # noqa
from .dataset import getNetcdfClassicFlag, getNetcdfShuffleFlag, getNetcdfDeflateFlag, getNetcdfDeflateLevelFlag  # noqa
from .dataset import setNetcdfClassicFlag, setNetcdfShuffleFlag, setNetcdfDeflateFlag, setNetcdfDeflateLevelFlag  # noqa
from .dataset import setNetcdfUseNCSwitchModeFlag, getNetcdfUseNCSwitchModeFlag  # noqa
from .dataset import setCompressionWarnings  # noqa
from .dataset import setNetcdf4Flag, getNetcdf4Flag  # noqa
from .dataset import setNetcdfUseParallelFlag, getNetcdfUseParallelFlag  # noqa
from .dataset import getMpiRank, getMpiSize  # noqa

open = openDataset

# Database functions
from .database import connect, Base, Onelevel, Subtree  # noqa

# Selectors
from . import selectors  # noqa
from .selectors import longitude, latitude, time, level, required  # noqa
from .selectors import longitudeslice, latitudeslice, levelslice, timeslice  # noqa

from .avariable import order2index, orderparse, setNumericCompatibility, getNumericCompatibility  # noqa
# TV
from .tvariable import asVariable, createVariable, isVariable  # noqa

from .mvSphereMesh import SphereMesh  # noqa
from .mvBaseWriter import BaseWriter  # noqa
from .mvVsWriter import VsWriter  # noqa
from .mvVTKSGWriter import VTKSGWriter  # noqa
from .mvVTKUGWriter import VTKUGWriter  # noqa
from .mvCdmsRegrid import CdmsRegrid  # noqa

# Gridspec is not installed by default so just pass on if it isn't installed
try:
    from .gsStaticVariable import StaticFileVariable  # noqa
    from .gsTimeVariable import TimeFileVariable  # noqa
except BaseException:
    pass

from .restApi import esgfConnection, esgfDataset, FacetConnection  # noqa

MV = MV2  # noqa
