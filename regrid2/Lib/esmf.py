#!/usr/bin/env python

#
# Copyright (c) 2008-2012, Tech-X Corporation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the conditions
# specified in the license file 'license.txt' are met.
#
# Authors: David Kindig and Alex Pletzer
#

import re
import time
import numpy
from regrid2 import RegridError
import ESMF
from functools import reduce

from cdms2.util import getenv_bool


# constants
R8 = ESMF.TypeKind.R8
R4 = ESMF.TypeKind.R4
I8 = ESMF.TypeKind.I8
I4 = ESMF.TypeKind.I4
CENTER = ESMF.StaggerLoc.CENTER  # Same as ESMF.StaggerLoc.CENTER_VCENTER
CENTER_VCENTER = ESMF.StaggerLoc.CENTER_VCENTER
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
    Constructor

    Parameters
    ----------
    numTopoDims :  number of topological dimensions

    numSpaceDims : number of space dimensions
    """

    def __init__(self, numTopoDims, numSpaceDims):
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

        self.grid = ESMF.Mesh(
            parametric_dim=numTopoDims,
            spatial_dim=numSpaceDims)

    def setCells(self, cellIndices, cellTypes, connectivity,
                 cellMask=None, cellAreas=None):
        """
        Set Cell connectivity.

        Parameters
        ----------

        cellIndices : any 0-based.

        cellTypes : any one of ESMF_MESHELEMTYPE_{TRI,QUAD,TETRA,HEX}.

        connectivityNode : any connectivity array, see below for node ordering.

        cellMask : any cellAreas area (volume) of each cell.



        Notes
        -----

::


                    3                       4-------------3
                    /\                      |             |
                   /  \                     |             |
                  /    \                    |             |
                 /      \                   |             |
                /        \                  |             |
               /          \                 |             |
              1------------2                1-------------2



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

       ESMF_MESHELEMTYPE_TETRA             ESMF.MESHELEMTYPE_HEX

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

        Parameters
        ----------
        indices : Ids of the nodes (0-based)

        coords : nodal coordinates

        peOwners : processor ranks where the coordinates reside (0-based)
        """
        n = len(indices)
        if not self.nodesAdded:
            if peOwners is None:
                peOwners = numpy.ones((n,), numpy.int32) * self.pe
            # node indices are 1-based
            indices += 1
            self.grid.add_nodes(n, indices, coords, peOwners)
        self.nodesAdded = True

    def toVTK(self, filename):
        """
        Write grid to VTK file format

        Parameters
        ----------
        filename : VTK file name

        """
        self.grid.write(filename)

    def __del__(self):
        self.grid.destroy()

##########################################################################


class EsmfStructGrid:
    """
    Structured grid

    Parameters
    ----------

    shape : Tuple of cell sizes along each axis

    coordSys : coordinate system
               ESMF.CoordSys.CART Cartesian
               ESMF.CoordSys.SPH_DEG (default) Degrees
               ESMF.CoordSys.SPH_RAD Radians

    periodicity : Does the grid have a periodic coordinate
                  0 No periodicity
                  1 Periodic in x (1st) axis
                  2 Periodic in x, y axes

    staggerloc : ESMF stagger location. ESMF.StaggerLoc.XXXX
                 The stagger constants are listed at the top

    hasBounds : If the grid has bounds, Run AddCoords for the bounds
    """

    def __init__(self, shape, coordSys=ESMF.CoordSys.SPH_DEG,
                 periodicity=0, staggerloc=ESMF.StaggerLoc.CENTER,
                 hasBounds=False):
        """

        """
        # ESMF grid object
        self.grid = None
        # number of cells in [z,] y, x on all processors
        self.shape = shape[::-1]
        # number of dimensions
        self.ndims = len(self.shape)
        # whether or not cell areas were set
        self.cellAreasSet = False
        # whether or not nodal coords were set
        self.nodesSet = False
        # whether or not cell centered coordinates were set
        self.centersSet = False

        # assume last 2 dimensions are Y,X
        # For esmf reverse to X, Y
        maxIndex = numpy.array(shape[::-1], dtype=numpy.int32)

        self.centersSet = False
        periodic_dim = 0
        pole_dim = 1
        if periodicity == 0:
            self.grid = ESMF.Grid(max_index=maxIndex, num_peri_dims=0, staggerloc=[staggerloc],
                                  coord_sys=coordSys)
        elif periodicity == 1:
            self.grid = ESMF.Grid(max_index=maxIndex, num_peri_dims=1,
                                  periodic_dim=periodic_dim, pole_dim=pole_dim,
                                  staggerloc=[staggerloc], coord_sys=coordSys)
        else:
            msg = """
esmf.EsmfStructGrid.__init__: ERROR periodic dimensions %d > 1 not permitted.
            """ % periodicity
            raise RegridError(msg)

        # Grid add coordinates call must go here for parallel runs
        # This occur before the fields are created, making the fields
        # parallel aware.
        if ((staggerloc == CENTER) and (not self.centersSet)):
            self.centersSet = True
        elif (staggerloc == CORNER) and (not self.nodesSet):
            self.nodesSet = True

        if hasBounds is not None:
            if self.ndims == 2:
                self.grid.add_coords([CORNER], coord_dim=None, from_file=False)
            if self.ndims == 3:
                self.grid.add_coords(
                    [VCORNER], coord_dim=None, from_file=False)

    def getLocalSlab(self, staggerloc):
        """
        Get the local slab (ellipsis). You can use this to grab
        the data local to this processor

        Parameters
        -----------
        staggerloc : (e.g. ESMF.StaggerLoc.CENTER)


        Returns
        -------
        tuple of slices.
        """
        lo, hi = self.getLoHiBounds(staggerloc)
        return tuple([slice(lo[i], hi[i], None)
                      for i in range(self.ndims)])[::-1]

    def getLoHiBounds(self, staggerloc):
        """
        Get the local lo/hi index values for the coordinates (per processor)
        (hi is not inclusive, lo <= index < hi)

        Parameters
        ----------
        staggerloc : (e.g. ESMF.StaggerLoc.CENTER)


        Returns
        -------
        lo, hi lists.
        """
        lo = self.grid.lower_bounds[staggerloc]
        hi = self.grid.upper_bounds[staggerloc]
        return lo, hi

    def getCoordShape(self, staggerloc):
        """
        Get the local coordinate shape (may be different on each processor)

        Parameters
        ----------
        staggerloc : (e.g. ESMF.StaggerLoc.CENTER)


        Returns
        -------
        tuple
        """
        lo, hi = self.getLoHiBounds(staggerloc)
        return tuple([hi[i] - lo[i] for i in range(self.ndims)])[::-1]

    def setCoords(self, coords, staggerloc=CENTER, globalIndexing=False):
        """
        Populate the grid with staggered coordinates (e.g. corner or center).

        Parameters
        ----------

        coords : The curvilinear coordinates of the grid. List of numpy arrays.
                 Must exist on all procs.

        staggerloc : The stagger location ESMF.StaggerLoc.CENTER (default)
                     ESMF.StaggerLoc.CORNER

        globalIndexing : if True array was allocated over global index space, otherwise array was
                         allocated over local index space on this processor. This is only relevant
                         if rootPe is None

        Notes
        -----
        coord dims in cdms2 are ordered in y, x, but ESMF expects x, y, hence the
        dimensions are reversed here.
        """
        # allocate space for coordinates, can only add coordinates once
        for i in range(self.ndims):
            ptr = self.grid.get_coords(coord_dim=i, staggerloc=staggerloc)
            if globalIndexing:
                slab = self.getLocalSlab(staggerloc)[::-1]
                # Populate self.grid with coordinates or the bounds as needed
                ptr[:] = numpy.array(coords[self.ndims - i - 1]).T[slab]
            else:
                ptr[:] = numpy.array(coords[self.ndims - i - 1]).T[:]

    def getCoords(self, dim, staggerloc):
        """
        Return the coordinates for a dimension

        Parameters
        ----------
        dim : desired dimension (zero based indexing)

        staggerloc : Stagger location
        """
        gridPtr = self.grid.get_coords(coord_dim=dim, staggerloc=staggerloc)
        shp = self.getCoordShape(staggerloc)[::-1]
        return numpy.reshape(gridPtr, shp).T

    def setCellAreas(self, areas):
        """
        Set the cell areas

        Parameters
        ----------
        areas : numpy array

        """
        self.grid.add_item(item=ESMF.GridItem.Area)
        areaPtr = self.grid.get_item(
            item=ESMF.GridItem.AREA,
            staggerloc=self.staggerloc)
        areaPtr[:] = areas.T.flat
        self.cellAreasSet = True

    def getCellAreas(self):
        """
        Get Cell Areas

        Returns
        -------
        cell areas or None if setCellAreas was not called
        """
        if self.cellAreasSet:
            areaPtr = self.grid.get_item(
                item=ESMF.GridItem.AREA,
                staggerloc=self.staggerloc)
            return numpy.reshape(areaPtr, self.shape).T
        else:
            return None

    def getMask(self, staggerloc=CENTER):
        """
        Get mask array. In ESMF, the mask is applied to cells.

        Returns
        -------
        mask numpy array 1 is invalid by default

        Note
        ----
        This array exists on all procs
        """
        try:
            maskPtr = self.grid.get_item(
                item=ESMF.GridItem.MASK, staggerloc=staggerloc)
        except BaseException:
            maskPtr = None
        return maskPtr.T

    def setMask(self, mask, staggerloc=CENTER):
        """
        Set mask array. In ESMF, the mask is applied to cells.

        Returns
        -------
        mask numpy array 1 is invalid by default


        Notes
        -----
        This array exists on all procs


        """
        self.grid.add_item(item=ESMF.GridItem.MASK, staggerloc=staggerloc)
        maskPtr = self.grid.get_item(
            item=ESMF.GridItem.MASK,
            staggerloc=staggerloc)
        slab = self.getLocalSlab(CENTER)[::-1]
        maskPtr[:] = mask.T[slab]

    def __del__(self):
        self.grid.destroy()

##########################################################################


class EsmfStructField:
    """
    Structured field.

    Creator for structured ESMF Field

    Parameters
    ----------

             esmfGrid
                 instance of an ESMF

             name field
                  name (must be unique)

             datatype
                  data type, one of 'float64', 'float32', 'int64', or 'int32'
                  (or equivalent numpy dtype)

             staggerloc
                  ESMF.StaggerLoc.CENTER
                  ESMF.StaggerLoc.CORNER
    """

    def __init__(self, esmfGrid, name, datatype, staggerloc=CENTER):
        """

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

        mpi_disabled = getenv_bool("CDMS_NO_MPI", "False")

        try:
            # skip trying to load mpi4py module
            if mpi_disabled:
                raise Exception()

            from mpi4py import MPI
            self.comm = MPI.COMM_WORLD
        except BaseException:
            pass

        etype = None
        sdatatype = str(datatype)  # in case user passes a numpy dtype
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
            raise RegridError(msg)

        self.field = ESMF.Field(
            grid=esmfGrid.grid,
            name=name,
            typekind=etype,
            staggerloc=staggerloc)
        vm = ESMF.ESMP_VMGetGlobal()
        self.pe, self.nprocs = ESMF.ESMP_VMGet(vm)

    def getPointer(self):
        """
        Get field data as a flat array

        Returns
        -------
        flat array pointer.
        """
        return numpy.ravel(self.field.data)

    def getData(self, rootPe):
        """
        Get field data as a numpy array

        Parameters
        ----------
        rootPe : if None then local data will be fetched, otherwise gather the
                 data on processor "rootPe" (all other procs will return None).

        Returns
        -------
        numpy array or None.

        """
        ptr = self.getPointer()
        if rootPe is None:
            shp = self.grid.getCoordShape(staggerloc=self.staggerloc)[::-1]
            # local data, copy
            return numpy.reshape(ptr, shp).T
        else:
            # gather the data on rootPe
            lo, hi = self.grid.getLoHiBounds(self.staggerloc)
            los = [lo]
            his = [hi]
            ptrs = [ptr]
            ptr = numpy.reshape(ptr, hi)
            if self.comm is not None:
                los = self.comm.gather(lo)  # Local
                his = self.comm.gather(hi)  # Local
                ptrs = self.comm.gather(ptr, root=rootPe)

            if self.pe == rootPe:    # Local
                # reassemble, find the largest hi indices to set
                # the shape of the data container
                bigHi = [0 for i in range(self.grid.ndims)]
                for i in range(self.grid.ndims):
                    bigHi[i] = reduce(lambda x, y: max(x, y),
                                      [his[p][i] for p in range(self.nprocs)])
                # allocate space to retrieve the data
                bigData = numpy.empty(bigHi, ptr.dtype)
                bigData[:] = 0.0

            # populate the data
                for p in range(self.nprocs):
                    slab = tuple([slice(los[p][i], his[p][i], None) for
                                  i in range(self.grid.ndims)])
                    # copy
                    bigData[slab].flat = ptrs[p]
                return bigData.T         # Local

        # rootPe is not None and self.pe != rootPe
        return None

    def setLocalData(self, data, staggerloc, globalIndexing=False):
        """
        Set local field data

        Parameters
        ----------
        data : full numpy array, this method will take care of setting
               a the subset of the data that reside on the local processor

        staggerloc : stagger location of the data

        globalIndexing : if True array was allocated over global index space, array
                         was allocated over local index space (on this processor)
        """
        ptr = self.field.data
        if globalIndexing:
            slab = self.grid.getLocalSlab(staggerloc)[::-1]
            ptr[:] = data.T[slab]
        else:
            ptr[:] = data.T


##########################################################################

class EsmfRegrid:
    """
    Regrid source grid data to destination grid data

    Constuct regrid object

    Parameters
    ----------
    srcField :
        the source field object of type EsmfStructFields
    dstField :
        the destination field object of type EsmfStructField
    srcMaskValues :
        Value of masked cells in source
    dstMaskValues :
        Value of masked cells in destination
    srcFrac :
        Cell fractions on source grid (type EsmfStructField
    dstFrac :
        Cell fractions on destination grid (type EsmfStructField)
    regridMethod :
        ESMF.RegridMethod.{BILINEAR,CONSERVE,PATCH}
    unMappedAction :
        ESMF.UnmappedAction.{IGNORE,ERROR}
    ignoreDegenerate :
        Ignore degenerate cells when checking inputs
    """

    def __init__(self, srcField, dstField,
                 srcFrac=None,
                 dstFrac=None,
                 srcMaskValues=None,
                 dstMaskValues=None,
                 regridMethod=BILINEAR,
                 ignoreDegenerate=False,
                 unMappedAction=IGNORE):
        """

        """
        self.srcField = srcField
        self.dstField = dstField
        self.regridMethod = regridMethod
        self.srcAreaField = None
        self.dstAreaField = None
        self.srcFracField = srcFrac
        self.dstFracField = dstFrac
        self.regridHandle = None
        self.ignoreDegenerate = ignoreDegenerate

        timeStamp = re.sub('\.', '', str(time.time()))

        # create and initialize the cell areas to zero
        if regridMethod == CONSERVE:
            self.srcAreaField = EsmfStructField(self.srcField.grid,
                                                name='src_areas_%s' % timeStamp,
                                                datatype='float64',
                                                staggerloc=CENTER)
            dataPtr = self.srcAreaField.getPointer()
            dataPtr[:] = 0.0
            self.dstAreaField = EsmfStructField(self.dstField.grid,
                                                name='dst_areas_%s' % timeStamp,
                                                datatype='float64',
                                                staggerloc=CENTER)
            dataPtr = self.dstAreaField.getPointer()
            dataPtr[:] = 0.0

        # initialize fractional areas to 1 (unless supplied)
        if srcFrac is None:
            self.srcFracField = EsmfStructField(self.srcField.grid,
                                                name='src_cell_area_fractions_%s' % timeStamp,
                                                datatype='float64',
                                                staggerloc=CENTER)
            dataPtr = self.srcFracField.getPointer()
            dataPtr[:] = 1.0

        if dstFrac is None:
            self.dstFracField = EsmfStructField(self.dstField.grid,
                                                name='dst_cell_area_fractions_%s' % timeStamp,
                                                datatype='float64',
                                                staggerloc=CENTER)
            dataPtr = self.dstFracField.getPointer()
            dataPtr[:] = 1.0

        srcMaskValueArr = None
        if srcMaskValues is not None:
            srcMaskValueArr = numpy.array(srcMaskValues, dtype=numpy.int32)

        dstMaskValueArr = None
        if dstMaskValues is not None:
            dstMaskValueArr = numpy.array(dstMaskValues, dtype=numpy.int32)

        self.regridHandle = ESMF.Regrid(
            srcField.field,
            dstField.field,
            src_frac_field=self.srcFracField.field,
            dst_frac_field=self.dstFracField.field,
            src_mask_values=srcMaskValueArr,
            dst_mask_values=dstMaskValueArr,
            regrid_method=regridMethod,
            unmapped_action=unMappedAction,
            ignore_degenerate=self.ignoreDegenerate)

    def getSrcAreas(self, rootPe):
        """
        Get the src grid areas as used by conservative interpolation

        Parameters
        ----------
        rootPe : None is local areas are returned, otherwise provide rootPe and
                 the data will be gathered


        Returns
        -------
        numpy array or None if interpolation is not conservative
        """
        if self.srcAreaField is not None:
            return self.srcAreaField.data.T
        return None

    def getDstAreas(self, rootPe):
        """
        Get the dst grid areas as used by conservative interpolation

        Parameters
        ----------
        rootPe : None is local areas are returned, otherwise provide rootPe and the data will be gathered


        Returns
        -------
            numpy array or None if interpolation is not conservative
        """
        if self.srcAreaField is not None:
            return self.dstAreaField.data.T
        return None

    def getSrcAreaFractions(self, rootPe):
        """
        Get the source grid fraction areas as used by conservative interpolation

        Parameters
        ----------
        rootPe : None is local areas are returned, otherwise provide rootPe and the data will be gathered


        Returns
        -------
        numpy array
        """
        if self.srcFracField is not None:
            #            self.srcFracField.get_area()
            return self.srcFracField.data.T
        return None

    def getDstAreaFractions(self, rootPe):
        """
        Get the destination grid fraction areas as used by conservative interpolation

        Parameters
        ----------
        rootPe : None is local areas are returned, otherwise provide rootPe and the data will be gathered


        Returns
        -------
        numpy array
        """
        if self.dstFracField is not None:
            #            self.dstFracField.get_area()
            return self.dstFracField.data.T
        return None

    def __call__(self, srcField=None, dstField=None, zero_region=None):
        """
        Apply interpolation weights

        Parameters
        ----------

        srcField : source field (or None if src field passed to constructor is to be used)

        dstField : destination field (or None if dst field passed to constructor is to be used)

        zero_region : specify which region of the field indices will be zeroed (or None default
                      to TOTAL Region)
        """
        if srcField is None:
            srcField = self.srcField
        if dstField is None:
            dstField = self.dstField

        # default is keep the masked values intact
        zeroregion = ESMF.Region.SELECT
        if self.regridMethod == CONSERVE:
            zeroregion = None  # will initalize to zero

        self.regridHandle(
            srcfield=srcField.field,
            dstfield=dstField.field,
            zero_region=zeroregion)

    def __del__(self):
        if self.regridHandle is not None:
            self.regridHandle.destroy()
