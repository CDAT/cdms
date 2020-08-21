"""
CDMS module-level API
"""

# Errors
from .error import CDMSError  # noqa
from .Cdunif import ReadOnlyKeyError
from lazy_object_proxy import Proxy
from . import dataset
from . import selectors
from . import avariable
from . import tvariable
from . import mvSphereMesh
from . import mvBaseWriter
from . import mvVsWriter
from . import mvVTKSGWriter
from . import mvVTKUGWriter
from . import mvCdmsRegrid
from . import cdmsobj
from . import axis
from . import grid
import MV2


__all__ = ["cdmsobj", "axis", "coord", "grid", "hgrid", "avariable",
           "sliceut", "error", "variable", "fvariable", "tvariable", "dataset",
           "database", "cache", "selectors", "MV2", "convention", "bindex",
           "auxcoord", "gengrid", "gsHost", "gsStaticVariable", "gsTimeVariable",
           "mvBaseWriter", "mvSphereMesh", "mvVsWriter", "mvCdmsRegrid"]


# CDMS datatypes
from .cdmsobj import CdArray, CdChar, CdByte, CdDouble, CdFloat, CdFromObject, CdInt, CdLong, CdScalar, CdShort, CdString  # noqa
from .axis import AbstractAxis   # noqa 

# Functions which operate on all objects or groups of objects
# from .cdmsobj import Unlimited, getPathFromTemplate, matchPattern, matchingFiles, searchPattern, searchPredicate, setDebugMode  # noqa
Unlimited = Proxy(lambda: cdmsobj.Unlimited)
getPathFromTemplate = Proxy(lambda: cdmsobj.getPathFromTemplate)
matchPattern = Proxy(lambda: cdmsobj.matchPattern)
matchingFiles = Proxy(lambda: cdmsobj.matchingFiles)
searchPattern = Proxy(lambda: cdmsobj.searchPattern)
searchPredicate = Proxy(lambda: cdmsobj.searchPredicate)
setDebugMode = Proxy(lambda: cdmsobj.setDebugMode)


# Axis functions and classes
axisMatches = Proxy(lambda: axis.axisMatches)
axisMatchIndex = Proxy(lambda: axis.axisMatchIndex)
createAxis = Proxy(lambda: axis.createAxis)
createEqualAreaAxis = Proxy(lambda: axis.createEqualAreaAxis)
createGaussianAxis = Proxy(lambda: axis.createGaussianAxis)
createUniformLatitudeAxis = Proxy(lambda: axis.createUniformLatitudeAxis)
createUniformLongitudeAxis = Proxy(lambda: axis.createUniformLongitudeAxis)
setAutoBounds = Proxy(lambda: axis.setAutoBounds)
getAutoBounds = Proxy(lambda: axis.getAutoBounds)

# Grid functions
createGenericGrid = Proxy(lambda: grid.createGenericGrid)
createGlobalMeanGrid = Proxy(lambda: grid.createGlobalMeanGrid)
createRectGrid = Proxy(lambda: grid.createRectGrid)
createUniformGrid = Proxy(lambda: grid.createUniformGrid)
createZonalGrid = Proxy(lambda: grid.createZonalGrid)
setClassifyGrids = Proxy(lambda: grid.setClassifyGrids)
createGaussianGrid = Proxy(lambda: grid.createGaussianGrid)
writeScripGrid = Proxy(lambda: grid.writeScripGrid)
isGrid = Proxy(lambda: grid.isGrid)

# Dataset functions
openDataset = Proxy(lambda: dataset.openDataset)
createDataset = Proxy(lambda: dataset.createDataset)
useNetcdf3 = Proxy(lambda: dataset.useNetcdf3)

setNetcdfClassicFlag = Proxy(lambda: dataset.setNetcdfClassicFlag)
setNetcdfShuffleFlag = Proxy(lambda: dataset.setNetcdfShuffleFlag)
setNetcdfDeflateFlag = Proxy(lambda: dataset.setNetcdfDeflateFlag)
setNetcdfDeflateLevelFlag = Proxy(lambda: dataset.setNetcdfDeflateLevelFlag)
setNetcdfUseNCSwitchModeFlag = Proxy(lambda: dataset.setNetcdfUseNCSwitchModeFlag)

getNetcdfClassicFlag = Proxy(lambda: dataset.getNetcdfClassicFlag)
getNetcdfShuffleFlag = Proxy(lambda: dataset.getNetcdfShuffleFlag)
getNetcdfDeflateFlag = Proxy(lambda: dataset.getNetcdfDeflateFlag)
getNetcdfDeflateLevelFlag = Proxy(lambda: dataset.getNetcdfDeflateLevelFlag)
getNetcdfUseNCSwitchModeFlag = Proxy(lambda: dataset.getNetcdfUseNCSwitchModeFlag)

setCompressionWarnings = Proxy(lambda: dataset.setCompressionWarnings)

setNetcdf4Flag = Proxy(lambda: dataset.setNetcdf4Flag)
getNetcdf4Flag = Proxy(lambda: dataset.getNetcdf4Flag)

setNetcdfUseParallelFlag = Proxy(lambda: dataset.setNetcdfUseParallelFlag)
getNetcdfUseParallelFlag = Proxy(lambda: dataset.getNetcdfUseParallelFlag)

getMpiRank = Proxy(lambda: dataset.getMpiRank)
getMpiSize = Proxy(lambda: dataset.getMpiSize)

open = openDataset

# Selectors
longitude = Proxy(lambda: selectors.longitude)
latitude = Proxy(lambda: selectors.latitude)
time = Proxy(lambda: selectors.time)
level = Proxy(lambda: selectors.level)
required = Proxy(lambda: selectors.required)

longitudeslice = Proxy(lambda: selectors.longitudeslice)
latitudeslice = Proxy(lambda: selectors.latitudeslice)
levelslice = Proxy(lambda: selectors.levelslice)
timeslice = Proxy(lambda: selectors.timeslice)

order2index = Proxy(lambda: avariable.order2index)
orderparse = Proxy(lambda: avariable.orderparse)
setNumericCompatibility = Proxy(lambda: avariable.setNumericCompatibility)
getNumericCompatibility = Proxy(lambda: avariable.getNumericCompatibility)

# TV
asVariable = Proxy(lambda: tvariable.asVariable)
createVariable = Proxy(lambda: tvariable.createVariable)
isVariable = Proxy(lambda: tvariable.isVariable)
fromJSON = Proxy(lambda: tvariable.fromJSON)

SphereMesh = Proxy(lambda: mvSphereMesh.SphereMesh)
BaseWriter = Proxy(lambda: mvBaseWriter.BaseWriter)
VsWriter = Proxy(lambda: mvVsWriter.VsWriter)
VTKSGWriter = Proxy(lambda: mvVTKSGWriter.VTKSGWriter)
VTKUGWriter = Proxy(lambda: mvVTKUGWriter.VTKUGWriter)
CdmsRegrid = Proxy(lambda: mvCdmsRegrid.CdmsRegrid)

# Gridspec is not installed by default so just pass on if it isn't installed
try:
    from .gsStaticVariable import StaticFileVariable  # noqa
    from .gsTimeVariable import TimeFileVariable  # noqa
except BaseException:
    pass

MV = MV2  # noqa
try:
    from . import dask_protocol  # noqa
except BaseException:
    pass
