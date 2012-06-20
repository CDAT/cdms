#/usr/bin/env python

"""
Regridding of curvilinear structured grids
Alex Pletzer and Dave Kindig, Tech-X (2011)
This code is provided with the hope that it will be useful.
No guarantee is provided whatsoever. Use at your own risk.
"""


# standard python includes
from re import search, sub
from ctypes import c_double, c_float, c_int, \
    c_char_p, CDLL, byref, POINTER
import ctypes
import operator
import sys
import os
import copy
import numpy
import cdms2
from regrid2 import RegridError

C_DOUBLE_P = POINTER(c_double)

# libcf
try:
    from pycf import libCFConfig, __path__
except:
    raise ImportError, 'Error: could not import pycf'

LIBCFDIR  = __path__[0] + "/pylibcf"

__FILE__ = sys._getframe().f_code.co_filename

def catchError(status, lineno):
    if status != 0:
        raise RegridError, "ERROR in %s: status = %d at line %d" \
            % (__FILE__, status, lineno)

def getTensorProduct(axis, dim, dims):
    """
    Convert an axis into a curvilinear coordinate by applying
    a tensor product
    @param axis 1D array of coordinates
    @param dim dimensional index of the above coordinate
    @param dims sizes of all coordinates
    @return coordinate values obtained by tensor product
    """
    return numpy.outer(numpy.outer( numpy.ones(dims[:dim], axis.dtype), axis),
                      numpy.ones(dims[dim+1:], axis.dtype)).reshape(dims)

def makeCurvilinear(coords):
    """
    Turn a mixture of axes and curvilinear coordinates into
    full curvilinear coordinates
    @param coords list of coordinates
    @return new list of coordinates and associated dimensions
    """
    rank = len(coords)

    count1DAxes = 0
    dims = []
    for i in range(rank):
        coord = coords[i]
        if len(coord.shape) == 1:
            # axis
            dims.append( len(coord) )
            count1DAxes += 1
        elif len(coord.shape) == rank:
            # fully curvilinear
            dims.append( coord.shape[i] )
        else:
            # assumption: all 1D axes preceed curvilinear
            # coordinates!!!
            dims.append( coord.shape[i - count1DAxes] )

    for i in range(rank):
        nd = len(coords[i].shape)
        if nd == rank:
            # already in curvilinear form, keep as is
            pass
        elif nd == 1:
            # it's an axis
            coords[i] = getTensorProduct(coords[i][:], i, dims)
        elif rank == 3 and nd == 2 and i > 0:
            # assume leading coordinate is an axis
            o1 = numpy.ones( (len(coords[0]),), coords[i].dtype )
            coords[i] = numpy.ma.outer(o1, coords[i]).reshape(dims)
        else:
            raise RegridError, \
                "ERROR in %s: funky mixture of axes and curvilinear coords %s" \
                % (__FILE__, str([x.shape for x in coords]))
    return coords, dims

def makeCoordsCyclic(coords, dims):
    """
    Make coordinates cyclic
    @params coords input coordinates
    @params dims input dimensions
    @return new, extended coordinates such that the longitudes cover the sphere
            and new dimensions
    """
    # assume lon is the last coordinate!!

    # check if already extended
    eps = 1.e-3

    # some models already overlap
    diff1 = abs(coords[-1][...,-2] - coords[-1][...,0])
    diff2 = abs(coords[-1][...,-2] - coords[-1][...,0] - 360.0)
    diff3 = abs(coords[-1][...,-2] - coords[-1][...,0] + 360.0)
    adiff = numpy.sum(numpy.minimum(diff1, numpy.minimum(diff2, diff3))) \
        / float(dims[-1])
    if adiff < eps:
        # cyclic, return input coordinates unchanged
        return coords, dims

    # some models are already periodic
    diff1 = abs(coords[-1][...,-1] - coords[-1][...,0])
    diff2 = abs(coords[-1][...,-1] - coords[-1][...,0] - 360.0)
    diff3 = abs(coords[-1][...,-1] - coords[-1][...,0] + 360.0)
    adiff = numpy.sum(numpy.minimum(diff1, numpy.minimum(diff2, diff3))) \
        / float(dims[-1])
    if adiff < eps:
        # cyclic, return input coordinates unchanged
        return coords, dims

    # make cyclic by appending a column to the coordinates
    newCoords = []
    newDims = list(copy.copy(dims))
    newDims[-1] += 1 # append to the right
    for i in range(len(coords)):
        newCoords.append( numpy.zeros( newDims, coords[i].dtype ) )
        newCoords[i][..., 0:-1] = coords[i][...]
        newCoords[i][...,   -1] = coords[i][...,  0]

    # add modulo term, want deltas ~ order of dlon otherwise add
    # or subtract a periodicity length
    nlon = dims[-1]
    dlon = 360.0 / float(nlon) # average resolution
    tol = 360.0 - min(5, nlon)*dlon
    mask1 = (newCoords[-1][..., -1] - newCoords[-1][..., -2] < -tol)
    mask2 = (newCoords[-1][..., -1] - newCoords[-1][..., -2] > +tol)
    newCoords[-1][..., -1] += 360.0*mask1
    newCoords[-1][..., -1] -= 360.0*mask2

    return newCoords, newDims

def checkForCoordCut(coords, dims):
    """
    Look for a cut in a coordinate system (e.g. tri-polar grid)
    Assume latitude is next to last coordinate and longitude is last coordinate!!!

    @params coords input coordinates
    @params dims input dimensions
    @return True for cut found
            False for no cut
    """

    # Assume latitude is next to last coordinate and longitude is last coordinate!!!

    rank = len(dims)
    if rank < 2:
        # print 'no cut: dims < 2'
        return False
    if len(coords[-2].shape) < 2:
        # Is the 'lat' coordinate an axis?
        return False

    nlat, nlon = dims[-2], dims[-1]
    lat = coords[-2]
    eps = 1.e-7

    # Check to see if the top row has already be dealt with by the modeling
    # agency. Last row is repeated in reverse.

    topRow = coords[-2][..., nlat-1, :]
    revTop = coords[-2][..., nlat-1, ::-1]
    nextRow = coords[-2][..., nlat-2, :]  # Reverse nextRow
    diffs = abs(revTop - nextRow)

    # If already accounted for all diffs are 0.
    if numpy.all(diffs < eps):
        # print "no cut: reversed"
        return False

    # Lon of max latitude -- Looking for a rotated pole
    maxLats = numpy.where(abs(lat - numpy.max(lat)) < eps)
    inTopRow = False
    if len(maxLats[0] > 0): inTopRow = numpy.all(maxLats[-2] == nlat-1)
    if not inTopRow:
        # The max lats are not in the top row. The cut may already be handled
        # print 'no cut: max lat not in top row.' + \
        #         'Either: it is a funky grid or rotated pole'
        return False

    # Only in top row.
    maxLatInd = lat[..., nlat-1, :].argmax()
    maxLonInd = lat[..., maxLatInd].argmax()
    rowOfMaxLat = lat[..., maxLonInd, :]
    diffs = rowOfMaxLat - topRow

    if diffs.max() != 0:
        # Rotated Pole
        # print "no cut: rotated pole"
        return False

    # Find locale minima.
    # A rotated pole grid has only one minimum. A tripolar grid should
    # have two, though they may not be at the same latitude

    minInds = numpy.where(abs(topRow - topRow.min()) < eps)
    if len(minInds[0]) > 2:
        # Account for the end points matching
        # Multiple minima in the top row
        return True

    # Now if we have an offset tri-pole. The extra poles are not at the same
    # latitude
    minCount = 0
    firstInd = topRow.argmin()
    diffs = numpy.diff(topRow)
    if firstInd == 0:
        if revTop.argmin() == 0:
            if topRow[firstInd] == revTop[0]: minCount += 1
    else:
        minCount += 1
        # Look for next Minima
    index = firstInd + 1
    while diffs[index] > 0:
        index += 1
        if index == nlon: break
    nextIndex = topRow[index+1:].argmin() + index+1
    if nextIndex != index+1 and nextIndex != nlon-1: minCount += 1
    if minCount == 1:
        # print "no cut: one pole"
        return False

    return True

def handleCoordsCut(coords, dims, bounds):
    """
    Generate connectivity across a cut. e.g. from a tri-polar grid.
    Assume latitude is next to last coordinate and longitude is last coordinate!!!

    @params coords input coordinates list of rank
    @params dims input dimensions
    @params bounds boundaries for each coordinate
    @return extended coordinates such that there is an extra row containing
            connectivity information across the cut
    """

    # Assume latitude is next to last coordinate and longitude is 
    # last coordinate!!!

    dims = coords[-2].shape
    rank = len(dims)
    nlat, nlon = dims[-2], dims[-1]

    epsExp = 3
    eps = 10**(-1*epsExp)

    # Add row to top with connectivity information. This means rearranging
    # the top row
    def getIndices(array, nlon, newI):
        """
        Find indices where a cell edge matches for two cells
        @param array Array of booleans
        @param nlon number of longitudes
        @param newI index row with connectivity to be updated
        @return new coordinates, new dimensions, index row
        """
        for i in range(len(array)):
            # An edge
            if len(numpy.where(array[i, :]==True)[0]) >= 2:
                if newI[i] < 0: newI[i] = (nlon-1) - i
                if newI[(nlon-1)-i] < 0: newI[(nlon-1)-i] = i

    lonb = bounds[-1][..., nlat-1, ...]
    latb = bounds[-2][..., nlat-1, ...]

    # Assume mkCyclic == True
    newI = numpy.arange(nlon-1, -1, -1)-1
    newI[nlon-1] = 0 #  Complete the rotation

    # Build new coordinate array and adjust dims
    newCoords = []
    newDims = list(copy.copy(dims))
    newDims[-2] += 1

    for i in range(len(coords)):
        nD = len(dims)
        newCoords.append( numpy.zeros( newDims, coords[i].dtype ) )
        newCoords[i][..., 0:dims[-2], :] = coords[i][...]
        newCoords[i][..., dims[-2], :] = coords[i][..., dims[-2]-1, newI]

    return newCoords, newDims, newI

class Regrid:

    def __init__(self, src_grid, dst_grid, src_bounds=None, mkCyclic=False,
                 handleCut=False, diagnostics=False):
        """
        Constructor

        @param src_grid source grid, a list of [x, y, ...] coordinates
                        or a cdms2.grid.Transient
        @param dst_grid destination grid, a list of [x, y, ...] coordinates
        @param src_bounds list of cell bounding coordinates (to be used when 
                          handling a cut in coordinates)
        @param mkCyclic Add a column to the right side of the grid to complete
               a cyclic grid
        @param handleCut Add a row to the top of grid to handle a cut for
               grids such as the tri-polar grid
        @param diagnostics print diagnostic messages
        @note the grid coordinates can either be axes (rectilinear grid) or
              n-dimensional for curvilinear grids. Rectilinear grids will
              be converted to curvilinear grids.
        """
        self.regridid = c_int(-1)
        self.src_gridid = c_int(-1)
        self.dst_gridid = c_int(-1)
        self.rank = 0
        self.src_dims = []
        self.dst_dims = []
        self.src_coords = []
        self.dst_coords = []
        self.lib = None
        self.extendedGrid = False
        self.handleCut = False
        self.dst_Index = []
        self.diagnostics = diagnostics
        self.weightsComputed = False
        self.maskSet = False

        # Open the shaped library
        dynLibFound = False
        for sosuffix in '.dylib', '.dll', '.DLL', '.so', '.a':
	    if os.path.exists(LIBCFDIR + sosuffix):
                dynLibFound = True
            	try:
                    self.lib = CDLL(LIBCFDIR + sosuffix)
                    break
                except:
                    pass
        if self.lib == None:
            if not dynLibFound:
 	        raise RegridError, "ERROR in %s: could not find shared library %s.{so,dylib,dll,DLL}" \
                % (__FILE__, LIBCFDIR)
            raise RegridError, "ERROR in %s: could not open shared library %s.{so,dylib,dll,DLL}" \
                % (__FILE__, LIBCFDIR)

        # Number of space dimensions
        self.rank = len(src_grid)

        if len(dst_grid) != self.rank:
            raise RegridError, "ERROR in %s: len(dst_grid) = %d != %d" \
                % (__FILE__, len(dst_grid), self.rank)

        if self.rank <= 0:
            raise RegridError, \
                "ERROR in %s: must have at least one dimension, rank = %d" \
                % (__FILE__, self.rank)

        # Convert src_grid/dst_grid to curvilinear grid, if need be
        if self.rank > 1:
            src_grid, src_dims = makeCurvilinear(src_grid)
            dst_grid, dst_dims = makeCurvilinear(dst_grid)

        # Make sure coordinates wrap around if mkCyclic is True
        if mkCyclic:
            src_gridNew, src_dimsNew = makeCoordsCyclic(src_grid, src_dims)
            if self.diagnostics:
                aa, bb = str(src_dims), str(src_dimsNew)
                print '...  src_dims = %s, after making cyclic src_dimsNew = %s' \
                    % (aa, bb)
                for i in range(self.rank):
                    print '...... src_gridNew[%d].shape = %s' \
                        % (i, str(src_gridNew[i].shape))
            # flag indicating that the grid was extended
            if reduce(lambda x, y:x+y, \
                          [src_dimsNew[i] - src_dims[i] \
                               for i in range(self.rank)]) > 0:
                self.extendedGrid = True
            # reset
            src_grid = src_gridNew
            src_dims = src_dimsNew

        # Handle a cut in the coordinate system. Run after mkCyclic.
        # e.g. a tri-polar grid
        if handleCut and src_bounds is not None:
            # Test for the presence of a cut.
            isCut = checkForCoordCut(src_grid, src_dims)
            if isCut:
                # No cut
                src_gridNew, src_dimsNew, dst_Index = handleCoordsCut(src_grid,
                                                     src_dims, src_bounds)
                if dst_Index is not None:
                    self.handleCut = True
                    self.extendedGrid = self.extendedGrid
                else:
                    self.handleCut = False
                    self.extendedGrid = self.extendedGrid
                if self.diagnostics:
                    aa, bb = str(src_dims), str(src_dimsNew)
                    print '...  src_dims = %s, after making cyclic src_dimsNew = %s' \
                        % (aa, bb)
                src_grid = src_gridNew
                src_dims = src_dimsNew
                self.dst_Index = dst_Index

        self.src_dims = (c_int * self.rank)()
        self.dst_dims = (c_int * self.rank)()

        # Build coordinate objects
        src_dimnames = (c_char_p * self.rank)()
        dst_dimnames = (c_char_p * self.rank)()
        for i in range(self.rank):
            src_dimnames[i] = 'src_n%d' % i
            dst_dimnames[i] = 'dst_n%d' % i
            self.src_dims[i] = src_dims[i]
            self.dst_dims[i] = dst_dims[i]
        self.src_coordids = (c_int * self.rank)()
        self.dst_coordids = (c_int * self.rank)()
        save = 0
        standard_name = ""
        units = ""
        coordid = c_int(-1)
        for i in range(self.rank):
            data =  numpy.array( src_grid[i], numpy.float64 )
            self.src_coords.append( data )
            dataPtr = data.ctypes.data_as(C_DOUBLE_P)
            name = "src_coord%d" % i
            # assume [lev,] lat, lon ordering
            if i == self.rank - 2:
                standard_name = 'latitude'
                units = 'degrees_north'
            elif i == self.rank - 1:
                standard_name = 'longitude'
                units = 'degrees_east'
            status = self.lib.nccf_def_coord(self.rank, self.src_dims,
                                             src_dimnames,
                                             dataPtr, save, name,
                                             standard_name, units,
                                             byref(coordid))
            catchError(status, sys._getframe().f_lineno)
            self.src_coordids[i] = coordid

            data =  numpy.array( dst_grid[i], numpy.float64 )
            self.dst_coords.append( data )
            dataPtr = data.ctypes.data_as(C_DOUBLE_P)
            name = "dst_coord%d" % i
            status = self.lib.nccf_def_coord(self.rank, self.dst_dims,
                                             dst_dimnames,
                                             dataPtr, save, name,
                                             standard_name, units,
                                             byref(coordid))
            catchError(status, sys._getframe().f_lineno)
            self.dst_coordids[i] = coordid
         
        # Build grid objects
        status = self.lib.nccf_def_grid(self.src_coordids, "src_grid",
                                        byref(self.src_gridid))
        catchError(status, sys._getframe().f_lineno)

        status = self.lib.nccf_def_grid(self.dst_coordids, "dst_grid",
                                        byref(self.dst_gridid))
        catchError(status, sys._getframe().f_lineno)

        # Create regrid object
        status = self.lib.nccf_def_regrid(self.src_gridid, self.dst_gridid,
                                          byref(self.regridid))
        catchError(status, sys._getframe().f_lineno)

    def getPeriodicities(self):
        """
        Get the periodicity lengths of the coordinates
        @return numpy array, values inf indicate no periodicity
        """
        coord_periodicity = numpy.zeros( (self.rank,), numpy.float64 )
        status = self.lib.nccf_inq_grid_periodicity(self.src_gridid,
                                 coord_periodicity.ctypes.data_as(C_DOUBLE_P))
        catchError(status, sys._getframe().f_lineno)
        return coord_periodicity

    def __del__(self):
        """
        Destructor, will be called automatically
        """
        status = self.lib.nccf_free_regrid(self.regridid)
        catchError(status, sys._getframe().f_lineno)

        status = self.lib.nccf_free_grid(self.src_gridid)
        catchError(status, sys._getframe().f_lineno)

        status = self.lib.nccf_free_grid(self.dst_gridid)
        catchError(status, sys._getframe().f_lineno)

        for i in range(self.rank):

            status = self.lib.nccf_free_coord(self.src_coordids[i])
            catchError(status, sys._getframe().f_lineno)

            status = self.lib.nccf_free_coord(self.dst_coordids[i])
            catchError(status, sys._getframe().f_lineno)

    def setValidMask(self, inMask):
        """
        Set valid mask array for the grid
        @param inMask flat numpy array of type numpy.int32 or a valid cdms2 variable
                    with its mask set. 
                    0 - invalid, 1 - valid data
        @note This must be invoked before computing the weights, the 
        mask is a property of the grid (not the data).
        """
        if self.weightsComputed:
            raise RegridError, 'Must set mask before computing weights'
    
        mask = numpy.array(inMask, dtype = numpy.int32)
    
        # extend src data if grid was made cyclic and or had a cut accounted for
        newMask = self._extend(mask)
        c_intmask = newMask.ctypes.data_as(POINTER(c_int))
        status = self.lib.nccf_set_grid_validmask(self.src_gridid,
                                                  c_intmask)
        catchError(status, sys._getframe().f_lineno)
        self.maskSet = True

    def setMask(self, inDataOrMask):
        """
        Set mask array. The mask is defined for nodes
        @param inDataOrMask cdms2 array or flat mask array, 
                                0 - valid data
                                1 - invalid data      
        @note this definition is compatible with the numpy masked arrays
        @note see setValidMask for the opposite definition 
        @note should be called before computing the weights
        """
        mask = None
        if hasattr(inDataOrMask, 'getmask'):
            # cdms2 variable
            mask = inDataOrMask.getmask()
        else:
            # flat mask array
            mask = inDataOrMask
        # reversing the meaning 1 == valid, 0 == invalid
        mask = 1 - numpy.array(inDataOrMask, dtype = numpy.int32)
        # now calling our own mask setter
        self.setValidMask(mask)

    def computeWeights(self, nitermax=100, tolpos=1.e-2):
        """
        Compute the the interpolation weights

        @param nitermax max number of iterations
        @param tolpos max tolerance when locating destination positions in
               index space
        """
        status = self.lib.nccf_compute_regrid_weights(self.regridid,
                                                      nitermax,
                                                      c_double(tolpos))
        catchError(status, sys._getframe().f_lineno)
        self.weightsComputed = True

    def apply(self, src_data_in, dst_data, missingValue = None):
        """
        Apply interpolation
        @param src_data data on source grid
        @param dst_data data on destination grid
        @param missingValue value that should be set for points falling outside the src domain, 
                            pass None if these should not be touched.
        """
        if not self.weightsComputed:
            raise RegridError, 'Weights must be set before applying the regrid'
        # extend src data if grid was made cyclic and or had a cut accounted for
        src_data = self._extend(src_data_in)

        # Check
        if reduce(operator.iand, [src_data.shape[i] == self.src_dims[i] \
                                 for i in range(self.rank)]) == False:
            raise RegridError, ("ERROR in %s: supplied src_data have wrong shape " \
                                  + "%s != %s") % (__FILE__, str(src_data.shape), \
                                     str(tuple([d for d in self.src_dims])))
        if reduce(operator.iand, [dst_data.shape[i] == self.dst_dims[i] \
                                 for i in range(self.rank)]) == False:
            raise RegridError, ("ERROR ins: supplied dst_data have wrong shape " \
                + "%s != %s") % (__FILE__, str(dst_data.shape),
                                 str(self.dst_dims))

        # Create temporary data objects
        src_dataid = c_int(-1)
        dst_dataid = c_int(-1)
        save = 0
        standard_name = ""
        units = ""
        time_dimname = ""

        status = self.lib.nccf_def_data(self.src_gridid, "src_data", \
                                        standard_name, units, time_dimname, \
                                        byref(src_dataid))
        catchError(status, sys._getframe().f_lineno)

        if src_data.dtype != dst_data.dtype:
            raise RegridError, "ERROR in %s: mismatch in src and dst data types (%s vs %s)" \
                % (__FILE__, src_data.dtype, dst_data.dtype)

        # only float64 and float32 data types are supported for interpolation
        if src_data.dtype == numpy.float64:
            fill_value = c_double(libCFConfig.NC_FILL_DOUBLE)
            if missingValue is not None:
                fill_value = c_double(missingValue)
            ptr = src_data.ctypes.data_as(POINTER(c_double))
            status = self.lib.nccf_set_data_double(src_dataid, ptr, save, fill_value)
            catchError(status, sys._getframe().f_lineno)
        elif src_data.dtype == numpy.float32:
            fill_value = c_float(libCFConfig.NC_FILL_FLOAT)
            if missingValue is not None:
                fill_value = c_float(missingValue)
            ptr = src_data.ctypes.data_as(POINTER(c_float))
            status = self.lib.nccf_set_data_float(src_dataid, ptr, save, fill_value)
            catchError(status, sys._getframe().f_lineno)
        else:
            raise RegridError, "ERROR in %s: invalid src_data type %s (neither float nor double)" \
                % (__FILE__, src_data.dtype)

        status = self.lib.nccf_def_data(self.dst_gridid, "dst_data", \
                                        standard_name, units, time_dimname, \
                                            byref(dst_dataid))
        catchError(status, sys._getframe().f_lineno)
        if dst_data.dtype == numpy.float64:
            fill_value = c_double(libCFConfig.NC_FILL_DOUBLE)
            if missingValue is not None:
                fill_value = c_double(missingValue)
                dst_data[:] = missingValue
            ptr = dst_data.ctypes.data_as(POINTER(c_double))
            status = self.lib.nccf_set_data_double(dst_dataid, ptr, save, fill_value)
            catchError(status, sys._getframe().f_lineno)
        elif dst_data.dtype == numpy.float32:
            fill_value = c_float(libCFConfig.NC_FILL_FLOAT)
            if missingValue is not None:
                fill_value = c_float(missingValue)
                dst_data[:] = missingValue
            ptr = dst_data.ctypes.data_as(POINTER(c_float))
            status = self.lib.nccf_set_data_float(dst_dataid, ptr, save, fill_value)
            catchError(status, sys._getframe().f_lineno)
        else:
            raise RegridError, "ERROR in %s: invalid dst_data type = %s" \
                % (__FILE__, dst_data.dtype)

        # Now apply weights
        status = self.lib.nccf_apply_regrid(self.regridid, src_dataid, dst_dataid)
        catchError(status, sys._getframe().f_lineno)
        
        # Clean up
        status = self.lib.nccf_free_data(src_dataid)
        catchError(status, sys._getframe().f_lineno)
        status = self.lib.nccf_free_data(dst_dataid)
        catchError(status, sys._getframe().f_lineno)

        return dst_data

    def __call__(self, src_data, dst_data, missingValue = None):
        """
        Apply interpolation (synonymous to apply method)
        @param src_data data on source grid
        @param dst_data data on destination grid
        @param missingValue value that should be set for points falling outside the src domain, 
                            pass None if these should not be touched.
        """
        self.apply(src_data, dst_data, missingValue)


    def getNumValid(self):
        """
        Return the number of valid destination points. Destination points
        falling outside the source domain, more gnerally, points which
        could not be located on the source grid, reduce the number of
        valid points.
        @return number of points
        """
        res = c_int(-1)
        status = self.lib.nccf_inq_regrid_nvalid(self.regridid,
                                                 byref(res))
        catchError(status, sys._getframe().f_lineno)
        return res.value

    def getNumDstPoints(self):
        """
        Return the number of points on the destination grid
        @return number of points
        """
        res = c_int(-1)
        status = self.lib.nccf_inq_regrid_ntargets(self.regridid,
                                                  byref(res))
        catchError(status, sys._getframe().f_lineno)
        return res.value

    def getSrcGrid(self):
        """
        Return the source grid
        @return grid
        """
        return self.src_coords

    def getDstGrid(self):
        """
        Return the destination grid
        @return grid
        """
        return self.dst_coords

    def getIndicesAndWeights(self, dst_indices):
        """
        Get the indices and weights for a single target location
        @param dst_indices index set on the target grid
        @return [index sets on original grid, weights]
        """
        dinds = numpy.array(dst_indices)
        sinds = (c_int * 2**self.rank)()
        weights = numpy.zeros( (2**self.rank,), numpy.float64 )
        status = self.lib.nccf_inq_regrid_weights(self.regridid,
                                                  dinds.ctypes.data_as(POINTER(c_double)),
                                                  sinds,
                                                  weights.ctypes.data_as(POINTER(c_double)))
        catchError(status, sys._getframe().f_lineno)
        # convert the flat indices to index sets
        ori_inds = []
        for i in range(2**self.rank):
            inx = numpy.zeros( (self.rank,), numpy.int32 )
            self.lib.nccf_get_multi_index(self.rank, self.src_dims,
                                          sinds[i],
                                          inx.ctypes.data_as(POINTER(c_int)))
            ori_inds.append(inx)

        return ori_inds, weights

    def _extend(self, src_data):
        """
        Extend the data by padding a column and a row, depending on whether the
        grid was made cyclic and a fold was added or not
        @param src_data input source data
        @return extended source data (or source input data of no padding was applied)
        """

        # extended dimensions
        nlatX, nlonX = self.src_dims[-2], self.src_dims[-1]
        # original dimensions, before extension
        # assuming ..., lat, lon ordering
        nlat, nlon = src_data.shape[-2:]

        # no cut and no cyclic extension
        src_dataNew = src_data

        if self.handleCut or self.extendedGrid:
            # copy data into new, extended container
            src_dataNew = numpy.zeros(self.src_dims, src_data.dtype)
            # start filling in...
            src_dataNew[..., :nlat, :nlon] = src_data[...]

        if self.handleCut:
            # fill in polar cut (e.g. tripolar cut), top row
            # self.dst_Index[i] knows how to fold
            for i in range(nlon):
                src_dataNew[..., -1, i] = src_data[..., -2, self.dst_Index[i]]

        if self.extendedGrid:
            # make data periodic in longitudes
            src_dataNew[..., -1] = src_dataNew[..., 0]

        return src_dataNew

    def _findIndices(self, targetPos, nitermax, tolpos,
                     dindicesGuess):
        """
        Find the floating point indices
        @param targetPos numpy array of target positions
        @param nitermax max number of iterations
        @param tolpos max toelrance in positions
        @param dindicesGuess guess for the floating point indices
        @return indices, number of iterations, achieved tolerance
        """
        posPtr = targetPos.ctypes.data_as(POINTER(c_double))
        adjustFunc = None
        hit_bounds = numpy.zeros((self.rank),
                                  dtype = int).ctypes.data_as(POINTER(c_int))
        # no periodicity
        coord_periodicity = float('inf') * numpy.ones((self.rank), targetPos.dtype)
        coord_periodicity_ptr = coord_periodicity.ctypes.data_as(POINTER(c_double))
        res = copy.copy(dindicesGuess)
        resPtr = res.ctypes.data_as(POINTER(c_double))
        src_coords = (POINTER(c_double) * self.rank)()
        niter = c_int(nitermax)
        tol = c_double(tolpos)
        for i in range(self.rank):
            ptr = self.src_coords[i].ctypes.data_as(POINTER(c_double))
            src_coords[i] = ptr
        status = self.lib.nccf_find_indices_double(self.rank,
                                                   self.src_dims,
                                                   src_coords,
                                                   coord_periodicity_ptr,
                                                   posPtr,
                                                   byref(niter),
                                                   byref(tol),
                                                   adjustFunc,
                                                   resPtr,
                                                   hit_bounds)
        catchError(status, sys._getframe().f_lineno)
        return resPtr.contents.value, niter.value, tol.value

######################################################################

def testMakeCyclic():

    y = numpy.array([-90.0 + i*30.0 for i in range(7)])
    x = numpy.array([(i+0.5)*60.0 for i in range(6)])
    yy = getTensorProduct(y, 0, [len(y), len(x)])
    xx = getTensorProduct(x, 1, [len(y), len(x)])
    coords = [yy, xx]
    dims = [len(y), len(x)]
    newCoords, newDims = makeCoordsCyclic(coords, dims)
#    print 'cyclic lats'
#    print newCoords[0]
#    print 'cyclic lons'
#    print newCoords[1]

def testHandleCut():

    # Need tripolar grid
    import cdms2
    filename = "data/so_Omon_GFDL-ESM2M_1pctCO2_r1i1p2_000101-000512_2timesteps.nc"
    f = cdms2.open(filename)
    if not f: return

    so = f.variables['so'][0, 0, :, :]
    if 'lon' in f.variables.keys():
        alllat = f.variables['lat']
        alllon = f.variables['lon']
    else:
        alllat = f.getAxis("lat").getData()
        alllon = f.getAxis("lon").getData()

    bounds = [f.variables['bounds_lon'][:].data,
              f.variables['bounds_lat'][:].data]
    coords = [alllat[:].data, alllon[:].data]
    dims = alllat.shape
    newCoords, newDims = makeCoordsCyclic(coords, dims)
    newCoords, newDims = handleCoordsCut(newCoords, newDims, bounds)

def testOuterProduct():

    # 2d
    x = numpy.array([1, 2, 3, 4])
    y = numpy.array([10, 20, 30])
    xx = getTensorProduct(x, 0, [len(x), len(y)])
    yy = getTensorProduct(y, 1, [len(x), len(y)])

    # 3d
    z = numpy.array([100, 200])

    #Mixed coordinates and axes

    aa = makeCurvilinear([z, yy, xx])
#    for g in aa:
#        print g


def test():
    def func1(coords):
        return coords[0]*coords[1] + coords[2]
    def func2(coords):
        return coords[0] * coords[1]

    # source grid, tensor product of axes
    src_x = numpy.array([1, 2, 3, 4, 5, 6])
    src_y = numpy.array([10, 20, 30, 40, 50])
    src_z = numpy.array([100, 200])

    # destination grid, product of axes
    dst_x = numpy.array([1.5, 2.0, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5])
    dst_y = numpy.array([15., 20., 25., 30., 40.])
    dst_z = numpy.array([120.0, 180.0, 240.])

    # regridding constructor
    rg = Regrid([src_x, src_y, src_z],
                [dst_x, dst_y, dst_z])
#    rg = Regrid([src_x, src_y],
#                [dst_x, dst_y])

    initialIndexGuess = numpy.array([0.0, 0.0, 0.0])
    indices = rg._findIndices(numpy.array([1.5, 18.0, 140.0]),
                              20, 1.e-2, initialIndexGuess)

    maxNumIters = 20
    posTol = 1.e-3
    rg.computeWeights(maxNumIters, posTol)

    # number of valid points (some destination points may fall 
    # outside the domain)
    nvalid = rg.getNumValid()

    # number of destination points
    ndstpts = rg.getNumDstPoints()
    print 'nvalid = ', nvalid, ' ndstpts = ', ndstpts

    # get the indices and weights for a single target location
    dst_indices = [4, 2, 1]
    inds, weights = rg.getIndicesAndWeights(dst_indices)
    print 'indices and weights are: ', inds, weights

    # data
    src_coords = rg.getSrcGrid()
    dst_coords = rg.getDstGrid()
    #print 'src_coords = ', src_coords
    #print 'dst_coords = ', dst_coords
    src_data = numpy.array( func1(src_coords), numpy.float32 )
    dst_data = -numpy.ones( dst_coords[0].shape, numpy.float32 )

    # regrid
    rg(src_data, dst_data)
    print 'after interp: dst_data = ', dst_data

    # check
    error = numpy.sum(abs(dst_data - func1(dst_coords)))
    #print dst_data
    #print func(dst_coords)
    print 'error = ', error

def testMasking():
    import numpy.ma as ma

    def func1(coords):
        return coords[0]*coords[1]
    def func2(coords):
        return coords[0] * coords[1]

    # source grid, tensor product of axes
    src_x = ma.masked_array([1, 2, 3, 4, 5, 6], mask = [0,0,1,0,0,0])
    src_y = ma.masked_array([10, 20, 30, 40, 50],mask = [0,0,0,1,0])

    # destination grid, product of axes
    dst_x = numpy.array([0.5,1,1.5, 2.0, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5,8.5,9.5])
    dst_y = numpy.array([15., 20., 25., 30., 35.,40.,45.,50.,55])

    # regridding constructor
    rg = Regrid([src_x, src_y],
                [dst_x, dst_y])

    initialIndexGuess = numpy.array([0.0, 0.0, 0.0])
    indices = rg._findIndices(numpy.array([1.5, 18.0, 140.0]),
                              20, 1.e-2, initialIndexGuess)

    # Mask needs to be set before weights are computed
    mask = rg.getSrcGrid()[0] == 3
    mask[:,3] = True
    rg.setValidMask(mask)
    rg.setMask(mask)
    maxNumIters = 20
    posTol = 1.e-2
    rg.computeWeights(maxNumIters, posTol)

    # number of valid points (some destination points may fall 
    # outside the domain)
    nvalid = rg.getNumValid()

    # number of destination points
    ndstpts = rg.getNumDstPoints()
    print 'nvalid = ', nvalid, ' ndstpts = ', ndstpts

    # get the indices and weights for a single target location
    dst_indices = [4, 2, 1]
    inds, weights = rg.getIndicesAndWeights(dst_indices)
    print 'indices and weights are: ', inds, weights

    # data
    src_coords = rg.getSrcGrid()
    dst_coords = rg.getDstGrid()
    #print 'src_coords = ', src_coords
    #print 'dst_coords = ', dst_coords
    src_data = numpy.array( func1(src_coords), numpy.float32 )
    dst_data = -numpy.ones( dst_coords[0].shape, numpy.float32 )

    # regrid
    rg(src_data, dst_data)
    print 'after interp: dst_data =\n', dst_data

    # check
    error = numpy.sum(abs(dst_data - func1(dst_coords)))
    #print dst_data
    #print func(dst_coords)
    print 'error = ', error

if __name__ == '__main__':
    #testOuterProduct()
    test()
    testMasking()
    #testMakeCyclic()
    #testHandleCut()

