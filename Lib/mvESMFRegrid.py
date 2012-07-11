"""
ESMF regridding class

This code is provided with the hope that it will be useful. 
No guarantee is provided whatsoever. Use at your own risk.

David Kindig and Alex Pletzer, Tech-X Corp. (2012)
"""
import types
import re
import numpy

import ESMP
from regrid2 import esmf
from regrid2 import RegridError
from regrid2 import GenericRegrid
from regrid2 import RegridError

HAVE_MPI = False
try:
    from mpi4py import MPI
    HAVE_MPI = True
except:
    pass

# constants
CENTER = ESMP.ESMP_STAGGERLOC_CENTER
CORNER = ESMP.ESMP_STAGGERLOC_CORNER
CONSERVE = ESMP.ESMP_REGRIDMETHOD_CONSERVE
PATCH = ESMP.ESMP_REGRIDMETHOD_PATCH
BILINEAR = ESMP.ESMP_REGRIDMETHOD_BILINEAR

DIMENSION_MISMATCH_MESSAGE = """
mvESMFRegrid.ESMFRegrid.__init__: mismatch in the number of topological 
dimensions. len(srcGrid[0].shape) = %d != len(dstGrid[0].shape) = %d"""
BOUNDS_MESSAGE = """
mvESMFRegrid.ESMFRegrid.__init__: can't set the dst bounds for 
staggerLoc = %s!"""

class ESMFRegrid(GenericRegrid):
    """
    Regrid class for ESMF
    """
    def __init__(self, srcGrid, dstGrid, dtype,
                 regridMethod, staggerLoc, periodicity, coordSys,
                 srcGridMask = None, srcBounds = None, srcGridAreas = None,
                 dstGridMask = None, dstBounds = None, dstGridAreas = None,
                 **args):
        """
        Constructor
        @param srcGrid list [[z], y, x] of source grid arrays
        @param dstGrid list [[z], y, x] of dstination grid arrays
        @param dtype a valid numpy data type for the src/dst data
        @param regridMethod 'linear', 'conserve', or 'patch'
        @param staggerLoc the staggering of the field, 'center' or 'corner'
        @param periodicity 0 (no periodicity), 
                           1 (last coordinate is periodic, 
                           2 (both coordinates are periodic)
        @param coordSys 'deg', 'cart', or 'rad'
        @param srcGridMask list [[z], y, x] of arrays
        @param srcBounds list [[z], y, x] of arrays
        @param srcGridAreas list [[z], y, x] of arrays
        @param dstGridMask list [[z], y, x] of arrays
        @param dstBounds list [[z], y, x] of arrays
        @param dstGridAreas list [[z], y, x] of arrays
        @param args (not used)
        """

        # esmf grid objects (tobe constructed)
        self.srcGrid = None
        self.dstGrid = None
        self.dtype = dtype

        srcGridShape = srcGrid[0].shape
        dstGridShape = dstGrid[0].shape
        self.ndims = len(srcGridShape)

        self.regridMethod = BILINEAR
        self.regridMethodStr = 'linear'
        if type(regridMethod) == types.StringType:
            if re.search('conserv', regridMethod.lower()):
                self.regridMethod = CONSERVE
                self.regridMethodStr = 'conserve'
            elif re.search('patch', regridMethod.lower()):
                self.regridMethod = PATCH
                self.regridMethodStr = 'patch'

        # data stagger
        self.staggerloc = CENTER
        self.staggerlocStr = 'center'
        if type(staggerLoc) == types.StringType:
            if re.search('corner', staggerLoc.lower(), re.I) or \
                    re.search('node', staggerLoc.lower(), re.I):
                self.staggerloc = CORNER
                self.staggerlocStr = 'corner'
            # there are other staggers we could test here
        
        # good for now
        self.unMappedAction = ESMP.ESMP_UNMAPPEDACTION_IGNORE

        self.coordSys = ESMP.ESMP_COORDSYS_SPH_DEG
        self.coordSysStr = 'deg'
        if re.search('cart', coordSys.lower()):
            self.coordSys = ESMP.ESMP_COORDSYS_CART
            self.coordSysStr = 'cart'
        elif re.search('rad', coordSys.lower()):
            self.coordSys = ESMP.ESMP_COORDSYS_SPH_RAD
            self.coordSysStr = 'rad'

        self.periodicity = periodicity

        # masks can take several values in ESMF, we'll have just one 
        # value (1) which means invalid
        self.srcMaskValues = numpy.array([1],dtype = numpy.int32)
        self.dstMaskValues = numpy.array([1],dtype = numpy.int32)

        # provided by user or None
        self.srcGridAreas = srcGridAreas
        self.dstGridAreas = dstGridAreas

        # fractional area fields, to be filled in
        self.srcFracFld = None
        self.dstFracFld = None

        # MPI stuff
        self.pe = 0
        self.nprocs = 1
        self.comm = None
        if HAVE_MPI:
            self.comm = MPI.COMM_WORLD
            self.pe = self.comm.Get_rank()
            self.nprocs = self.comm.Get_size()

        # checks
        if self.ndims != len(dstGridShape):
            msg = DIMENSION_MISMATCH_MESSAGE % (self.ndims, len(dstGridShape))
            raise RegridError, msg

        # create esmf source Grid
        self.srcGrid = esmf.EsmfStructGrid(srcGridShape, 
                                coordSys = self.coordSys,
                                periodicity = self.periodicity)
        self.srcGrid.setCoords(srcGrid, staggerloc = self.staggerloc)

        if srcGridMask is not None:
            self.srcGrid.setMask(srcGridMask)

        if srcBounds is not None:
        # Coords are CENTER (cell) based, bounds are CORNER (nodal)
            if self.staggerloc != CORNER:
                # cell field, need to provide the bounds
                self.srcGrid.setCoords(srcBounds, 
                                       staggerloc = CORNER)

        # create destination Grid
        self.dstGrid = esmf.EsmfStructGrid(dstGrid[0].shape, 
                                           coordSys = self.coordSys,
                                           periodicity = self.periodicity)
        self.dstGrid.setCoords(dstGrid, staggerloc = self.staggerloc)
        if dstGridMask is not None:
            self.dstGrid.setMask(dstGridMask)

        if dstBounds is not None:
            # Coords are CENTER (cell) based, bounds are CORNER (nodal)
            if self.staggerloc != CORNER:
                self.dstGrid.setCoords(dstBounds, 
                                       staggerloc = CORNER)
            elif self.staggerloc == CORNER:
                msg = BOUNDS_MESSAGE % staggerLoc
                raise RegridError, msg

        self.srcFld = esmf.EsmfStructField(self.srcGrid, 'srcFld', 
                                           datatype = self.dtype, 
                                           staggerloc = self.staggerloc)
        self.dstFld = esmf.EsmfStructField(self.dstGrid, 'dstFld', 
                                           datatype = self.dtype,
                                           staggerloc = self.staggerloc)

    def computeWeights(self, **args):
        """
        Compute interpolation weights
        @param **args (not used)
        """
        # Note: passing dstFrac = self.dstFracFld may cause a seg fault 
        # when runnning in parallel on some machines
        self.regridObj = esmf.EsmfRegrid(self.srcFld, self.dstFld,
                                  srcFrac = self.srcFracFld, 
                                  dstFrac = self.dstFracFld,
                                  srcMaskValues = self.srcMaskValues,
                                  dstMaskValues = self.dstMaskValues,
                                  regridMethod = self.regridMethod,
                                  unMappedAction = self.unMappedAction)

    def apply(self, srcData, dstData, rootPe, globalIndexing = False, **args):
        """
        Regrid source to destination
        @param srcData array source data, shape should 
                       cover entire global index space
        @param dstData array destination data, shape should 
                       cover entire global index space
        @param rootPe if other than None, then data will be MPI gathered
                      on the specified rootPe processor
        @param globalIndexing if True array was allocated over global index 
                              space on the processot, if False then array
                              was allocated over local index space on this
                              processor
        @param **args (not used)
        """
        self.srcFld.setLocalData(srcData, self.staggerloc, globalIndexing = globalIndexing)
        self.dstFld.setLocalData(dstData, self.staggerloc, globalIndexing = globalIndexing)

        # Regrid
        self.regridObj(self.srcFld, self.dstFld)

        # Get the destination data
        if rootPe is None:
            if globalIndexing:
                slab = self.dstGrid.getLocalSlab(staggerloc = self.staggerloc)
                dstData[slab] = self.dstFld.getData(rootPe = rootPe)
            else:
                dstData[:] = numpy.reshape(self.dstFld.getPointer(), dstData.shape)

        else:
            if globalIndexing:
                data = self.dstFld.getData(rootPe = rootPe)
                if self.pe == rootPe:
                    dstData[:] = data
            else:
                dstData[:] = numpy.reshape(self.dstFld.getPointer(), dstData.shape)

    def getSrcGrid(self):
        """
        Get the source grid on this processor
        @return grid
        """
        return [self.srcGrid.getCoords(i, staggerloc=self.staggerloc) \
                    for i in range(self.ndims)]

    def getDstGrid(self):
        """
        Get the destination grid on this processor
        @return grid
        """
        return [self.dstGrid.getCoords(i, staggerloc=self.staggerloc) \
                    for i in range(self.ndims)]

    def getSrcLocalSlab(self):
        """
        Get the source local slab (ellipsis). Use this to grab the data local 
        to this processor
        @return tuple of slices
        """
        staggerloc = CENTER
        return self.srcGrid.getLocalSlab(staggerloc)

    def getDstLocalSlab(self):
        """
        Get the destination local slab (ellipsis). You can use 
        this to grab the data local to this processor
        @return tuple of slices
        """
        staggerloc = CENTER
        return self.dstGrid.getLocalSlab(staggerloc)

    def getSrcCoordShape(self):
        """
        Get the local coordinate shape (may be different on each processor)
        @return tuple 
        """
        staggerloc = CENTER
        return self.srcGrid.getCoordShape(staggerloc)

    def getDstCoordShape(self):
        """
        Get the local coordinate shape (may be different on each processor)
        @return tuple 
        """
        staggerloc = CENTER
        return self.dstGrid.getCoordShape(staggerloc)

    def fillInDiagnosticData(self, diag, rootPe):
        """
        Fill in diagnostic data
        @param diag a dictionary whose entries, if present, will be filled
                    valid entries are: 'srcAreaFractions', 'dstAreaFractions',
                                       'srcAreas', 'dstAreas'
        @param rootPe root processor where data should be gathered (or 
                      None if local areas are to be returned)
        """
        for entry in  'srcAreaFractions', 'dstAreaFractions',  'srcAreas', 'dstAreas':
            if diag.has_key(entry):
                meth = 'get' + entry[0].upper() + entry[1:]
                parenStr = '(rootPe = rootPe)'
                diag[entry] = eval('self.regridObj.' + meth + parenStr)
        diag['regridTool'] = 'esmf'
        diag['regridMethod'] = self.regridMethodStr
        diag['periodicity'] = self.periodicity
        diag['coordSys'] = self.coordSysStr
        diag['staggerLoc'] = self.staggerlocStr
