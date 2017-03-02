#!/usr/bin/env python

"""
Copyright (c) 2008-2012, Tech-X Corporation
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the conditions
specified in the license file 'license.txt' are met.

Authors: David Kindig and Alex Pletzer
"""
import pdb
import re
import time
import numpy
from regrid2 import RegridError
import ESMF

# constants
R8 = ESMF.TypeKind.R8
R4 = ESMF.TypeKind.R4
I8 = ESMF.TypeKind.I8
I4 = ESMF.TypeKind.I4
CENTER = ESMF.StaggerLoc.CENTER # Same as ESMP_STAGGERLOC_CENTER_VCENTER
CORNER = ESMF.StaggerLoc.CORNER
VCORNER = ESMF.StaggerLoc.CORNER_VFACE
VFACE = VCORNER
CONSERVE = ESMF.RegridMethod.CONSERVE
PATCH = ESMF.RegridMethod.PATCH
BILINEAR = ESMF.RegridMethod.BILINEAR
IGNORE = ESMF.UnmappedAction.IGNORE
ERROR = ESMF.UnmappedAction.ERROR

class EsmfUnstructGrid:
    """
    Unstructured grid
    """
    def __init__(self, numTopoDims, numSpaceDims):
        """
        Constructor
        @param numTopoDims number of topological dimensions
        @param numSpaceDims number of space dimensions
        """
        # handle to the grid object
        self.grid = None
        # whether or not nodes were added
        self.nodesAdded = False
        # whether or not cells were added
        self.cellsAdded = False
        # the local processor rank
        self.pe = 0
        # number of processors
        self.nprocs = 1
        # communicator
        self.comm = None

        vm = ESMF.ESMP_VMGetGlobal()
        self.pe, self.nprocs = ESMF.ESMP_VMGet(vm)

        self.grid = ESMF.Mesh(parametric_dim=numTopoDims, spatial_dim=numSpaceDims)

    def setCells(self, cellIndices, cellTypes, connectivity,
                 cellMask=None, cellAreas=None):
        """
        Set Cell connectivity
        @param cell indices (0-based)
        @param cellTypes one of ESMP_MESHELEMTYPE_{TRI,QUAD,TETRA,HEX}
        @param connectivity node connectivity array, see below for node ordering
        @param cellMask
        @param cellAreas area (volume) of each cell


                     3                          4 ---------- 3
                    / \                         |            |
                   /   \                        |            |
                  /     \                       |            |
                 /       \                      |            |
                /         \                     |            |
               1 --------- 2                    1 ---------- 2



                 3                               8---------------7
                /|\                             /|              /|
               / | \                           / |             / |
              /  |  \                         /  |            /  |
             /   |   \                       /   |           /   |
            /    |    \                     5---------------6    |
           4-----|-----2                    |    |          |    |
            \    |    /                     |    4----------|----3
             \   |   /                      |   /           |   /
              \  |  /                       |  /            |  /
               \ | /                        | /             | /
                \|/                         |/              |/
                 1                          1---------------2

       ESMP_MESHELEMTYPE_TETRA             ESMP_MESHELEMTYPE_HEX

        """
        n = len(cellIndices)
        if not self.cellsAdded:
            # node/cell indices are 1-based in ESMF
            cellIndices += 1
            self.grid.add_elements(n, cellIndices, cellTypes,
                                      connectivity, elementMask=cellMask,
                                      elementArea=cellAreas)
        self.cellsAdded = True

    def setNodes(self, indices, coords, peOwners=None):
        """
        Set the nodal coordinates
        @param indices Ids of the nodes (0-based)
        @param coords nodal coordinates
        @param peOwners processor ranks where the coordinates reside (0-based)
        """
        n = len(indices)
        if not self.nodesAdded:
            if peOwners is None:
                peOwners = numpy.ones((n,), numpy.int32) * self.pe
            # node indices are 1-based
            indices += 1
            self.grid.add_nodes(n, indices, coords, peOwners)
#            ESMF.ESMP_MeshAddNodes(self.grid, n, indices, coords, peOwners)
        self.nodesAdded = True

    def toVTK(self, filename):
        """
        Write grid to VTK file format
        @param filename VTK file name
        """
#        ESMF.ESMP_MeshWrite(self.grid, filename)
        self.grid.write(filename)


    def __del__(self):
#        ESMF.ESMP_MeshDestroy(self.grid)
        self.grid.destroy()

################################################################################

class EsmfStructGrid:
    """
    Structured grid
    """
    def __init__(self, shape, coordSys = ESMF.CoordSys.SPH_DEG,
                 periodicity = 0, staggerloc = ESMF.StaggerLoc.CENTER,
                 hasBounds = False):
        """
        Constructor
        @param shape  Tuple of cell sizes along each axis
        @param coordSys    coordinate system
                           ESMF.CoordSys.CART              Cartesian
                           ESMF.CoordSys.SPH_DEG (default) Degrees
                           ESMF.CoordSys.SPH_RAD           Radians
        @param periodicity Does the grid have a periodic coordinate
                           0 No periodicity
                           1 Periodic in x (1st) axis
                           2 Periodic in x, y axes
        @param staggerloc ESMF stagger location. ESMF.StaggerLoc.XXXX
                          The stagger constants are listed at the top
        @param hasBounds If the grid has bounds, Run AddCoords for the bounds
        """
        # ESMF grid object
        self.grid = None
        # number of cells in [z,] y, x on all processors
        self.shape = shape
        # number of dimensions
        self.ndims = len(self.shape)
        # whether or not cell areas were set
        self.cellAreasSet = False
        # whether or not nodal coords were set
        self.nodesSet = False
        # whether or not cell centered coordinates were set
        self.centersSet = False

        maxIndex = numpy.array(shape, dtype = numpy.int32)
#        pdb.set_trace()
        if periodicity == 0:
            self.grid = ESMF.Grid(maxIndex, num_peri_dims=0, staggerloc=[staggerloc])
#            self.grid = ESMF.ESMP_GridCreateNoPeriDim(maxIndex,
#                                                      coordSys = coordSys)
        elif periodicity == 1:
            self.grid = ESMF.Grid(maxIndex, num_peri_dims=1, staggerloc=[staggerloc])
#            self.grid = ESMF.ESMP_GridCreate1PeriDim(maxIndex,
#                                                     coordSys = coordSys)
        else:
            msg = """
esmf.EsmfStructGrid.__init__: ERROR periodic dimensions %d > 1 not permitted.
            """ % periodicity
            raise RegridError, msg

        # Grid add coordinates call must go here for parallel runs
        # This occur before the fields are created, making the fields
        # parallel aware.
        self.grid.add_coords([staggerloc])
#        ESMF.ESMP_GridAddCoord(self.grid, staggerloc=staggerloc)
        if staggerloc ==  CENTER and not self.centersSet:
            self.centersSet = True
        elif staggerloc ==  CORNER and not self.nodesSet:
            self.nodesSet = True

        if hasBounds is not None:
            if self.ndims == 2:
                self.grid.add_coords([CORNER])
#                ESMF.ESMP_GridAddCoord(self.grid, staggerloc = CORNER)
            if self.ndims == 3:
                self.grid.add_coords([VCORNER])
#                ESMF.ESMP_GridAddCoord(self.grid, staggerloc = VCORNER)

    def getLocalSlab(self, staggerloc):
        """
        Get the local slab (ellipsis). You can use this to grab
        the data local to this processor
        @param staggerloc (e.g. ESMF.ESMP_STAGGERLOC_CENTER)
        @return tuple of slices
        """
        lo, hi = self.getLoHiBounds(staggerloc)
        return tuple([slice(lo[i], hi[i], None) \
                          for i in range(self.ndims)])

    def getLoHiBounds(self, staggerloc):
        """
        Get the local lo/hi index values for the coordinates (per processor)
                         (hi is not inclusive, lo <= index < hi)
        @param staggerloc e.g. ESMF.ESMP_STAGGERLOC_CENTER
        @return lo, hi lists
        """
#        lo, hi = ESMF.ESMP_GridGetCoord(self.grid, staggerloc)
        lo = self.grid.lower_bounds[staggerloc]
        hi = self.grid.upper_bounds[staggerloc]
        # reverse order since ESMF follows fortran order
#        return lo[::-1], hi[::-1]
        return lo, hi

    def getCoordShape(self, staggerloc):
        """
        Get the local coordinate shape (may be different on each processor)
        @param staggerloc (e.g. ESMF.ESMP_STAGGERLOC_CENTER)
        @return tuple
        """
        lo, hi = self.getLoHiBounds(staggerloc)
        return tuple( [hi[i] - lo[i] for i in range(self.ndims)] )

    def setCoords(self, coords, staggerloc = CENTER, globalIndexing = False):
        """
        Populate the grid with staggered coordinates (e.g. corner or center).
        @param coords   The curvilinear coordinates of the grid.
                        List of numpy arrays. Must exist on all procs.
        @param staggerloc  The stagger location
                           ESMF.ESMP_STAGGERLOC_CENTER (default)
                           ESMF.ESMP_STAGGERLOC_CORNER
        @param globalIndexing if True array was allocated over global index
                              space, otherwise array was allocated over
                              local index space on this processor. This
                              is only relevant if rootPe is None
        Note: coord dims in cdms2 are ordered in y, x, but ESMF expects x, y,
        hence the dimensions are reversed here.
        """
        # allocate space for coordinates, can only add coordinates once

        for i in range(self.ndims):
#            ptr = ESMF.ESMP_GridGetCoordPtr(self.grid, i, staggerloc)
            ptr = self.grid.get_coords(i)
            if globalIndexing:
                slab = self.getLocalSlab(staggerloc)
                # Populate self.grid with coordinates or the bounds as needed
                ptr[:] = coords[self.ndims-i-1][slab]
            else:
                ptr[:] = coords[self.ndims-i-1]

    def getCoords(self, dim, staggerloc):
        """
        Return the coordinates for a dimension
        @param dim desired dimension (zero based indexing)
        @param staggerloc Stagger location
        """
#        gridPtr = ESMF.ESMP_GridGetCoordPtr(self.grid, dim, staggerloc)
        gridPtr = self.grid.get_coords(dim)
        shp = self.getCoordShape(staggerloc)
        return numpy.reshape(gridPtr, shp)

    def setCellAreas(self, areas):
        """
        Set the cell areas
        @param areas numpy array
        """
#        ESMF.ESMP_GridAddItem(self.grid, item=ESMF.ESMP_GRIDITEM_AREA)
        self.grid.add_item(item=ESMF.GridItem.Area)
#        areaPtr = ESMF.ESMP_GridGetItem(self.grid,
#                                        item=ESMF.ESMP_GRIDITEM_AREA)
        areaPtr = self.grid.get_item(item=ESMF.GridItem.AREA)
        areaPtr[:] = areas.flat
        self.cellAreasSet = True

    def getCellAreas(self):
        """
        @return cell areas or None if setCellAreas was not called
        """
        if self.cellAreasSet:
#            areaPtr = ESMF.ESMP_GridGetItem(self.grid,
#                                            item = ESMF.ESMP_GRIDITEM_AREA)
            areaPtr = self.grid.get_item(item=ESMF.GridItem.AREA)
            return numpy.reshape(areaPtr, self.shape)
        else:
            return None

    def setMask(self, mask):
        """
        Set mask array. In ESMF, the mask is applied to cells.
        @param mask numpy array. 1 is invalid by default. This array exists
                    on all procs
        """
        #ESMF.ESMP_GridAddItem(self.grid, item=ESMF.ESMP_GRIDITEM_MASK)
#        maskPtr = ESMF.ESMP_GridGetItem(self.grid,
#                                        item=ESMF.ESMP_GRIDITEM_MASK)
        self.grid.add_item(item=ESMF.GridItem.Area)
        maskPtr = self.grid.get_item(item=ESMF.GridItem.MASK)
        slab = self.getLocalSlab(CENTER)
        maskPtr[:] = mask[slab].flat

    def __del__(self):
        #ESMF.ESMP_GridDestroy(self.grid)
        self.grid.destroy()

################################################################################

class EsmfStructField:
    """
    Structured field.
    """
    def __init__(self, esmfGrid, name, datatype, staggerloc = CENTER):
        """
        Creator for structured ESMF Field
        @param esmfGrid instance of an ESMF
        @param name field name (must be unique)
        @param datatype data type, one of 'float64', 'float32', 'int64', or 'int32'
                        (or equivalent numpy dtype)
        @param staggerloc ESMP_STAGGERLOC_CENTER
                          ESMP_STAGGERLOC_CORNER
        """
        # field object
        self.field = None
        # the local processor rank
        self.pe = 0
        # the number of processors
        self.nprocs = 1
        # associated grid
        self.grid = esmfGrid
        # staggering
        self.staggerloc = staggerloc
        # communicator
        self.comm = None

        try:
            from mpi4py import MPI
            self.comm = MPI.COMM_WORLD
        except:
            pass

        vm = ESMF.ESMP_VMGetGlobal()
        self.pe, self.nprocs = ESMF.ESMP_VMGet(vm)

        etype = None
        sdatatype = str(datatype) # in case user passes a numpy dtype
        if re.search('float64', sdatatype):
            etype = R8
        elif re.search('float32', sdatatype):
            etype = R4
        elif re.search('int64', sdatatype):
            etype = I8
        elif re.search('int32', sdatatype):
            etype = I4
        else:
            msg = 'esmf.EsmfStructField.__init__: ERROR invalid type %s' % datatype
            raise RegridError, msg

#        self.field = ESMF.ESMP_FieldCreateGrid(esmfGrid.grid,
#                                               name,
#                                               staggerloc = staggerloc,
#                                               typekind = etype)
        self.field = ESMF.Field(esmfGrid.grid, name=name, typekind = etype, staggerloc = staggerloc)

    def getPointer(self):
        """
        Get field data as a flat array
        @return pointer
        """
#        return ESMF.ESMP_FieldGetPtr(self.field)
        self.field.get_area()
        return self.field.data

    def getData(self, rootPe):
        """
        Get field data as a numpy array
        @param rootPe if None then local data will be fetched, otherwise
                      gather the data on processor "rootPe" (all other
                      procs will return None).
        @return numpy array or None
        """
        ptr = self.getPointer()
        if rootPe is None:
            shp = self.grid.getCoordShape(staggerloc = self.staggerloc)
            # local data, copy
            return ptr.reshape(shp)
        else:
            # gather the data on rootPe
            lo, hi = self.grid.getLoHiBounds(self.staggerloc)
            los = [lo]
            his = [hi]
            ptrs = [ptr]
            if self.comm is not None:
                los = self.comm.gather(lo)  # Local
                his = self.comm.gather(hi)  # Local 
                ptrs = self.comm.gather(ptr, root = rootPe)

            if self.pe == rootPe:    # Local
                # reassemble, find the largest hi indices to set
                # the shape of the data container
                bigHi = [0 for i in range(self.grid.ndims)]
                for i in range(self.grid.ndims):
                    bigHi[i] = reduce(lambda x,y: max(x, y),
                                      [his[p][i] for p in range(self.nprocs)])
                # allocate space to retrieve the data
                bigData = numpy.empty(bigHi, ptr.dtype)
                bigData[:] = 0.0

            # populate the data
                for p in range(self.nprocs):
                    slab = tuple([slice(los[p][i], his[p][i], None) for \
                                      i in range(self.grid.ndims)])
                    # copy
                    bigData[slab].flat = ptrs[p]
                return bigData         # Local

        # rootPe is not None and self.pe != rootPe
        return None

    def setLocalData(self, data, staggerloc, globalIndexing = False):
        """
        Set local field data
        @param data full numpy array, this method will take care of setting a
                    the subset of the data that reside on the local processor
        @param staggerloc stagger location of the data
        @param globalIndexing if True array was allocated over global index
                              space, array was allocated over local index
                              space (on this processor)
        """
        ptr = self.getPointer()
        if globalIndexing:
            slab = self.grid.getLocalSlab(staggerloc)
            ptr[:] = data[slab].flat
        else:
            ptr[:] = data.flat

    def  __del__(self):
#        ESMF.ESMP_FieldDestroy(self.field)
        self.field.destroy()

################################################################################

class EsmfRegrid:
    """
    Regrid source grid data to destination grid data
    """
    def __init__(self, srcField, dstField,
                 srcFrac = None,
                 dstFrac = None,
                 srcMaskValues = None,
                 dstMaskValues = None,
                 regridMethod   = BILINEAR,
                 unMappedAction = IGNORE):
        """
        Constuct regrid object
        @param srcField the source field object of type EsmfStructField
        @param dstField the destination field object of type EsmfStructField
        @param srcMaskValues Value of masked cells in source
        @param dstMaskValues Value of masked cells in destination
        @param srcFrac Cell fractions on source grid (type EsmfStructField)
        @param dstFrac Cell fractions on destination grid (type EsmfStructField)
        @param regridMethod ESMF.ESMP_REGRIDMETHOD_{BILINEAR,CONSERVE,PATCH}
        @param unMappedAction ESMF.ESMP_UNMAPPEDACTION_{IGNORE,ERROR}
        """
        self.srcField = srcField
        self.dstField = dstField
        self.regridMethod = regridMethod
        self.srcAreaField = None
        self.dstAreaField = None
        self.srcFracField = srcFrac
        self.dstFracField = dstFrac
        self.regridHandle = None

        timeStamp = re.sub('\.', '', str(time.time()))

        # create and initialize the cell areas to zero
        if regridMethod == CONSERVE:
            self.srcAreaField = EsmfStructField(self.srcField.grid,
                                                name = 'src_areas_%s' % timeStamp,
                                                datatype = 'float64',
                                                staggerloc = CENTER)
            dataPtr = self.srcAreaField.getPointer()
            dataPtr[:] = 0.0
            self.dstAreaField = EsmfStructField(self.dstField.grid,
                                                name = 'dst_areas_%s' % timeStamp,
                                                datatype = 'float64',
                                                staggerloc = CENTER)
            dataPtr = self.dstAreaField.getPointer()
            dataPtr[:] = 0.0

        # initialize fractional areas to 1 (unless supplied)
        if srcFrac is None:
            self.srcFracField = EsmfStructField(self.srcField.grid,
                                                name = 'src_cell_area_fractions_%s' % timeStamp,
                                                datatype = 'float64',
                                                staggerloc = CENTER)
            dataPtr = self.srcFracField.getPointer()
            dataPtr[:] = 1.0

        if dstFrac is None:
            self.dstFracField = EsmfStructField(self.dstField.grid,
                                                name = 'dst_cell_area_fractions_%s' % timeStamp,
                                                datatype = 'float64',
                                                staggerloc = CENTER)
            dataPtr = self.dstFracField.getPointer()
            dataPtr[:] = 1.0

        srcMaskValueArr = None
        if srcMaskValues is not None:
            srcMaskValueArr = numpy.array(srcMaskValues, dtype=numpy.int32)

        dstMaskValueArr = None
        if dstMaskValues is not None:
            dstMaskValueArr = numpy.array(dstMaskValues, dtype=numpy.int32)

        #self.regridHandle = ESMF.ESMP_FieldRegridStore(
        self.regridHandle = ESMF.Regrid(
                                     srcField.field,
                                     dstField.field,
                                     src_mask_values = srcMaskValueArr,
                                     dst_mask_values = dstMaskValueArr,
                                     src_frac_field  = self.srcFracField.field,
                                     dst_frac_field  = self.dstFracField.field,
                                     regrid_method   = regridMethod,
                                     unmapped_action = unMappedAction)

    def getSrcAreas(self, rootPe):
        """
        Get the src grid areas as used by conservative interpolation
        @param rootPe None is local areas are returned, otherwise
                      provide rootPe and the data will be gathered
        @return numpy array or None if interpolation is not conservative
        """
        if self.srcAreaField is not None:
#            ESMF.ESMP_FieldRegridGetArea(self.srcAreaField.field)
            self.srcAreaField.get_area()
            return self.srcAreaField.data
        return None

    def getDstAreas(self, rootPe):
        """
        Get the dst grid areas as used by conservative interpolation
        @param rootPe None is local areas are returned, otherwise
                      provide rootPe and the data will be gathered
        @return numpy array or None if interpolation is not conservative
        """
        if self.srcAreaField is not None:
#            ESMF.ESMP_FieldRegridGetArea(self.dstAreaField.field)
            self.dstAreaField.get_area()
            return self.dstAreaField.data
        return None

    def getSrcAreaFractions(self, rootPe):
        """
        Get the source grid fraction areas as used by conservative interpolation
        @param rootPe None is local areas are returned, otherwise
                      provide rootPe and the data will be gathered
        @return numpy array
        """
        if self.srcFracField is not None:
            return self.srcFracField.data
        return None

    def getDstAreaFractions(self, rootPe):
        """
        Get the destination grid fraction areas as used by conservative interpolation
        @param rootPe None is local areas are returned, otherwise
                      provide rootPe and the data will be gathered
        @return numpy array
        """
        if self.dstFracField is not None:
            return self.dstFracField.data
        return None

    def __call__(self, srcField=None, dstField=None):
        """
        Apply interpolation weights
        @param srcField source field (or None if src field passed to
               constructor is to be used)
        @param dstField destination field (or None if dst field passed
               to constructor is to be used)
        """
        if srcField == None:
            srcField = self.srcField
        if dstField == None:
            dstField = self.dstField

        # default is keep the masked values intact
        zeroregion = ESMF.Region.SELECT
        if self.regridMethod == CONSERVE:
            zeroregion = None # will initalize to zero

#        ESMF.ESMP_FieldRegrid(srcField.field, dstField.field,
#                              self.regridHandle,
#                              zeroregion = zeroregion)
        ESMF.Regrid(srcField.field, dstField.field, zeroregion)

    def __del__(self):
        if self.regridHandle is not None:
            ESMF.ESMP_FieldRegridRelease(self.regridHandle)

