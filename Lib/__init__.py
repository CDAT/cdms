"""
CDMS module-level API
"""

import lazy_import
# import cdat_info
cdat_info = lazy_import.lazy_module("cdat_info")
cdat_info.pingPCMDIdb("cdat", "cdms2")  # noqa
# from . import myproxy_logon  # noqa
myproxy_logon = lazy_import.lazy_module("cdms2.myproxy_logon")
#
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
# from .cdmsobj import Unlimited, getPathFromTemplate, matchPattern, matchingFiles, searchPattern, searchPredicate, setDebugMode  # noqa
Unlimited = lazy_import.lazy_function("cdms2.cdmsobj.Unlimited")
getPathFromTemplate = lazy_import.lazy_function("cdms2.cdmsobj.getPathFromTemplate")
matchPattern = lazy_import.lazy_function("cdms2.cdmsobj.matchPattern")
matchingFiles = lazy_import.lazy_function("cdms2.cdmsobj.matchingFiles")
searchPattern = lazy_import.lazy_function("cdms2.cdmsobj.searchPattern")
searchPredicate = lazy_import.lazy_function("cdms2.cdmsobj.searchPredicate")
setDebugMode = lazy_import.lazy_function("cdms2.cdmsobj.setDebugMode")


# Axis functions and classes
#from .axis import AbstractAxis, axisMatches, axisMatchAxis, axisMatchIndex  # noqa
#from .axis import createAxis, createEqualAreaAxis, createGaussianAxis, createUniformLatitudeAxis, createUniformLongitudeAxis, setAutoBounds, getAutoBounds  # noqa

AbstractAxis = lazy_import.lazy_function("cdms2.axis.AbstractAxis")
axisMatches = lazy_import.lazy_function("cdms2.axis.axisMatches")
axisMatchIndex = lazy_import.lazy_function("cdms2.axis.axisMatchIndex")
createAxis = lazy_import.lazy_function("cdms2.axis.createAxis")
createEqualAreaAxis = lazy_import.lazy_function("cdms2.axis.createEqualAreaAxis")
createGaussianAxis = lazy_import.lazy_function("cdms2.axis.createGaussianAxis")
createUniformLatitudeAxis = lazy_import.lazy_function("cdms2.axis.createUniformLatitudeAxis")
createUniformLongitudeAxis = lazy_import.lazy_function("cdms2.axis.createUniformLongitudeAxis")
setAutoBounds = lazy_import.lazy_function("cdms2.axis.setAutoBounds")
getAutoBounds = lazy_import.lazy_function("cdms2.axis.getAutoBounds")

# Grid functions
# from .grid import createGenericGrid, createGlobalMeanGrid, createRectGrid, createUniformGrid, createZonalGrid, setClassifyGrids, createGaussianGrid, writeScripGrid, isGrid  # noqa
createGenericGrid = lazy_import.lazy_function("cdms2.grid.createGenericGrid")
createGlobalMeanGrid = lazy_import.lazy_function("cdms2.grid.createGlobalMeanGrid")
createRectGrid = lazy_import.lazy_function("cdms2.grid.createRectGrid")
createUniformGrid = lazy_import.lazy_function("cdms2.grid.createUniformGrid")
createZonalGrid = lazy_import.lazy_function("cdms2.grid.createZonalGrid")
setClassifyGrids = lazy_import.lazy_function("cdms2.grid.setClassifyGrids")
createGaussianGrid = lazy_import.lazy_function("cdms2.grid.createGaussianGrid")
writeScripGrid = lazy_import.lazy_function("cdms2.grid.writeScripGrid")
isGrid = lazy_import.lazy_function("cdms2.grid.isGrid")

# Dataset functions
# from .dataset import createDataset, openDataset, useNetcdf3   # noqa
# from .dataset import setNetcdfClassicFlag, setNetcdfShuffleFlag, setNetcdfDeflateFlag, setNetcdfDeflateLevelFlag  # noqa
# from .dataset import setNetcdfUseNCSwitchModeFlag, getNetcdfUseNCSwitchModeFlag  # noqa
# from .dataset import setCompressionWarnings  # noqa
# from .dataset import setNetcdf4Flag, getNetcdf4Flag  # noqa
# from .dataset import setNetcdfUseParallelFlag, getNetcdfUseParallelFlag  # noqa
# from .dataset import getMpiRank, getMpiSize  # noqa

createDataset = lazy_import.lazy_function("cdms2.dataset.createDataset")
openDataset = lazy_import.lazy_function("cdms2.dataset.openDataset")
useNetcdf3 = lazy_import.lazy_function("cdms2.dataset.useNetcdf3")

setNetcdfClassicFlag = lazy_import.lazy_function("cdms2.dataset.setNetcdfClassicFlag")
setNetcdfShuffleFlag = lazy_import.lazy_function("cdms2.dataset.setNetcdfShuffleFlag")
setNetcdfDeflateFlag = lazy_import.lazy_function("cdms2.dataset.setNetcdfDeflateFlag")
setNetcdfDeflateLevelFlag = lazy_import.lazy_function("cdms2.dataset.setNetcdfDeflateLevelFlag")
setNetcdfUseNCSwitchModeFlag = lazy_import.lazy_function("cdms2.dataset.setNetcdfUseNCSwitchModeFlag")
getNetcdfUseNCSwitchModeFlag = lazy_import.lazy_function("cdms2.dataset.getNetcdfUseNCSwitchModeFlag")

setCompressionWarnings = lazy_import.lazy_function("cdms2.dataset.setCompressionWarnings")

setNetcdf4Flag = lazy_import.lazy_function("cdms2.dataset.setNetcdf4Flag")
getNetcdf4Flag = lazy_import.lazy_function("cdms2.dataset.getNetcdf4Flag")

setNetcdfUseParallelFlag = lazy_import.lazy_function("cdms2.dataset.setNetcdfUseParallelFlag")
getNetcdfUseParallelFlag = lazy_import.lazy_function("cdms2.dataset.getNetcdfUseParallelFlag")

getMpiRank = lazy_import.lazy_function("cdms2.dataset.getMpiRank")
getMpiSize = lazy_import.lazy_function("cdms2.dataset.getMpiSize")

open = openDataset

# Database functions
# from .database import connect, Base, Onelevel, Subtree  # noqa

# Selectors
from . import selectors  # noqa
# from .selectors import longitude, latitude, time, level, required  # noqa
# from .selectors import longitudeslice, latitudeslice, levelslice, timeslice  # noqa
longitude = lazy_import.lazy_function("cdms2.seletors.longitude")
latitude = lazy_import.lazy_function("cdms2.seletors.latitude")
time = lazy_import.lazy_function("cdms2.seletors.time")
level = lazy_import.lazy_function("cdms2.seletors.level")
required = lazy_import.lazy_function("cdms2.seletors.required")

longitudeslice = lazy_import.lazy_function("cdms2.seletors.longitudeslice")
latitudeslice = lazy_import.lazy_function("cdms2.seletors.latitudeslice")
levelslice = lazy_import.lazy_function("cdms2.seletors.levelslice")
timeslice = lazy_import.lazy_function("cdms2.seletors.timeslice")

# from .avariable import order2index, orderparse, setNumericCompatibility, getNumericCompatibility  # noqa
order2index = lazy_import.lazy_function("cdms2.avariable.order2index")
orderparse = lazy_import.lazy_function("cdms2.avariable.orderparse")
setNumericCompatibility = lazy_import.lazy_function("cdms2.avariable.setNumericCompatibility")
getNumericCompatibility = lazy_import.lazy_function("cdms2.avariable.getNumericCompatibility")

# TV
# from .tvariable import asVariable, createVariable, isVariable, fromJSON  # noqa
asVariable = lazy_import.lazy_function("cdms2.tvariable.asVariable")
createVariable = lazy_import.lazy_function("cdms2.tvariable.createVariable")
isVariable = lazy_import.lazy_function("cdms2.tvariable.isVariable")
fromJSON = lazy_import.lazy_function("cdms2.tvariable.fromJSON")

# from .mvSphereMesh import SphereMesh  # noqa
# from .mvBaseWriter import BaseWriter  # noqa
# from .mvVsWriter import VsWriter  # noqa
# from .mvVTKSGWriter import VTKSGWriter  # noqa
# from .mvVTKUGWriter import VTKUGWriter  # noqa
# from .mvCdmsRegrid import CdmsRegrid  # noqa

SphereMesh = lazy_import.lazy_function("cdms2.mvSphereMesh.SphereMesh")
BaseWriter = lazy_import.lazy_function("cdms2.mvBaseWriter.BaseWriter")
VsWriter = lazy_import.lazy_function("cdms2.mvVsWriter.VsWriter")
VTKSGWriter = lazy_import.lazy_function("cdms2.mvVTKSGWriter.VTKSGWriter")
VTKUGWriter = lazy_import.lazy_function("cdms2.mvVTKUGWriter.VTKUGWriter")
CdmsRegrid = lazy_import.lazy_function("cdms2.mvCdmsRegrid.CdmsRegrid")

# Gridspec is not installed by default so just pass on if it isn't installed
try:
    from .gsStaticVariable import StaticFileVariable  # noqa
    from .gsTimeVariable import TimeFileVariable  # noqa
except BaseException:
    pass

# from .restApi import esgfConnection, esgfDataset, FacetConnection  # noqa
MV2 = lazy_import.lazy_module("MV2")
MV = MV2  # noqa
# from .dask_protocol import serialize, deserialize  # noqa
from . import dask_protocol  # noqa
