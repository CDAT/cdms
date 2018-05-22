#This code is provided with the hope that it will be useful.
#No guarantee is provided whatsoever. Use at your own risk.
#
#David Kindig and Alex Pletzer, Tech-X Corp. (2012)


"""
ESMF regridding class
"""
import re
import numpy

import ESMF
from . import esmf
from . import RegridError
from .mvGenericRegrid import GenericRegrid

ESMF.Manager(debug=False)
HAVE_MPI = False
try:
    from mpi4py import MPI
    HAVE_MPI = True
except BaseException:
    pass

# constants
CENTER = ESMF.StaggerLoc.CENTER  # Same as ESMF_STAGGERLOC_CENTER_VCENTER
CORNER = ESMF.StaggerLoc.CORNER
VCORNER = ESMF.StaggerLoc.CORNER_VFACE
VFACE = VCORNER
CONSERVE = ESMF.RegridMethod.CONSERVE
PATCH = ESMF.RegridMethod.PATCH
BILINEAR = ESMF.RegridMethod.BILINEAR
IGNORE = ESMF.UnmappedAction.IGNORE
ERROR = ESMF.UnmappedAction.ERROR


class ESMFRegrid(GenericRegrid):
    """
    Regrid class for ESMF
     Constructor
       
 Parameters
 ----------

           srcGridShape 
                tuple source grid shape

           dstGridShape
                tuple destination grid shape

           dtype
                a valid numpy data type for the src/dst data

           regridMethod
               'linear', 'conserve', or 'patch'

           staggerLoc
               the staggering of the field, 'center' or 'corner'

           periodicity
               0 (no periodicity),
               1 (last coordinate is periodic,
               2 (both coordinates are periodic)

           coordSys
               'deg', 'cart', or 'rad'

           hasSrcBounds
               tuple source bounds shape

           hasDstBounds
               tuple destination bounds shape

           ignoreDegenerate
               Ignore degenerate celss when checking inputs
    """

    def __init__(self, srcGridshape, dstGridshape, dtype,
                 regridMethod, staggerLoc, periodicity, coordSys,
                 srcGridMask=None, hasSrcBounds=False, srcGridAreas=None,
                 dstGridMask=None, hasDstBounds=False, dstGridAreas=None,
                 ignoreDegenerate=False,
                 **args):
        """
       
        """

        # esmf grid objects (tobe constructed)
        self.srcGrid = None
        self.dstGrid = None
        self.dtype = dtype

        self.srcGridShape = srcGridshape
        self.dstGridShape = dstGridshape
        self.ignoreDegenerate = ignoreDegenerate
        self.ndims = len(self.srcGridShape)

        self.hasSrcBounds = hasSrcBounds
        self.hasDstBounds = hasDstBounds

        self.regridMethod = BILINEAR
        self.regridMethodStr = 'linear'
        if isinstance(regridMethod, str):
            if re.search('conserv', regridMethod.lower()):
                self.regridMethod = CONSERVE
                self.regridMethodStr = 'conserve'
            elif re.search('patch', regridMethod.lower()):
                self.regridMethod = PATCH
                self.regridMethodStr = 'patch'

        # data stagger
        self.staggerloc = CENTER
        self.staggerlocStr = 'center'
        if isinstance(staggerLoc, str):
            if re.search('vface', staggerLoc.lower(), re.I):
                self.staggerloc = VFACE
                self.staggerlocStr = 'vcorner'
            # there are other staggers we could test here
            elif re.search('corner', staggerLoc.lower(), re.I) or \
                    re.search('node', staggerLoc.lower(), re.I):
                self.staggerloc = CORNER
                self.staggerlocStr = 'corner'
            # there are other staggers we could test here

        # good for now
        unMappedAction = args.get('unmappedaction', 'ignore')
        self.unMappedAction = ESMF.UnmappedAction.IGNORE
        if re.search('error', unMappedAction.lower()):
            self.unMappedAction = ESMF.UnmappedAction.ERROR

        self.coordSys = ESMF.CoordSys.SPH_DEG
        self.coordSysStr = 'deg'
        if re.search('cart', coordSys.lower()):
            self.coordSys = ESMF.CoordSys.CART
            self.coordSysStr = 'cart'
        elif re.search('rad', coordSys.lower()):
            self.coordSys = ESMF.CoordSys.SPH_RAD
            self.coordSysStr = 'rad'

        self.periodicity = periodicity

        # masks can take several values in ESMF, we'll have just one
        # value (1) which means invalid
#        self.srcMaskValues = numpy.array([1],dtype = numpy.int32)
#        self.dstMaskValues = numpy.array([1],dtype = numpy.int32)

        if isinstance(regridMethod, str):
            if re.search('conserv', regridMethod.lower()):
                self.srcMaskValues = numpy.array([1], dtype=numpy.int32)
                self.dstMaskValues = numpy.array([1], dtype=numpy.int32)
            else:
                self.srcMaskValues = srcGridMask
                self.dstMaskValues = dstGridMask

        # provided by user or None
        self.srcGridAreas = srcGridAreas
        self.dstGridAreas = dstGridAreas
        self.maskPtr = None

        # MPI stuff
        self.pe = 0
        self.nprocs = 1
        self.comm = None
        if HAVE_MPI:
            self.comm = MPI.COMM_WORLD
            self.pe = self.comm.Get_rank()
            self.nprocs = self.comm.Get_size()

        # checks
        if self.ndims != len(self.dstGridShape):
            msg = """
mvESMFRegrid.ESMFRegrid.__init__: mismatch in the number of topological
dimensions. len(srcGridshape) = %d != len(dstGridshape) = %d""" % \
                (self.ndims, len(self.dstGridShape))
            raise RegridError(msg)

        # Initialize the grids without data.
        self.srcGrid = esmf.EsmfStructGrid(self.srcGridShape,
                                           coordSys=self.coordSys,
                                           periodicity=self.periodicity,
                                           staggerloc=self.staggerloc,
                                           hasBounds=self.hasSrcBounds)
        self.dstGrid = esmf.EsmfStructGrid(dstGridshape,
                                           coordSys=self.coordSys,
                                           periodicity=self.periodicity,
                                           staggerloc=self.staggerloc,
                                           hasBounds=self.hasDstBounds)

        # Initialize the fields with data.
        self.srcFld = esmf.EsmfStructField(self.srcGrid, 'srcFld',
                                           datatype=self.dtype,
                                           staggerloc=self.staggerloc)
        self.dstFld = esmf.EsmfStructField(self.dstGrid, 'dstFld',
                                           datatype=self.dtype,
                                           staggerloc=self.staggerloc)

        self.srcAreaField = esmf.EsmfStructField(self.srcGrid, name='srcAreas',
                                                 datatype=self.dtype,
                                                 staggerloc=self.staggerloc)
        self.dstAreaField = esmf.EsmfStructField(self.dstGrid, name='dstAreas',
                                                 datatype=self.dtype,
                                                 staggerloc=self.staggerloc)

        self.srcFracField = esmf.EsmfStructField(self.srcGrid, name='srcFracAreas',
                                                 datatype=self.dtype,
                                                 staggerloc=self.staggerloc)
        self.dstFracField = esmf.EsmfStructField(self.dstGrid, name='dstFracAreas',
                                                 datatype=self.dtype,
                                                 staggerloc=self.staggerloc)
        self.srcFld.field.data[:] = -1
        self.dstFld.field.data[:] = -1
        self.srcAreaField.field.data[:] = 0.0
        self.dstAreaField.field.data[:] = 0.0
        self.srcFracField.field.data[:] = 1.0
        self.dstFracField.field.data[:] = 1.0

    def setCoords(self, srcGrid, dstGrid,
                  srcGridMask=None, srcBounds=None, srcGridAreas=None,
                  dstGridMask=None, dstBounds=None, dstGridAreas=None,
                  globalIndexing=False, **args):
        """
        Populator of grids, bounds and masks

        Parameters
        ----------

            srcGrid
                list [[z], y, x] of source grid arrays

            dstGrid
                list [[z], y, x] of dstination grid arrays

            srcGridMask
                list [[z], y, x] of arrays

            srcBounds
                list [[z], y, x] of arrays

            srcGridAreas
                list [[z], y, x] of arrays

            dstGridMask
                list [[z], y, x] of arrays

            dstBounds
                list [[z], y, x] of arrays

            dstGridAreas
                list [[z], y, x] of arrays

            globalIndexing 
                if True array was allocated over global index space, otherwise array was allocated over local index space on this processor. This is only relevant if rootPe is None
        """

        # create esmf source Grid
        self.srcGrid.setCoords(srcGrid, staggerloc=self.staggerloc,
                               globalIndexing=globalIndexing)

        if srcGridMask is not None:
            self.srcGrid.setMask(srcGridMask, self.staggerloc)

        if srcBounds is not None:
            # Coords are CENTER (cell) based, bounds are CORNER (nodal)
            # VCORNER for 3D
            if self.staggerloc != CORNER and self.staggerloc != VCORNER:
                if self.ndims == 2:
                    # cell field, need to provide the bounds
                    self.srcGrid.setCoords(srcBounds, staggerloc=CORNER,
                                           globalIndexing=globalIndexing)
                if self.ndims == 3:
                    # cell field, need to provide the bounds
                    self.srcGrid.setCoords(srcBounds, staggerloc=VCORNER,
                                           globalIndexing=globalIndexing)

            elif self.staggerloc == CORNER or self.staggerloc == VCORNER:
                msg = """
mvESMFRegrid.ESMFRegrid.__init__: can't set the src bounds for
staggerLoc = %s!""" % self.staggerLoc
                raise RegridError(msg)

        # create destination Grid
        self.dstGrid.setCoords(dstGrid, staggerloc=self.staggerloc,
                               globalIndexing=globalIndexing)
        if dstGridMask is not None:
            self.dstGrid.setMask(dstGridMask)

        if dstBounds is not None:
            # Coords are CENTER (cell) based, bounds are CORNER (nodal)
            if self.staggerloc != CORNER and self.staggerloc != VCORNER:
                if self.ndims == 2:
                    self.dstGrid.setCoords(dstBounds, staggerloc=CORNER,
                                           globalIndexing=globalIndexing)
                if self.ndims == 3:
                    self.dstGrid.setCoords(dstBounds, staggerloc=VCORNER,
                                           globalIndexing=globalIndexing)
            elif self.staggerloc == CORNER or self.staggerloc == VCORNER:
                msg = """
mvESMFRegrid.ESMFRegrid.__init__: can't set the dst bounds for
staggerLoc = %s!""" % self.staggerLoc
                raise RegridError(msg)

    def computeWeights(self, **args):
        """
        Compute interpolation weights

        Parameters
        ----------

            **args
                (not used)

            _: None
        """
        self.regridObj = ESMF.Regrid(srcfield=self.srcFld.field,
                                     dstfield=self.dstFld.field,
                                     src_mask_values=self.srcMaskValues,
                                     dst_mask_values=self.dstMaskValues,
                                     regrid_method=self.regridMethod,
                                     unmapped_action=self.unMappedAction,
                                     ignore_degenerate=True)

    def apply(self, srcData, dstData, rootPe, globalIndexing=False, **args):
        """
        Regrid source to destination.
        When used in parallel, if the processor is not the root processor,
        the dstData returns None.

        Source data mask:
       
            . If you provide srcDataMask in args the source grid will be masked and weights will be recomputed.

            . Subsequently, if you do not provide a srcDataMask the last weights will be used to regrid the source data array.

            . By default, only the data are masked, but not the grid.

        Parameters
        ----------

           srcData
               array source data, shape should cover entire global index space

           dstData
               array destination data, shape should cover entire global index space

           rootPe
               if other than None, then data will be MPI gathered on the specified rootPe processor

           globalIndexing
               if True array was allocated over global index space, otherwise array was allocated over local index space on this processor. This is only relevant if rootPe is None

            **args
        """

#        if args.has_key('srcDataMask'):
#            srcDataMask=args.get('srcDataMask')
        # Make sure with have a mask intialized for this grid.

#            if(self.maskPtr is None):
#                if(self.srcFld.field.grid.mask[self.staggerloc] is None):
#                    self.srcFld.field.grid.add_item(item=ESMF.GridItem.MASK, staggerloc=self.staggerloc)
#                self.maskPtr = self.srcFld.field.grid.get_item(item=ESMF.GridItem.MASK,
#                                                               staggerloc=self.staggerloc)
        # Recompute weights only if masks are different.
#            if(not numpy.array_equal(self.maskPtr, srcDataMask)):
#                self.maskPtr[:] = srcDataMask[:]
#                self.computeWeights(**args)

        zero_region = ESMF.Region.SELECT
        if 'zero_region' in args.keys():
            zero_region=args.get('zero_region')

        self.srcFld.field.data[:] = srcData.T
        self.dstFld.field.data[:] = dstData.T
        # regrid

        self.regridObj(self.srcFld.field, self.dstFld.field, zero_region=zero_region)

        # fill in dstData
        if rootPe is None and globalIndexing:
            # only fill in the relevant portion of the data
            slab = self.dstGrid.getLocalSlab(staggerloc=self.staggerloc)
            dstData[slab] = self.dstFld.getData(rootPe=rootPe)
        else:
            tmp = self.dstFld.field.data.T
            if tmp is None:
                dstData = None
            else:
                dstData[:] = tmp

    def getDstGrid(self):
        """
        Get the destination grid on this processor
     
        Returns
        -------
            grid
        """
        return [self.dstGrid.getCoords(i, staggerloc=self.staggerloc)
                for i in range(self.ndims)]

    def getSrcAreas(self, rootPe):
        """
        Get the source grid cell areas

Parameters
----------
            rootPe
                root processor where data should be gathered (or None if local areas are to be returned)

            _: None

       Returns
       -------
           areas
               or None if non-conservative interpolation
        """
        if self.regridMethod == CONSERVE:
            #            self.srcAreaField.field.get_area()
            return self.srcAreaField.field.data
        else:
            return None

    def getDstAreas(self, rootPe):
        """
        Get the destination grid cell areas

        Parameters
        ----------

            rootPe
                root processor where data should be gathered (or None if local areas are to be returned)

            _: None

     
        Returns
        -------

            areas or None if non-conservative interpolation
        """
        if self.regridMethod == CONSERVE:
            #            self.dstAreaField.field.get_area()
            return self.dstAreaField.field.data
        else:
            return None

    def getSrcAreaFractions(self, rootPe):
        """
        Get the source grid area fractions 

Parameters
----------

            rootPe
               root processor where data should be gathered (or None if local areas are to be returned)

            _: None
       

       Returns
       -------

           fractional areas or None (if non-conservative)
        """
        if self.regridMethod == CONSERVE:
            return self.srcFracField.field.data
        else:
            return None

    def getDstAreaFractions(self, rootPe):
        """
        Get the destination grid area fractions

        Parameters
        ----------
     
            rootPe
               root processor where data should be gathered (or None if local areas are to be returned)

            _: None

        Returns
        -------

            fractional areas
                or None (if non-conservative)
        """
        if self.regridMethod == CONSERVE:
            return self.dstFracField.field.data
        else:
            return

    def getSrcLocalShape(self, staggerLoc):
        """
        Get the local source coordinate/data shape (may be different on each processor)

        Parameters
        ----------

            staggerLoc
                (e.g. 'center' or 'corner')

            _: None

        Returns
        -------

            tuple
        """
        stgloc = CENTER
        if re.match('corner', staggerLoc, re.I) or \
           re.search('nod', staggerLoc, re.I):
            stgloc = CORNER
        elif re.search('vface', staggerLoc, re.I) or \
                re.search('vcorner', staggerLoc, re.I):
            stgloc = VFACE
        return self.srcGrid.getCoordShape(stgloc)

    def getDstLocalShape(self, staggerLoc):
        """
        Get the local destination coordinate/data shape (may be different on each processor)

        Parameters
        ----------

            staggerLoc
                (e.g. 'center' or 'corner')

            _: None

        Returns
        -------

            tuple
        """
        stgloc = CENTER
        if re.match('corner', staggerLoc, re.I) or \
           re.search('nod', staggerLoc, re.I):
            stgloc = CORNER
        elif re.search('vface', staggerLoc, re.I) or \
                re.search('vcorner', staggerLoc, re.I):
            stgloc = VFACE
        return self.dstGrid.getCoordShape(stgloc)

    def getSrcLocalSlab(self, staggerLoc):
        """
        Get the destination local slab (ellipsis). You can use this to grab the data 
        local to this processor

        Parameters
        ----------

            staggerLoc
                (e.g. 'center'):

            _: None

        Returns
        -------

           tuple of slices
        """
        stgloc = CENTER
        if re.match('corner', staggerLoc, re.I) or \
           re.search('nod', staggerLoc, re.I):
            stgloc = CORNER
        elif re.search('vface', staggerLoc, re.I) or \
                re.search('vcorner', staggerLoc, re.I):
            stgloc = VFACE
        return self.srcGrid.getLocalSlab(stgloc)

    def getDstLocalSlab(self, staggerLoc):
        """
        Get the destination local slab (ellipsis). You can use this to grab the data local to this
        processor

        Parameters
        ----------

            staggerLoc
                (e.g. 'center')

            _: None

        Returns
        -------
         
           tuple of slices
        """
        stgloc = CENTER
        if re.match('corner', staggerLoc, re.I) or \
           re.search('nod', staggerLoc, re.I):
            stgloc = CORNER
        elif re.search('vface', staggerLoc, re.I) or \
                re.search('vcorner', staggerLoc, re.I):
            stgloc = VFACE
        return self.dstGrid.getLocalSlab(stgloc)

    def fillInDiagnosticData(self, diag, rootPe):
        """
        Fill in diagnostic data

        Parameters
        ----------

            diag
                a dictionary whose entries, if present, will be filled valid entries are: 'srcAreaFractions', 'dstAreaFractions', srcAreas', 'dstAreas'
            
            rootPe
                root processor where data should be gathered (or None if local areas are to be returned)
        """
        oldMethods = {}
        oldMethods['srcAreaFractions'] = 'getSrcAreaFractions'
        oldMethods['dstAreaFractions'] = 'getDstAreaFractions'
        oldMethods['srcAreas'] = 'getSrcAreas'
        oldMethods['dstAreas'] = 'getDstAreas'
        for entry in 'srcAreaFractions', 'dstAreaFractions',  \
                'srcAreas', 'dstAreas':
            if entry in diag:
                diag[entry] = eval(
                    'self.' + oldMethods[entry] + '(rootPe=rootPe)').T
        diag['regridTool'] = 'esmf'
        diag['regridMethod'] = self.regridMethodStr
        diag['periodicity'] = self.periodicity
        diag['coordSys'] = self.coordSysStr
        diag['staggerLoc'] = self.staggerlocStr
