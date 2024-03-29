"""
CDMS Axis objects
"""

from future import standard_library
import sys
import types
import copy
import numpy
# import regrid2._regrid
from . import cdmsNode
import cdtime
from . import cdmsobj
from .cdmsobj import CdmsObj, Max32int
from .sliceut import reverseSlice, splitSlice, splitSliceExt
from .error import CDMSError
from . import forecast
from .util import base_doc
# import warnings
from six import string_types
standard_library.install_aliases()
from collections import UserList  # noqa
_debug = 0
std_axis_attributes = ['name', 'units', 'length', 'values', 'bounds']


class AliasList (UserList):
    """AliasList.
    """

    def __init__(self, alist):
        """__init__.

        Parameters
        ----------
        alist :
            alist
        """
        UserList.__init__(self, alist)

    def __setitem__(self, i, value):
        """__setitem__.

        Parameters
        ----------
        i :
            i
        value :
            value
        """
        self.data[i] = value.lower()

    def __setslice(self, i, j, values):
        """__setslice.

        Parameters
        ----------
        i :
            i
        j :
            j
        values :
            values
        """
        self.data[i:j] = [x.lower() for x in values]

    def append(self, value):
        """append.

        Parameters
        ----------
        value :
            value
        """
        self.data.append(value.lower())

    def extend(self, values):
        """extend.

        Parameters
        ----------
        values :
            values
        """
        self.data.extend(list(map(str.lower, values)))


level_aliases = AliasList(['plev'])
longitude_aliases = AliasList([])
latitude_aliases = AliasList([])
time_aliases = AliasList([])
forecast_aliases = AliasList([])

FileWasClosed = "File was closed for object: "
InvalidBoundsArray = "Invalid boundary array: "
InvalidCalendar = "Invalid calendar: %i"
MethodNotImplemented = "Method not yet implemented"
ReadOnlyAxis = "Axis is read-only: "

# mf 20010402 -- prevent user from going beyond N cycles
InvalidNCycles = "Invalid number of cycles requested for wrapped dimension: "

ComptimeType = type(cdtime.comptime(0))
ReltimeType = type(cdtime.reltime(0, "days"))
CdtimeTypes = (ComptimeType, ReltimeType)

# Map between cdtime calendar and CF tags
calendarToTag = {
    cdtime.MixedCalendar: 'gregorian',
    cdtime.NoLeapCalendar: 'noleap',
    cdtime.GregorianCalendar: 'proleptic_gregorian',
    cdtime.JulianCalendar: 'julian',
    cdtime.Calendar360: '360_day',
    cdtime.ClimCalendar: 'clim_noncf',
    cdtime.ClimLeapCalendar: 'climleap_noncf',
    cdtime.DefaultCalendar: 'gregorian',
    cdtime.StandardCalendar: 'proleptic_gregorian',
}

tagToCalendar = {
    'gregorian': cdtime.MixedCalendar,
    'standard': cdtime.GregorianCalendar,
    'noleap': cdtime.NoLeapCalendar,
    'julian': cdtime.JulianCalendar,
    'proleptic_gregorian': cdtime.GregorianCalendar,
    '360_day': cdtime.Calendar360,
    '360': cdtime.Calendar360,
    '365_day': cdtime.NoLeapCalendar,
    'clim': cdtime.ClimCalendar,
    'clim_noncf': cdtime.ClimCalendar,
    'climleap_noncf': cdtime.ClimLeapCalendar,
    'climleap': cdtime.ClimLeapCalendar,
}

# This is not an error message, it is used to detect which things have
# been left as default indices or coordinates.
unspecified = "No value specified."

# Automatically generate axis and grid boundaries in getBounds
_autobounds = 2
# (for 1D lat/lon axes only.)
# Modes:
# 0 : off (not bounds generation)
# 1 : on  (generate bounds)
# 2 : grid (generate bounds for lat/lon
# grids only)

# Set autobounds mode to 'on' or 'off'. If on, getBounds will automatically
# generate boundary information for an axis or grid, if not explicitly defined.
# If 'off', and no boundary data is explicitly defined, the bounds will NOT
# be generated; getBounds will return None for the boundaries.


def setAutoBounds(mode):
    """Sets AutoBounds behavior.

    Automatically generates axis and grid boundaries when ``getBounds``
    is called.

    Parameters
    ----------
    mode : (str/int)
        0 : 'off'   (No bounds will be generated)
        1 : 'on'    (Generate bounds)
        2 : 'grid'  (Generate bounds for lat/lon grids only)

    Notes
    -----
    This only affects 1D axes.

    """
    global _autobounds
    if mode == 'on' or mode == 1:
        _autobounds = 1
    elif mode == 'off' or mode == 0:
        _autobounds = 0
    elif mode == 'grid' or mode == 2:
        _autobounds = 2


def getAutoBounds():
    """Gets AutoBounds mode.

    See ``setAutoBounds`` for description of modes.
    """
    return _autobounds

# Create a transient axis


def createAxis(data, bounds=None, id=None, copy=0, genericBounds=False):
    """ Creates an axis.

    To enabled automatic bounds generation see ``setAutoBounds``.

    Parameters
    ----------
    data : (list/:obj:`numpy.ndarray`)
        Values for axis.
    bounds : ``numpy.ndarray``
        2D array containing boundaries for ``data``.
    id : str
        Axis identifier.
    copy : int
        0: Stores reference of data.
        1: Stores copy of data.
    genericBounds : bool
        True will create generic bounds if ``bounds`` is None.

    Returns
    -------
    cdms2.TransientAxis
        Returns a ``TransientAxis`` containing data.
    """
    return TransientAxis(data, bounds=bounds, id=id,
                         copy=copy, genericBounds=genericBounds)

# Generate a Gaussian latitude axis, north-to-south


def createGaussianAxis(nlat):
    """Creates Guassian Axis.

    Parameters
    ----------
    nlat : int
        Number of latitudes to generate.

    Returns
    ------
    cdms2.TransientAxis
        ``TransientaAxis`` containing guassian axis of ``nlat``.
    """
    import regrid2._regrid

    lats, wts, bnds = regrid2._regrid.gridattr(nlat, 'gaussian')

    # For odd number of latitudes, gridattr returns 0 in the second half of
    # lats
    if nlat % 2:
        mid = int(nlat / 2)
        lats[mid + 1:] = -lats[:mid][::-1]

    latBounds = numpy.zeros((nlat, 2), numpy.float)
    latBounds[:, 0] = bnds[:-1]
    latBounds[:, 1] = bnds[1:]
    lat = createAxis(lats, latBounds, id="latitude")
    lat.designateLatitude()
    lat.units = "degrees_north"
    return lat

# Generate an equal-area latitude axis, north-to-south


def createEqualAreaAxis(nlat):
    """Creates an equal area axis.

    Parameters
    ----------
    nlat : int
        Number of latitudes to generate.

    Returns
    -------
    cdms2.TransientAxis
        ``TransientAxis`` containing equal area axis of ``nlat``.
    """
    import regrid2._regrid

    lats, wts, bnds = regrid2._regrid.gridattr(nlat, 'equalarea')
    latBounds = numpy.zeros((nlat, 2), numpy.float)
    latBounds[:, 0] = bnds[:-1]
    latBounds[:, 1] = bnds[1:]
    lat = createAxis(lats, latBounds, id="latitude")
    lat.designateLatitude()
    lat.units = "degrees_north"
    return lat

# Generate a uniform latitude axis


def createUniformLatitudeAxis(startLat, nlat, deltaLat):
    """Creates a uniform latitude axis.

    Parameters
    ----------
    startLat : float
        Starting latitude value.
    nlat :
        Number of latitudes.
    deltaLat : float
        Difference between each latitude point.

    Returns
    -------
    cdms2.TransientAxis
        ``TransientAxis`` containing uniform latitude axis.
    """
    latArray = startLat + deltaLat * numpy.arange(nlat)
    lat = createAxis(latArray, id="latitude")
    lat.designateLatitude()
    lat.units = "degrees_north"
    latBounds = lat.genGenericBounds(width=deltaLat)
    lat.setBounds(latBounds)
    return lat

# Generate a uniform longitude axis


def createUniformLongitudeAxis(startLon, nlon, deltaLon):
    """Creates a uniform longitude axis.

    Parameters
    ----------
    startLon : float
        Starting longitude value.
    nlon : int
        Number of longitudes.
    deltaLon : float
        Difference between each longitude point.

    Returns
    -------
    cdms2.TransientAxis
        ``TransientAxis`` containing uniform longitude axis.
    """
    lonArray = startLon + deltaLon * numpy.arange(nlon)
    lon = createAxis(lonArray, id="longitude")
    lon.designateLongitude()
    lon.units = "degrees_east"
    lonBounds = lon.genGenericBounds(width=deltaLon)
    lon.setBounds(lonBounds)
    return lon


def mapLinearIntersection(xind, yind, iind,
                          aMinusEps, aPlusEps, bPlusEps, bMinusEps,
                          boundLeft, nodeSubI, boundRight):
    """
    Map Linear Intersection

    Parameters
    ----------
    xind : c' if (a,b) is closed on the left, 'o' if open,
    yind : same for right endpoint j

    Returns
    -------
    True if the coordinate interval (a,b) intersects the node nodeSubI or cell
    bounds [boundLeft,boundRight], where the interval (a,b) is defined by:

      * aMinusEps,aPlusEps = a +/- epsilon
      * bPlusEps,bMinusEps = b +/- epsilon

    and the intersection option iind = 'n','b','e','s' specifies whether
    the intersection is with respect to the node value nodeSubI ('n' or 'e')
    or the cell bounds [boundLeft,boundRight].

    See Also
    --------
    mapLinearExt
    """

    if(iind == 'n' or iind == 'e'):
        testC_ = (aMinusEps <= nodeSubI)
        test_C = (nodeSubI <= bPlusEps)
        testO_ = (aPlusEps < nodeSubI)
        test_O = (nodeSubI < bMinusEps)
    elif(iind == 'b'):
        testC_ = (aMinusEps <= boundRight)
        test_C = (boundLeft <= bPlusEps)
        testO_ = (aPlusEps < boundRight)
        test_O = (boundLeft < bMinusEps)
    elif(iind == 's'):
        testC_ = (aMinusEps <= boundLeft)
        test_C = (boundRight <= bPlusEps)
        testO_ = (aPlusEps < boundLeft)
        test_O = (boundRight < bMinusEps)

    if(xind == 'c' and yind == 'c'):
        test = (testC_ and test_C)
    elif(xind == 'c' and yind == 'o'):
        test = (testC_ and test_O)
    elif(xind == 'o' and yind == 'c'):
        test = (testO_ and test_C)
    elif(xind == 'o' and yind == 'o'):
        test = (testO_ and test_O)

    return(test)


def mapLinearExt(axis, bounds, interval, indicator='ccn',
                 epsilon=None, stride=1, wrapped=0):
    """Map coordinate interval to index interval, without
    wraparound. Interval has the form (x,y) where x and y are the
    endpoints in coordinate space. Indicator is a three-character
    string, where the first character is 'c' if the interval is closed
    on the left, 'o' if open, and the second character has the same
    meaning for the right-hand point. The third character indicates
    how the intersection of the interval and axis is treated:

    'n' - the node is in the interval
    'b' - the interval intersects the cell bounds
    's' - the cell bounds are a subset of the interval
    'e' - same as 'n', plus an extra node on either side.

    Returns
    -------
    The corresponding index interval (i,j), where i<j, indicating the
    half-open index interval [i,j), or None if the intersection is empty.
    """

    indicator = indicator.lower()
    length = len(axis)

    # Make the interval and search array non-decreasing
    x, y = interval

    iind = indicator[2]

    if x > y:
        x, y = y, x
        xind = indicator[1]
        yind = indicator[0]

    else:
        xind = indicator[0]
        yind = indicator[1]

    if axis[0] > axis[-1]:
        ar = axis[::-1]
        if bounds[0, 0] < bounds[0, 1]:
            bd = bounds[::-1]
        else:
            bd = bounds[::-1, ::-1]
        direc = 'dec'
    else:
        ar = axis
        if bounds[0, 0] < bounds[0, 1]:
            bd = bounds
        else:
            bd = bounds[:, ::-1]
        direc = 'inc'

    if(epsilon is None):
        eps = 1.0e-5
        if len(ar) > 1:
            epsilon = eps * min(abs(ar[1] - ar[0]), abs(ar[-1] - ar[-2]))
        else:
            epsilon = eps

    #
    #  interval bound +/- epsilon
    #

    aMinusEps = (x - epsilon)
    aPlusEps = (x + epsilon)
    bMinusEps = (y - epsilon)
    bPlusEps = (y + epsilon)

    # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo
    #
    # out-of-bounds requests
    #
    # oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo

    if iind in ['n', 'e']:
        mina = ar[0]
        maxa = ar[-1]
    else:
        mina = bd[0, 0]
        maxa = bd[-1, 1]

    if(bPlusEps < mina or aMinusEps > maxa):
        return None

    # nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
    #
    # empty node check
    #
    # nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn

    # Handle empty intersections
    if (
        (((aPlusEps) > ar[-1]) and (iind == 'n') and (xind == 'o')) or
        (((aMinusEps) >= ar[-1]) and (iind == 'n') and (xind == 'c')) or
        (((bMinusEps) < ar[0]) and (iind == 'n') and (yind == 'o')) or
        (((bPlusEps) <= ar[0]) and (iind == 'n') and (yind == 'c'))
    ):
        return None

    bdMaxRight = max(bd[-1][0], bd[-1][1])
    bdMinLeft = min(bd[0][0], bd[0][1])
    if (
        (((aMinusEps) > bdMaxRight) and (iind != 'n') and (xind == 'o')) or
        (((aMinusEps) >= bdMaxRight) and (iind != 'n') and (xind == 'c')) or
        (((bPlusEps) < bdMinLeft) and (iind != 'n') and (yind == 'o')) or
        (((bPlusEps) <= bdMinLeft) and (iind != 'n') and (yind == 'c'))
    ):
        return None

    # The intersection is nonempty; use searchsorted to get left/right limits
    # for testing

    ii, jj = numpy.searchsorted(ar, (x, y))

    #
    #  find index range for left (iStart,iEnd) and right (jStart,jEnd)
    #

    # iEnd + 2 because last point in loop not done
    iStart = ii - 1
    iEnd = ii + 2
    if(iStart < 0):
        iStart = 0
    if(iEnd >= length):
        iEnd = length - 1

    jStart = jj - 1
    jEnd = jj + 2
    if(jStart < 0):
        jStart = 0
    if(jEnd >= length):
        jEnd = length - 1

    #
    #  initialise the index to -1 (does not exist)
    #

    iInterval = -1
    jInterval = -1
    iIntervalB = -1
    jIntervalB = -1

    # pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp
    #
    #  preliminary checks
    #
    # pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp

    if(iStart == jStart == iEnd == jEnd):
        iInterval = jInterval = iStart

    elif(jEnd < iEnd):
        pass

    else:

        # llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll
        #
        #  left interval check
        #
        # llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll

        # - user check

        for i in range(iStart, iEnd + 1):

            nodeSubI = ar[i]
            boundLeft = bd[i][0]
            boundRight = bd[i][1]

            test = mapLinearIntersection(
                xind,
                yind,
                iind,
                aMinusEps,
                aPlusEps,
                bPlusEps,
                bMinusEps,
                boundLeft,
                nodeSubI,
                boundRight)

            if(iInterval == -1 and test):
                iInterval = i
                break

        # - "B" check for extension

        for i in range(iStart, iEnd + 1):

            nodeSubI = ar[i]
            boundLeft = bd[i][0]
            boundRight = bd[i][1]

            testB = mapLinearIntersection(
                xind,
                yind,
                'b',
                aMinusEps,
                aPlusEps,
                bPlusEps,
                bMinusEps,
                boundLeft,
                nodeSubI,
                boundRight)

            if(iIntervalB == -1 and testB):
                iIntervalB = i
                break

        # rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr
        #
        #  right interval check
        #
        # rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr

        for j in range(jStart, jEnd + 1):

            nodeSubI = ar[j]
            boundLeft = bd[j][0]
            boundRight = bd[j][1]

            #
            #  user test
            #

            test = mapLinearIntersection(
                xind,
                yind,
                iind,
                aMinusEps,
                aPlusEps,
                bPlusEps,
                bMinusEps,
                boundLeft,
                nodeSubI,
                boundRight)

            if((jInterval == -1 and iInterval != -1 and test == 0 and j <= jEnd)):
                jInterval = j - 1

            if((j == length - 1 and test == 1)):
                jInterval = j

                # no break here...

        #
        #  B test on right
        #

        for j in range(jStart, jEnd + 1):

            nodeSubI = ar[j]
            boundLeft = bd[j][0]
            boundRight = bd[j][1]

            testB = mapLinearIntersection(
                xind,
                yind,
                'b',
                aMinusEps,
                aPlusEps,
                bPlusEps,
                bMinusEps,
                boundLeft,
                nodeSubI,
                boundRight)

            if((jIntervalB == -1 and iIntervalB != -1 and testB == 0 and j <= jEnd)):
                jIntervalB = j - 1

            if((j == length - 1 and testB == 1)):
                jIntervalB = j

    # eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
    #
    #  extension check
    #
    # eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee

    if(iind == 'e'):

        # if B index does not exist return
        if(iIntervalB < 0 or jIntervalB < 0):
            return None

        # if user index exists:
        elif ((iInterval > -1 and jInterval > -1)):

            if(jInterval < iInterval):

                npoints = iInterval - jInterval
                if(npoints > 0):
                    (iInterval, jInterval) = (jInterval + 1, iInterval + 1)

                else:
                    jInterval = iInterval
                    iInterval = jInterval + 1

            else:

                iInterval = iInterval - 1
                jInterval = jInterval + 1

        # else set index interval to B index interval
        else:

            iInterval = iIntervalB
            jInterval = jIntervalB

        if(iInterval == jInterval):
            if(x < ar[iInterval] and iInterval > 0):
                iInterval = jInterval - 1
            elif(jIntervalB < length - 1):
                jInterval = iInterval + 1

        if(jInterval < iInterval):
            npoints = jInterval - iInterval
            if(npoints > 2):
                jInterval = iIntervalB
                iInterval = jIntervalB
            else:
                jInterval = iIntervalB
                iInterval = jIntervalB + 1

        # Since the lookup is linear, ensure that the result is in range
        # [0..length)
        iInterval = max(iInterval, 0)
        jInterval = min(jInterval, length - 1)

    # ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
    #
    # final checks
    #
    # ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

    # if jInteval < iInterval have a single point; set to iInterval

    if(jInterval < iInterval):
        jInterval = iInterval

    elif(jInterval < 0 and iInterval < 0):
        return None

    # Reverse back if necessary
    if direc == 'dec':
        iInterval, jInterval = length - jInterval - 1, length - iInterval - 1

    iReturn = iInterval
    jReturn = jInterval + 1

    return (iReturn, jReturn)


def lookupArray(ar, value):
    """Lookup value in array ar.

    Parameters
    ----------
    ar : Input array
    value : Value to search

    Returns
    -------
    index:
        * ar is monotonically increasing.
        * value <= ar[index], index==0..len(ar)-1
            * value > ar[index], index==len(ar)
            * ar is monotonically decreasing:
                * value >= ar[index], index==0..len(ar)-1
                * value < ar[index], index==len(ar)
    """
    ar = numpy.ma.filled(ar)
    ascending = (ar[0] < ar[-1]) or len(ar) == 1
    if ascending:
        index = numpy.searchsorted(ar, value)
    else:
        revar = ar[::-1]
        index = numpy.searchsorted(revar, value)
        if index < len(revar) and value == revar[index]:
            index = len(ar) - index - 1
        else:
            index = len(ar) - index
    return index

# Lookup a value in a monotonic 1-D array. value is a scalar
# Always returns a valid index for ar
# def lookupArray(ar,value):
#     ascending = (ar[0]<ar[-1])
# if ascending:
#         index = numpy.searchsorted(ar,value)
# else:
#         index = numpy.searchsorted(ar[::-1],value)
#         index = len(ar)-index-1
#     index = max(index,0)
#     index = min(index,len(ar))
# return index

# Return true if vector vec1 is a subset of vec2, within tolerance tol.
# Return second arg of index, if it is a subset


def isSubsetVector(vec1, vec2, tol):
    """Checks if ``vec1`` is a subset of ``vec2``.

    Parameters
    ----------
    vec1 : (cdms2.TransientAxis, cdms2.FileAxis, numpy.ndarray)
        Subset data.
    vec2 : (cdms2.TransientAxis, cdms2.FileAxis, numpy.ndarray)
        Superset data.
    tol : float
        Tolerance used when checking for subset.

    Returns
    -------
    (bool/int), int
        First value of ``True`` denotes ``vec1`` is a subset of ``vec2``.
        A value of 0 or ``False`` denotes the opposite.

        Second value is the starting index of ``vec1`` in ``vec2`` if it
        is a subset.
    """
    # TODO this needs fixing return should be None if not subset otherwise the index value.
    index = lookupArray(vec2, vec1[0])
    if index > (len(vec2) - len(vec1)):
        # vec1 is too large, cannot be a subset
        return (0, -1)
    issubset = numpy.alltrue(numpy.less(numpy.absolute(
        vec1 - vec2[index:index + len(vec1)]), tol))
    if issubset:
        return (issubset, index)
    else:
        return (0, -1)


def isOverlapVector(vec1, vec2, atol=1.e-8):
    """Is Overlap Vector

    Parameters
    ----------
    vec1 : Input arrays to compare
    vec2 : Input arrays to compare
    atol : float, optional
    Absolute tolerance, The absolute differenc is equal to **atol** Default is 1e-8

    Returns
    -------
    (isoverlap, index) :
        where isoverlap is true if a leading portion of vec1 is a subset of vec2;
            * index is the index such that vec1[0] <= vec2[index]
            * If indexl == len(vec2), then vec1[0] > vec2[len(vec2) - 1]
    """
    index = lookupArray(vec2, vec1[0])
    if index == 0 and abs(vec1[0] - vec2[0]):
        return (0, index)
    elif index == len(vec2):
        return (1, index)
    else:
        ar2 = vec2[index:index + len(vec1)]
        ar1 = vec1[:len(ar2)]
        isoverlap = numpy.ma.allclose(ar1, ar2, atol=atol)
    if isoverlap:
        return (isoverlap, index)
    else:
        return (0, index)


def allclose(ax1, ax2, rtol=1.e-5, atol=1.e-8):
    """All close

    Parameters
    ----------
    ax1, ax2 : array_like

    Returns
    -------
    bool
        True if all elements of axes ax1 and ax2 are close,
        in the sense of numpy.ma.allclose.

    See Also : all, any

    Examples
    --------
    >>> a = ma.array([1e10, 1e-7, 42.0], mask=[0, 0, 1])
    >>> a
    masked_array(data = [10000000000.0 1e-07 --],
                 mask = [False False True],
           fill_value = 1e+20)
    >>> b = ma.array([1e10, 1e-8, 42.0], mask=[0, 0, 1])
    >>> ma.allclose(a, b)
    False
    """
    return ((ax1 is ax2) or numpy.ma.allclose(
        ax1[:], ax2[:], rtol=rtol, atol=atol))

# AbstractAxis defines the common axis interface.
# Concrete axis classes are derived from this class.


class AbstractAxis(CdmsObj):
    """AbstractAxis

    Parameters
    ----------
    parent : cdms2.dataset.CdmsFile
        Reference to ``CdmsFile`` containing axis.
    node : None
        Not used.
    """

    def __init__(self, parent, node):
        CdmsObj.__init__(self, node)
        val = self.__cdms_internals__ + ['id', ]
        self.___cdms_internals__ = val
        self.parent = parent
        self.id = id
        # Cached data values
        self._data_ = None
        # Cached wraparound values for circular axes
        self._doubledata_ = None

    def __str__(self):
        return "\n".join(self.listall()) + "\n"

    __repr__ = __str__

    def __len__(self):
        raise CDMSError(MethodNotImplemented)

    def _getshape(self):
        return (len(self),)

    def _getdtype(self, name=None):
        """Gets numpy dtype.

        Parameters
        ----------
        name : str
            Name of the dtype
        """
        tc = self.typecode()
        return numpy.dtype(tc)

    def __getitem__(self, key):
        raise CDMSError(MethodNotImplemented)

    def __setitem__(self, index, value):
        raise CDMSError(MethodNotImplemented)

    def __getslice__(self, low, high):
        raise CDMSError(MethodNotImplemented)

    def __setslice__(self, low, high, value):
        raise CDMSError(MethodNotImplemented)

    def rank(self):
        """Gets rank of contained data.

        Returns
        -------
        int
            Number of dimensions.
        """
        return len(self.shape)

    # Designate axis as a latitude axis.
    # If persistent is true, write metadata to the container.
    def designateLatitude(self, persistent=0):
        """Designate axis as latitude.

        Sets attribute ``axis`` to "Y".

        Parameters
        ----------
        persistent : int
            0: Sets value in memory.
            1: Sets value in underlying file.
        """
        if persistent:
            self.axis = "Y"
        else:
            self.__dict__['axis'] = "Y"
            self.attributes['axis'] = "Y"

    # Return true iff the axis is a latitude axis
    def isLatitude(self):
        """Checks if axis is latitude.

        Returns
        -------
        bool
            True if axis is latitude otherwise false.
        """
        id = self.id.strip().lower()
        if (hasattr(self, 'axis') and self.axis == 'Y'):
            return True
        units = getattr(self, "units", "").strip().lower()
        if units in [
            "degrees_north", "degree_north", "degree_n", "degrees_n",
            "degreen", "degreesn"] and not(
                self.isLongitude() or self.isLevel() or self.isTime()):
            return True
        return (id[0:3] == 'lat') or (id in latitude_aliases)

    # Designate axis as a vertical level axis
    # If persistent is true, write metadata to the container.
    def designateLevel(self, persistent=0):
        """Designate axis as level.

        Sets attribute ``axis`` to "Z".

        Parameters
        ----------
        persistent : int
            0: Sets value in memory.
            1: Sets value in underlying file.
        """
        if persistent:
            self.axis = "Z"
        else:
            self.__dict__['axis'] = "Z"
            self.attributes['axis'] = "Z"

    # Return true iff the axis is a level axis
    def isLevel(self):
        """Checks if axis is level.

        Returns
        -------
        bool
            True if axis is level otherwise false.
        """
        id = self.id.strip().lower()
        if (hasattr(self, 'axis') and self.axis == 'Z'):
            return True
        if getattr(self, "positive", "").strip().lower() in ["up", "down"]:
            return True
        try:
            # Ok let's see if this thing as pressure units
            import genutil
            p = genutil.udunits(1, "Pa")
            units = getattr(self, 'units', "").strip()
            p.to(units)
            return True
        except ImportError:
            # import warnings
            # warnings.warn(
            #     "genutil module not present, was not able to determine if axis is level based on units")
            pass
        except Exception:
            pass
        return ((id[0:3] == 'lev') or (id[0:5] == 'depth') or
                (id in level_aliases))

    # Designate axis as a longitude axis
    # If persistent is true, write metadata to the container.
    # If modulo is defined, set as circular
    def designateLongitude(self, persistent=0, modulo=360.0):
        """Designate axis as longitude.

        Sets attribute ``axis`` to "X".

        Parameters
        ----------
        persistent : int
            0: Sets value in memory.
            1: Sets value in underlying file.
        modulo : float
            Sets topology of longitude. None will set topology to "linear".
        """
        if persistent:
            self.axis = "X"
            if modulo is None:
                self.topology = 'linear'
            else:
                self.modulo = modulo
                self.topology = 'circular'
        else:
            self.__dict__['axis'] = "X"
            self.attributes['axis'] = "X"
            if modulo is None:
                self.__dict__['topology'] = 'linear'
                self.attributes['topology'] = 'linear'
            else:
                self.__dict__['modulo'] = modulo
                self.__dict__['topology'] = 'circular'
                self.attributes['modulo'] = modulo
                self.attributes['topology'] = 'circular'

    # Return true iff the axis is a longitude axis
    def isLongitude(self):
        """Checks if axis is longitude.

        Returns
        -------
        bool
            True if axis is longitude otherwise False.
        """
        id = self.id.strip().lower()
        if (hasattr(self, 'axis') and self.axis == 'X'):
            return True
        units = getattr(self, "units", "").strip().lower()
        if units in [
                "degrees_east", "degree_east", "degree_e", "degrees_e", "degreee",
                "degreese"] and not(
                self.isLatitude() or self.isLevel() or self.isTime()):
            return True
        return (id[0:3] == 'lon') or (id in longitude_aliases)

    # Designate axis as a time axis, and optionally set the calendar
    # If persistent is true, write metadata to the container.
    def designateTime(self, persistent=0, calendar=None):
        """Designate axis as time.

        Sets attribute ``axis`` to "T".

        Parameters
        ----------
        persistent : int
            0: Sets value in memory.
            1: Sets value in underlying file.
        calendar : cdtime.Calendar
            Sets the calendar for the time axis. See ``cdtime`` for valid calendars.
        """
        if calendar is None:
            calendar = cdtime.DefaultCalendar
        if persistent:
            self.axis = "T"
            if calendar is not None:
                self.setCalendar(calendar, persistent)
        else:
            self.__dict__['axis'] = "T"
            self.attributes['axis'] = "T"
            if calendar is not None:
                self.setCalendar(calendar, persistent)

    # For isTime(), keep track of whether each id is for a time axis or not, for better performance.
    # This dictionary is a class variable (not a member of any particular
    # instance).
    idtaxis = {}  # id:type where type is 'T' for time, 'O' for other

    # Return true iff the axis is a time axis
    def isTime(self):
        """Checks if axis is time.

        Returns
        -------
        bool
            True if axis is time otherwise false.
        """
        id = self.id.strip().lower()
        if hasattr(self, 'axis'):
            if self.axis == 'T':
                return True
            elif self.axis is not None:
                return False
        # Have we saved the id-to-axis type information already?
        if id in self.idtaxis:
            if self.idtaxis[id] == 'T':
                return True
            else:
                return False
        # Try to figure it out from units
        try:
            import genutil
            units = getattr(self, "units", "").lower()
            sp = units.split("since")
            if len(sp) > 1:
                t = genutil.udunits(1, "day")
                s = sp[0].strip()
                if s in t.available_units() and t.known_units()[s] == "TIME":
                    self.idtaxis[id] = 'T'
                    return True
                # try the plural version since udunits only as singular (day
                # noy days)
                s = s + "s"
                if s in t.available_units() and t.known_units()[s] == "TIME":
                    self.idtaxis[id] = 'T'
                    return True
        except BaseException:
            pass
        # return (id[0:4] == 'time') or (id in time_aliases)
        if (id[0:4] == 'time') or (id in time_aliases):
            self.idtaxis[id] = 'T'
            return True
        else:
            self.idtaxis[id] = 'O'
            return False

    # Return true iff the axis is a forecast axis
    def isForecast(self):
        """Checks if axis is forecast.

        Returns
        -------
        bool
            True if axis is forecast otherwise False.
        """
        id = self.id.strip().lower()
        if (hasattr(self, 'axis') and self.axis == 'F'):
            return True
        return (id[0:6] == 'fctau0') or (id in forecast_aliases)

    # TODO is this needed?
    def isForecastTime(self):
        """Checks if axis is forecast.

        Returns
        -------
        bool
            True if axis is forecast otherwise False.
        """
        return self.isForecast()

    def asComponentTime(self, calendar=None):
        """Returns values as component time if axis represents time.

        Parameters
        ----------
        calendar : cdtime.Calendar
            Calendar used to convert relative time to component time. If ``None``
            then the calendar set in attributes will be used. If this is not set
            then the default calendar will be used.
        """
        if not hasattr(self, 'units'):
            raise CDMSError("No time units defined")
        if calendar is None:
            calendar = self.getCalendar()
        if self.isForecast():
            result = [forecast.comptime(t) for t in self[:]]
        else:
            result = []
            for val in self[:]:
                result.append(cdtime.reltime(val, self.units).tocomp(calendar))
        return result

    #
    #  mf 20010418 -- output DTGs (YYYYMMDDHH)
    #
    def asDTGTime(self, calendar=None):
        """Returns values as DTG if axis represents time.

        Parameters
        ----------
        calendar : cdtime.Calendar
            Calendar used to convert relative time to component time. If ``None``
            then the calendar set in attributes will be used. If this is not set
            then the default calendar will be used.
        """
        if not hasattr(self, 'units'):
            raise CDMSError("No time units defined")
        result = []
        if calendar is None:
            calendar = self.getCalendar()
        for val in self[:]:
            comptime = cdtime.reltime(val, self.units).tocomp(calendar)
            s = repr(comptime)
            tt = str.split(s, ' ')

            ttt = str.split(tt[0], '-')
            yr = int(ttt[0])
            mo = int(ttt[1])
            da = int(ttt[2])

            ttt = str.split(tt[1], ':')
            hr = int(ttt[0])
            dtg = "%04d%02d%02d%02d" % (yr, mo, da, hr)
            result.append(dtg)

        return result

    def asdatetime(self, calendar=None):
        """ Returns values as ``datetime.datetime`` if axis represents time.

        Parameters
        ----------
        calendar : cdtime.Calendar
            Calendar used to convert relative time to component time. If ``None``
            then the calendar set in attributes will be used. If this is not set
            then the default calendar will be used.
        """
        import datetime
        if not hasattr(self, 'units'):
            raise CDMSError("No time units defined")
        result = []
        if calendar is None:
            calendar = self.getCalendar()
        for val in self[:]:
            c = cdtime.reltime(val, self.units).tocomp(calendar)
            dtg = datetime.datetime(
                c.year, c.month, c.day, c.hour, c.minute, int(c.second),
                int((c.second - int(c.second)) * 1000))
            result.append(dtg)
        return result

    def asRelativeTime(self, units=None):
        """ Returns values as relative time if axis represents time.

        Parameters
        ----------
        units : str
            Base units used in conversion of values.
        """
        sunits = getattr(self, 'units', None)
        if sunits is None or sunits == 'None':
            raise CDMSError("No time units defined")
        if units is None or units == 'None':
            units = sunits
        if self.isForecast():
            result = [forecast.comptime(t).torel(units) for t in self[:]]
        else:
            cal = self.getCalendar()
            result = [
                cdtime.reltime(
                    t,
                    sunits).torel(
                    units,
                    cal) for t in self[:]]
        return result

    def toRelativeTime(self, units, calendar=None):
        """Converts values in-place to relative time.

        Parameters
        ----------
        units : str
            Base units used converting component to relative values.
        calendar : cdtime.Calendar
            Calendar used to convert relative time to component time. If ``None``
            then the calendar set in attributes will be used. If this is not set
            then the default calendar will be used.
        """
        if not hasattr(self, 'units'):
            raise CDMSError("No time units defined")
        n = len(self[:])
        b = self.getBounds()
        scal = self.getCalendar()
        if calendar is None:
            calendar = scal
        else:
            self.setCalendar(calendar)
        for i in range(n):
            tmp = cdtime.reltime(self[i], self.units).tocomp(scal)
            tmp2 = numpy.array(
                float(
                    tmp.torel(
                        units,
                        calendar).value)).astype(
                self[:].dtype.char)
            # if i==1 : print
            # self[:].dtype.char,'tmp2:',tmp2,tmp2.astype('f'),self[i],self[i].astype('f')
            self[i] = tmp2
            if b is not None:
                tmp = cdtime.reltime(b[i, 0], self.units).tocomp(scal)
                b[i, 0] = numpy.array(
                    float(tmp.torel(units, calendar).value)).astype(b.dtype.char)
                tmp = cdtime.reltime(b[i, 1], self.units).tocomp(scal)
                b[i, 1] = numpy.array(
                    float(tmp.torel(units, calendar).value)).astype(b.dtype.char)
        if b is not None:
            self.setBounds(b)
        self.units = units
        return

# mfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmf
#
# mf 20010412 -- test if an Axis is intrinsically circular
#
# mfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmf

    # Return true iff the axis wraps around
    # An axis is defined as circular if:
    # (1) self.topology=='circular', or
    # (2) self.topology is undefined, and the axis is a longitude
    def isCircularAxis(self):
        """Superficial check if axis is circular.

        Returns
        -------
        (bool/int)
            True if axis topology is set to circular.
            False if axis topology is not circular.
            1 if axis is longitude.
            0 if not circular.
        """
        # TODO fix the return values no more mixed int/bool
        if hasattr(self, 'topology'):
            iscircle = (self.topology == 'circular')
        elif self.isLongitude():
            iscircle = 1
        else:
            iscircle = 0

        return iscircle

# mfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmf
#
# mf 20010405 -- test if an transient Axis is REALLY circular
#
# mfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmf

    # Return true iff the axis wraps around
    # An axis is defined as circular if:
    # (1) self.topology=='circular', or
    # (2) self.topology is undefined, and the axis is a longitude

    def isCircular(self):
        """Checks if axis is circular.

        Checks for attribute "realtopology" first. If "realtopology" is not present
        then the data is checked. Attribute "realtopology" is set from the result of
        checking the data.

        Returns
        -------
        bool
            True if axis is circular otherwise False.
        """
        if hasattr(self, 'realtopology'):
            if self.realtopology == 'circular':
                return True
            elif self.realtopology == 'linear':
                return False
        if(len(self) < 2):
            return False

        try:  # non float types will fail this
            baxis = self[0]
            eaxis = self[-1]
            deltaend = self[-1] - self[-2]
            eaxistest = eaxis + deltaend - baxis

            cycle = self.getModuloCycle()

            tol = 0.01 * deltaend

            test = 0
            if(abs(eaxistest - cycle) < tol):
                test = 1

            if hasattr(self, 'topology') and test == 1:
                iscircle = (self.topology == 'circular')
            elif (self.isLongitude() and test == 1):
                iscircle = 1
            else:
                iscircle = 0
        except BaseException:
            iscircle = 0

        # save realtopology attribute in __dict__, don't write it to the file
        if iscircle == 1:
            self.__dict__['realtopology'] = 'circular'
        elif iscircle == 0:
            self.__dict__['realtopology'] = 'linear'
        return iscircle

    def designateCircular(self, modulo, persistent=0):
        """Designates axis as circular.

        Parameters
        ----------
        modulo : float
            Length of cycle.
        persistent : (bool/int)
            True: Sets values in underlying file.
            Flase: Sets values in memory.
        """
        if persistent:
            self.topology = 'circular'
            self.modulo = modulo
        else:
            self.__dict__['topology'] = 'circular'
            self.__dict__['modulo'] = modulo
            self.attributes['modulo'] = modulo
            self.attributes['topology'] = 'linear'

    def isLinear(self):
        """Checks if axis is linear.

        Returns
        -------
        bool
            True if axis is linear otherwise False.
        """
        raise CDMSError(MethodNotImplemented)

    def getBounds(self, isGeneric=None):
        """Gets axis bounds.

        Parameters
        ----------
        isGeneric : bool
            If True generic bounds will be generated otherwise bounds in file
            be returned.
        """
        raise CDMSError(MethodNotImplemented)

    def getExplicitBounds(self):
        """Gets explicit bounds.

        Returns
        -------
        numpy.ndarray
            Returns bounds if they are cells otherise ``None`` is returned.
        """
        # Original doc
        # '''
        # Return None if not explicitly defined
        # This is a way to determine if attributes are defined at cell
        # or at point level. If this function returns None attributes are
        # defined at points, otherwise they are defined at cells
        # '''
        raise CDMSError(MethodNotImplemented)

    def getBoundsForDualGrid(self, dualGrid):
        """Get explicit bounds for dual grid.

        Parameters
        ----------
        dualGrid : bool
            True if targetting dual grids otherwise False.

        Returns
        -------
        numpy.ndarray
            If bounds are explicit and ``dualGrid`` is True then the explicit
            bounds are returned otherwise ``None`` is.

            If bounds are no explicit and ``dualGrid`` is False then the bounds
            are returned otherise ``None`` is.
        """
        # Original doc
        # '''
        # dualGrid changes the type of dataset from the current type to the dual.
        # So, if we have a point dataset we switch to a cell dataset and viceversa.
        # '''
        explicitBounds = self.getExplicitBounds()
        if (explicitBounds is None):
            # point data
            if (dualGrid):
                return self.getBounds()
            else:
                return None
        else:
            # cell data
            if (dualGrid):
                return None
            else:
                return explicitBounds

    def setBounds(self, bounds):
        """Sets the bounds for the axis.

        Parameters
        ----------
        bounds : numpy.ndarray
            2D array containing bounds for the axis.
        """
        raise CDMSError(MethodNotImplemented)

    # Return the cdtime calendar: GregorianCalendar, NoLeapCalendar, JulianCalendar, Calendar360
    # or None. If the axis does not have a calendar attribute, return the global
    # calendar.
    def getCalendar(self):
        """Gets calendar for axis.

        If the axis represents time then the calendar is return if stored in the attributes.

        Returns
        -------
        cdtime.Calendar
            Returns the calendar for the axis if defined otherwise ``None```
        """
        if hasattr(self, 'calendar'):
            calendar = self.calendar.lower()
        else:
            calendar = None

        cdcal = tagToCalendar.get(calendar, cdtime.DefaultCalendar)
        return cdcal

    # Set the calendar
    def setCalendar(self, calendar, persistent=1):
        """Sets calendar for axis.

        Parameters
        ----------
        calendar : cdtime.Calendar
            Calendar to set for the axis.
        persistent : (bool/int)
            Sets the calender in the underlying file if True otherwise its set in memory.
        """
        if persistent:
            self.calendar = calendarToTag.get(calendar, None)
            self.attributes['calendar'] = self.calendar
            if self.calendar is None:
                raise CDMSError(InvalidCalendar % calendar)
        else:
            self.__dict__['calendar'] = calendarToTag.get(calendar, None)
            self.attributes['calendar'] = self.calendar
            if self.__dict__['calendar'] is None:
                raise CDMSError(InvalidCalendar % calendar)

    def getData(self):
        """Get data.

        Returns
        -------
        numpy.ndarray
            Returns the axis data.
        """
        raise CDMSError(MethodNotImplemented)

    # Return the entire array
    def getValue(self):
        """Gets entire data.

        Returns
        -------
        numpy.ndarray
            Returns the axis data.
        """
        return self.__getitem__(slice(None))

    def assignValue(self, data):
        """Sets data.

        Parameters
        ----------
        data : numpy.ndarray
            Data representing the axis.
        """
        self.__setitem__(slice(None), data)

    def _time2value(self, value):
        """Returns value converted to relative time.

        Uses axis attributes to convert value to relative time.

        Parameters
        ----------
        value : (ComptimeType, ReltimeType, str)
            Value to convert to relative time.

        Returns
        -------
        str
            Relative time value.
        """
        # original doc
        # """ Map value of type comptime, reltime, or string of form "yyyy-mm-dd hh:mi:ss" to value"""
        if self.isTime():
            if type(value) in CdtimeTypes:
                value = value.torel(self.units, self.getCalendar()).value
            elif isinstance(value, string_types) and value not in [':', unspecified]:
                cal = self.getCalendar()
                value = cdtime.s2c(value, cal).torel(self.units, cal).value
        return value

    def getModuloCycle(self):
        """Gets axis modulo.

        Defaults to 360.0 if not store in attributes.

        Returns
        -------
        float
            The modulo value for the axis.
        """

        if hasattr(self, 'modulo'):
            cycle = self.modulo
            #
            # mf 20010419 test if attribute is a string (non CF), set to 360.0
            #
            if(isinstance(cycle, string_types)):
                cycle = 360.0
        else:
            cycle = 360.0

        if isinstance(cycle, numpy.ndarray):
            cycle = cycle[0]

        return(cycle)

    def getModulo(self):
        """Get axis modulo.

        Returns
        -------
        float
            The modulo value for the axis if axis is circular.
        """

        if not self.isCircular():
            return(None)

        return(self.getModuloCycle())

    # TODO this is a bad signature, too confusing not explicit enough
    # mapInterval(self, x, y, left_endpoint, right_endpoint, cycle):
    def mapInterval(self, interval, indicator='ccn', cycle=None):
        """Map coordinate interval to index interval. interval has one of the forms

          * `(x,y)`
          * `(x,y,indicator)`: indicator overrides keywork argument
          * `(x,y,indicator,cycle)`: indicator, cycle override keyword arguments
          * `None`: indicates the full interval

        where `x` and `y` are the endpoints in coordinate space. indicator is a
        two-character string, where the first character is `c` if the interval
        is closed on the left, `o` if open, and the second character has the
        same meaning for the right-hand point. Set cycle to a nonzero value
        to force wraparound.

        Parameters
        ----------
        internval : tuple of float, float, str (optional), float (optional)
            (x, y) First and last value to map.
            (x, y, indicator) First and last value to map with indicator for handling endpoints.
            (x, y, indicator, cycle) First and last value to map with endpoint indicator and cycle length.
        indicator : str
            String indicator describing how to handle interval endpoints.
        cycle : float
            Length of cycle to use when mapping interval.

        Returns
        -------
        The corresponding index interval (i,j), where i<j, indicating
        the half-open index interval [i,j), or None if the intersection is empty.

        For an axis which is circular (self.topology == 'circular'), [i,j)
        is interpreted as follows (where N = len(self)):

        (1) if j<=N, the interval does not wrap around the axis endpoint
        (2) if j>N, the interval wraps around, and is equivalent to the
            two consecutive intervals [i,N), [0,j-N)

        Example:
          if the vector is [0,2,4,...,358] of length 180,and the coordinate
          interval is [-5,5), the return index interval is[178,183). This is
          equivalent to the two intervals [178,180) and [0,3).

         Note:
           if the interval is interior to the axis, but does not span any axis element,
           a singleton (i,i+1) indicating an adjacent index is returned.
        """
        i, j, k = self.mapIntervalExt(interval, indicator, cycle)
        j = min(j, i + len(self))
        # i=i-1
        return (i, j)

# mfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmf
#
# mf 20010308 - 20010412 -- general handing of wrapping
#
# mfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmfmf

    def mapIntervalExt(self, interval, indicator='ccn', cycle=None, epsilon=None):
        """Extended ``mapInterval``.

        See ``mapInterval`` for full documentation.

        Parameters
        ----------
        internval : tuple of float, float, str (optional), float (optional)
            (x, y) First and last value to map.
            (x, y, indicator) First and last value to map with indicator for handling endpoints.
            (x, y, indicator, cycle) First and last value to map with endpoint indicator and cycle length.
        indicator : str
            String indicator describing how to handle interval endpoints.
        cycle : float
            Length of cycle to use when mapping interval.
        epsilon : Not use.

        Returns
        -------
        int, int, int
            Returns tuple containing the first and last index along with the stride.
        """
        # original doc
        # """Like mapInterval, but returns (i,j,k) where k is stride,
        # and (i,j) is not restricted to one cycle."""

        # nCycleMax : max number of cycles a user a specify in wrapping

        nCycleMax = 6

        # interval is None returns the full interval
        if interval is None or interval == ':':
            return (0, len(self), 1)

        # Allow intervals of the same form as getRegion.
        if len(interval) == 3:
            x, y, indicator = interval
            interval = (x, y)
        elif len(interval) == 4:
            x, y, indicator, cycle = interval
            interval = (x, y)

        # check length of indicator if overridden by user
        #

        indicator = indicator.lower()
        if len(indicator) == 2:
            indicator += 'n'

        if((len(indicator) != 3) or
           ((indicator[0] != 'c' and indicator[0] != 'o') or
            (indicator[1] != 'c' and indicator[1] != 'o') or
            (indicator[2] != 'n' and indicator[2] != 'b' and indicator[2] != 's' and
             indicator[2] != 'e')
            )
           ):
            raise CDMSError(
                "EEE: 3-character interval/intersection indicator incomplete or incorrect = " +
                indicator)

        if self._data_ is None:
            self._data_ = self.getData()

        # ttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt
        # Handle time types
        interval = (
            self._time2value(
                interval[0]), self._time2value(
                interval[1]))

        # If the interval is reversed wrt self, reverse the interval and
        # set the stride to -1
        if (interval[0] <= interval[1]) == (self[0] <= self[-1]):
            stride = 1
        else:
            stride = -1
            interval = (interval[1], interval[0])
            indicator = indicator[1] + indicator[0] + indicator[2]

        # mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
        #
        # basic test for wrapping - is axis REALLY circular?
        #
        # ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

        xi, yi = interval

        length = len(self)
        ar = self[:]
        ar0 = ar[0]
        arn = ar[-1]
        armin = min(ar0, arn)
        armax = max(ar0, arn)

        # Wrapped if circular and at least one value is outside the axis range.
        wraptest1 = self.isCircular()
        wraptest2 = not ((armin <= xi <= armax) and (armin <= yi <= armax))

        if (wraptest1 and wraptest2):

            #
            #  find cycle and calc # of cycles in the interval
            #

            cycle = self.getModulo()

            intervalLength = yi - xi
            intervalCycles = intervalLength / cycle

            bd = self.getBounds()

            nPointsCycle = len(ar)

            ar0 = ar[0]
            ar1 = ar[-1]

            #
            # test for reversed coordinates
            #

            if ar0 > ar1:
                cycle = -1 * abs(cycle)

            # eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
            #
            #  make sure xi<yi and shift to positive axis indices
            #
            # eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee

            # Ensure that xi<yi

            if cycle > 0 and yi < xi:
                xi, yi = yi, xi
            if cycle < 0 and yi > xi:
                xi, yi = yi, xi

            # calculate the number of cycles to shift to positive side

            nCycleShift = numpy.floor((xi - ar0) / cycle)
            xp = xi - cycle * nCycleShift
            yp = xp + intervalLength

            # Extend the data vector with wraparound number of cycles in
            # interval and shifts

            nCycle = int(intervalCycles + 1.0 + 0.5) + abs(nCycleShift)

            #
            # check if nCycle is > nCycleMax
            #
            if(nCycle >= nCycleMax):
                raise CDMSError(InvalidNCycles + repr(nCycle))

            self._doubledata_ = numpy.concatenate((ar, ar + cycle))
            k = 2
            while(k < nCycle):
                self._doubledata_ = numpy.concatenate(
                    (self._doubledata_, ar + k * cycle))
                k = k + 1

            # Map the canonical coordinate interval (xp,yp) in the 'extended' data array
            # create axis to get the bounds array

            bigar = self._doubledata_
            bigarAxis = createAxis(bigar)
            bd = bigarAxis.getBounds()
            if bd is None:              # In case autobounds is off
                bd = bigarAxis.genGenericBounds()

            # run the more general mapLinearExt to get the indices

            indexInterval = mapLinearExt(
                bigar, bd, (xp, yp), indicator, wrapped=1)

            #
            # check to make sure we got an interval
            #

            if(indexInterval is None):
                return None

            i, j = indexInterval

            #
            #  now shift i back
            #

            i = i + int(nCycleShift * float(nPointsCycle))

            #
            #  adjust the length of the output interval by the indicator
            #  mapLinear does the calc correctly, we have to modify because we
            #  are overriding with the (float)(number of cycles) in the interval
            #

            j = j + int(nCycleShift * float(nPointsCycle))
            retval = (i, j)

        else:
            bd = self.getBounds()
            if bd is None:              # In case autobounds is off
                bd = self.genGenericBounds()
            retval = mapLinearExt(ar, bd, interval, indicator)

        if retval is not None:
            i, j = retval
            if stride == -1:
                if(j == length):
                    i, j = j - 1, i - 1
                else:
                    i, j = j - 1, i - 1
                if j == -1:
                    j = None

            retval = (i, j, stride)

        return retval

    def subaxis(self, i, j, k=1, wrap=True):
        """Returns subaxis.

        Parameters
        ----------
        i : int
            Positive start index.
        j : int
            Positive stop index.
        k : int
            Positive/Negative step value.
        wrap : bool
            True if subaxis can be wrapper otherwise False to prevent wrapping.

        Returns
        -------
        cdms2.TransientAxis
            Returns ``TransientAxis`` containing sub-axis.
        """
        # Original doc
        # """Create a transient axis for the index slice [i:j:k]
        # The stride k can be positive or negative. Wraparound is
        # supported for longitude dimensions or those with a modulus attribute.
        # """
        isGeneric = [False]
        fullBounds = self.getBounds(isGeneric)
        _debug = 0

        # Handle wraparound
        modulo = None
        size = len(self)

        # ----------------------------------------------------------------------
        # mf 20010328 negative stride i >= vice i >
        # ----------------------------------------------------------------------

        if wrap and ((k > 0 and j > size) or (
                k < 0 and i >= size)) and self.isCircular():
            modulo = self.getModuloCycle()

        if modulo is not None:
            # If self is decreasing and stride is positive,
            # or self is increasing and stride is negative, subtract the modulus,
            # otherwise add it.
            if (self[0] > self[-1]) == (k > 0):
                modulo = -modulo

            # ------------------------------------------------------------------
            #
            #  mf 20010329 -- N vice two slice scheme (more general)
            #
            # ------------------------------------------------------------------

            donew = 1

            if(donew):

                sn = splitSliceExt(slice(i, j, k), size)
                if(_debug):
                    print("SSSS1-------------------- ", sn, len(sn))

                for kk in range(0, len(sn)):
                    sl = sn[kk]
                    if(_debug):
                        print("SSSSSSSS kk = ", kk, sl)
                    part = self[sl] + kk * modulo
                    if(_debug):
                        print("SSSSSSSSSSSSSSS modulo",
                              part[0], part[-1], modulo)
                    if(kk == 0):
                        data = part
                    else:
                        data = numpy.concatenate((data, part))

                    if fullBounds is not None:
                        bound = fullBounds[sl] + kk * modulo
                        if (kk == 0):
                            bounds = bound
                        else:
                            bounds = numpy.concatenate((bounds, bound))
                    else:
                        bounds = None

            else:

                s1, s2 = splitSlice(slice(i, j, k), size)
                if(_debug):
                    print("SSSS0: original ", s1, s2)

                part1 = self[s1]
                part2 = self[s2] + modulo
                if(_debug):
                    print("SSSSSSSSSSSSSSS modulo", self[0], self[-1], modulo)
                data = numpy.concatenate((part1, part2))
                if fullBounds is not None:
                    bounds1 = fullBounds[s1]
                    bounds2 = fullBounds[s2] + modulo
                    bounds = numpy.concatenate((bounds1, bounds2))
                else:
                    bounds = None

        else:                           # no wraparound
            data = self[i:j:k]
            if fullBounds is not None:
                bounds = fullBounds[i:j:k]
            else:
                bounds = None

        newaxis = TransientAxis(
            data,
            bounds,
            id=self.id,
            copy=1,
            genericBounds=isGeneric[0])

        if self.isLatitude():
            newaxis.designateLatitude()
        if self.isLongitude():
            newaxis.designateLongitude()
        if self.isLevel():
            newaxis.designateLevel()
        if self.isTime():
            newaxis.designateTime()

        for attname in list(self.attributes.keys()):
            if attname not in ["datatype", "length", "isvar",
                               "name_in_file", "partition", "partition_length"]:
                setattr(newaxis, attname, getattr(self, attname))
                newaxis.attributes[attname] = getattr(self, attname)

        # Change circular topology to linear if a strict subset was copied
        if hasattr(self, "topology") and self.topology == "circular" and len(
                newaxis) < len(self):
            newaxis.topology = "linear"

        return newaxis

# ----------------------------------------------------------------------
# mf 2001 set calls to subAxis as subaxis
# ----------------------------------------------------------------------

    subAxis = subaxis

    def typecode(self):
        """Data typecode.
        """
        raise CDMSError(MethodNotImplemented)

    # Check that a boundary array is valid, raise exception if not. bounds is
    # an array of shape (n,2)
    def validateBounds(self, bounds):
        """Checks whether boundaries are valid.

        Performs the following checks:
        - Bounds shape is correct for axis data.
        - Bounds values are monotonic.

        Notes
        -----
        This method does modify ``bounds`` by reshaping.

        Parameters
        ----------
        bounds : numpy.ndarray
            2D array containing bounds.
        """
        requiredShape = (len(self), 2)
        requiredShape2 = (len(self) + 1,)
        if bounds.shape != requiredShape and bounds.shape != requiredShape2:
            raise CDMSError(
                InvalidBoundsArray +
                'shape is %s, should be %s or %s' %
                (repr(
                    bounds.shape),
                    repr(requiredShape),
                    repr(requiredShape2)))
        # Why are we modifying data?
        # Seems better found in something like fixBounds(bounds) method
        if bounds.shape == requiredShape2:  # case of "n+1" bounds
            bounds2 = numpy.zeros(requiredShape)
            bounds2[:, 0] = bounds[:-1]
            bounds2[:, 1] = bounds[1::]
            bounds = bounds2
        mono = (bounds[0, 0] <= bounds[0, 1])
        if mono:
            for i in range(bounds.shape[0]):
                if not bounds[i, 0] <= self[i] <= bounds[i, 1]:
                    raise CDMSError(InvalidBoundsArray +
                                    'bounds[%i]=%f is not in the range [%f,%f]' %
                                    (i, self[i], bounds[i, 0], bounds[i, 1]))
        else:
            for i in range(bounds.shape[0]):
                if not bounds[i, 0] >= self[i] >= bounds[i, 1]:
                    raise CDMSError(InvalidBoundsArray +
                                    'bounds[%i]=%f is not in the range [%f,%f]' %
                                    (i, self[i], bounds[i, 1], bounds[i, 0]))
        return bounds

    # Generate bounds from midpoints. width is the width of the zone if the
    # axis has one value.
    def genGenericBounds(self, width=1.0):
        """Generate generic bounds.

        Generate generic bounds. The axis values will be in the center of the
        bounds.

        If the axis is latitude the endpoints of the bounds are capped at 90
        and -90 respectively.

        If the axis is longitude the endpoints of the bounds will be adjusted
        as to ensure they are circular.

        Parameters
        ----------
        width : float
            Width of the bounds when axis length is 1.

        Returns
        -------
        numpy.ndarray
            2D (n,2) array containing bounds values.

        Examples
        --------
        >>> a1 = cdms2.createAxis(np.arange(0, 360, 1), id='lon')
        >>> a1.designateLongitude()
        >>> b1 = a1.genGenericBounds()
        >>> b1[0, 0], b1[-1, 1]
        (array([-0.5,  0.5]), array([358.5, 359.5]))

        >>> a1 = cdms2.createAxis(np.arange(0, 360, 1), id='lon')
        >>> a1.designateLongitude()
        >>> b1 = a1.genGenericBounds()
        >>> b1[0, 0], b1[-1, 1]
        (array([90.5, 89.5]), array([-88.5, -89.5]))
        """
        if self._data_ is None:
            self._data_ = self.getData()
        ar = self._data_
        if len(self) > 1:
            leftPoint = numpy.array([1.5 * ar[0] - 0.5 * ar[1]])
            midArray = (ar[0:-1] + ar[1:]) / 2.0
            rightPoint = numpy.array([1.5 * ar[-1] - 0.5 * ar[-2]])
            bnds = numpy.concatenate((leftPoint, midArray, rightPoint))
        else:
            delta = width / 2.0
            bnds = numpy.array([self[0] - delta, self[0] + delta])

        # Transform to (n,2) array
        retbnds = numpy.zeros((ar.shape + (2,)), numpy.float64)
        retbnds[..., 0] = bnds[:-1]
        retbnds[..., 1] = bnds[1:]
        # To avoid floating point error on bound limits

        if(self.isLongitude() and hasattr(self, 'units') and
                (self.units.find('degree') != -1) and len(retbnds.shape) == 2):
            # Make sure we have close to 360 degree interval
            if(abs(abs(retbnds[-1, 1] - retbnds[0, 0]) - 360) <
                  (numpy.minimum(0.01, abs(retbnds[0, 1] - retbnds[0, 0]) * 0.1))):
                # Now check wether either bound is near an interger value;
                # if yes round both integer
                if((abs(retbnds[0, 0] - numpy.floor(retbnds[0, 0] + 0.5)) <
                    abs(retbnds[0, 1] - retbnds[0, 0]) * 0.01) or
                    (abs(retbnds[-1, 1] - numpy.floor(retbnds[-1, 1] + 0.5)) <
                     abs(retbnds[-1, 1] - retbnds[-1, 0]) * 0.01)):
                    # only for -180, 180 not needed if values are all positive
                    # (0-360)
                    if((retbnds[0, 0] * retbnds[-1, 1]) < 0):
                        # msg = "\nYour first bounds[0,0] %3.15lf will be corrected to %3.15lf\n"\
                        #       "Your bounds bounds[-1,1] %3.15lf will be corrected to %3.15lf" \
                        #     % (retbnds[0, 0], numpy.floor(retbnds[0, 0] + 0.5), retbnds[-1, 1],
                        #        numpy.floor(retbnds[-1, 1] + 0.5))
                        # warnings.warn(msg, UserWarning)
                        retbnds[0, 0] = numpy.floor(retbnds[0, 0] + 0.5)
                        retbnds[-1, 1] = numpy.floor(retbnds[-1, 1] + 0.5)
                else:
                    if(retbnds[-1, 1] > retbnds[0, 0]):
                        retbnds[-1, 1] = retbnds[0, 0] + 360.
                    else:
                        retbnds[0, 0] = retbnds[-1, 1] + 360.

        if((self.isLatitude() and getAutoBounds()) and hasattr(self, 'units') and (self.units.find('degree') != -1)):
            retbnds[0, ...] = numpy.maximum(-90.0,
                                            numpy.minimum(90.0, retbnds[0, ...]))
            retbnds[-1, ...] = numpy.maximum(-90.0,
                                             numpy.minimum(90.0, retbnds[-1, ...]))

        return retbnds

    def clone(self, copyData=1):
        """Clone axis.

        Parameters
        ----------
        copyData : int
            1 Will copy the data.
            0 Will use a reference of the axis data.

        Returns
        -------
        cdms2.TransientAxis
            Returns a ``TransientAxis`` containing a clone.
        """
        # Original doc
        # """clone (self, copyData=1)
        # Return a copy of self as a transient axis.
        # If copyData is 1, make a separate copy of the data."""
        isGeneric = [False]
        b = self.getBounds(isGeneric)
        if copyData == 1:
            mycopy = createAxis(copy.copy(self[:]))
        else:
            mycopy = createAxis(self[:])
        mycopy.id = self.id
        mydict = self.__dict__
        newdict = {k: mydict[k] for k in mydict if k not in ['_data_']}
        mycopy.__dict__.update(newdict)
        mycopy._obj_ = None  # Erase Cdfile object if exist
        try:
            mycopy.setBounds(b, isGeneric=isGeneric[0])
        except CDMSError:
            b = mycopy.genGenericBounds()
            mycopy.setBounds(b, isGeneric=False)
        return mycopy

    def listall(self, all=None):
        """List axis information.

        Parameters
        ----------
        all : bool
            If True values and bounds will be printed.

        Returns
        -------
        str
            Returns a string with all the information about the axis.
        """
        # "Get list of info about this axis."
        aname = self.id
        result = []
        result.append('   id: ' + aname)
        if self.isLatitude():
            result.append('   Designated a latitude axis.')
        if self.isLongitude():
            result.append('   Designated a longitude axis.')
        if self.isTime():
            result.append('   Designated a time axis.')
        if self.isLevel():
            result.append('   Designated a level axis.')
        try:
            units = self.units
            result.append('   units:  ' + units)
        except BaseException:
            pass
        d = self.getValue()
        result.append('   Length: ' + str(len(d)))
        result.append('   First:  ' + str(d[0]))
        result.append('   Last:   ' + str(d[-1]))
        flag = 1
        for k in list(self.attributes.keys()):
            if k in std_axis_attributes:
                continue
            if flag:
                result.append('   Other axis attributes:')
                flag = 0
            result.append('      ' + k + ': ' + str(self.attributes[k]))
        result.append('   Python id:  %s' % hex(id(self)))

        if all:
            result.append("   Values:")
            result.append(str(d))
            b = self.getBounds()
            result.append("   Bounds:")
            result.append(str(b))
        return result

    def info(self, flag=None, device=None):
        "Write info about axis; include dimension values and weights if flag"
        if device is None:
            device = sys.stdout
        device.write(str(self))

    def isVirtual(self):
        "Return true iff coordinate values are implicitly defined."
        return False

    shape = property(_getshape, None)
    dtype = _getdtype

# PropertiedClasses.set_property(AbstractAxis, 'shape',
# AbstractAxis._getshape, nowrite=1, nodelete=1)
# PropertiedClasses.set_property(AbstractAxis, 'dtype',
# AbstractAxis._getdtype, nowrite=1, nodelete=1)
# internattr.add_internal_attribute (AbstractAxis, 'id', 'parent')

# One-dimensional coordinate axis in a dataset


class Axis(AbstractAxis):
    """Base Axis class.

    Parameters
    ----------
    parent : cdms2.CdmsFile
        Underlying file object.
    axisNode : xml.etree.Element
        Xml element for axis.
    """

    def __init__(self, parent, axisNode=None):
        if axisNode is not None and axisNode.tag != 'axis':
            raise CDMSError('Creating axis, node is not an axis node.')
        AbstractAxis.__init__(self, parent, axisNode)
        if axisNode is not None:
            if axisNode.partition is not None:
                flatpart = axisNode.partition
                self.__dict__['partition'] = numpy.reshape(
                    flatpart, (len(flatpart) // 2, 2))
                self.attributes['partition'] = self.partition
        self.id = axisNode.id

    def typecode(self):
        """Get typecode.
        """
        return cdmsNode.CdToNumericType.get(self._node_.datatype)

    # Handle slices of the form x[i], x[i:j:k], x[(slice(i,j,k),)], and x[...]
    def __getitem__(self, key):
        node = self._node_
        length = len(node)

        # Allow key of form (slice(i,j),) etc.
        if isinstance(key, tuple) and len(key) == 1:
            key = key[0]

        if isinstance(key, (int, numpy.int, numpy.int32)):  # x[i]
            if key >= length:
                raise IndexError('index out of bounds')
            else:
                # Don't generate the entire array (if linear) just for one
                # value
                return node.data[key % length]
        elif isinstance(key, slice):  # x[i:j:k]
            if self._data_ is None:
                self._data_ = node.getData()
            return self._data_[key.start:key.stop:key.step]
        elif isinstance(key, type(Ellipsis)):  # x[...]
            if self._data_ is None:
                self._data_ = node.getData()
            return self._data_
        elif isinstance(key, tuple):
            raise IndexError('axis is one-dimensional')
        else:
            raise IndexError('index must be an integer: %s' % repr(key))

    # Get axis data
    def getData(self):
        """Get axis data.

        Returns
        -------
        numpy.ndarray
            Returns axis data.
        """
        return self._node_.getData()      # Axis data is retrieved from the metafile

    # Handle slices of the form x[i:j]
    def __getslice__(self, low, high):
        if self._data_ is None:
            self._data_ = self.getData()
        return self._data_[low:high]

    def __len__(self):
        return len(self._node_)

    # Return true iff the axis representation is linear
    def isLinear(self):
        """Checks if axis is linear.

        Returns
        -------
        bool
            True if axis is linear otherwise False.
        """
        return self._node_.dataRepresent == cdmsNode.CdLinear

    # Return the bounds array, or generate a default if autoBounds mode is on
    def getBounds(self, isGeneric=None):
        """Get axis bounds.

        If bounds are not available and you want them generated set the correct
        behavior using ``setAutoBounds``.

        Parameters
        ----------
        isGeneric : list of bool
            First value is set True if bounds are generated.

        Returns
        -------
        numpy.ndarray
            Returns bounds if available, generates bounds if ``setAutoBounds`` has been set
            accordingly otherise ``None`` is returned.
        """
        # '''
        # If isGeneric is a list with one element, we set its element to True if the
        # bounds were generated and False if bounds were read from the file.
        # '''
        if (isGeneric):
            isGeneric[0] = False
        boundsArray = self.getExplicitBounds()
        try:
            self.validateBounds(boundsArray)
        except BaseException:
            boundsArray = None
        abopt = getAutoBounds()
        if boundsArray is None and (abopt == 1 or (
                abopt == 2 and (self.isLatitude() or self.isLongitude()))):
            if (isGeneric):
                isGeneric[0] = True
            boundsArray = self.genGenericBounds()

        return boundsArray

    # Return the bounds array, or None
    @base_doc(AbstractAxis)
    def getExplicitBounds(self):
        """getExplicitBounds.
        """
        boundsArray = None
        if hasattr(self, 'bounds'):
            boundsName = self.bounds
            try:
                boundsVar = self.parent.variables[boundsName]
                boundsArray = numpy.ma.filled(boundsVar.getSlice())
            except KeyError:
                boundsArray = None

        return boundsArray

    @base_doc(AbstractAxis)
    def getCalendar(self):
        """getCalendar.
        """
        if hasattr(self, 'calendar'):
            calendar = self.calendar.lower()
        elif self.parent is not None and hasattr(self.parent, 'calendar'):
            calendar = self.parent.calendar.lower()
        else:
            calendar = None

        cdcal = tagToCalendar.get(calendar, cdtime.DefaultCalendar)
        return cdcal

# In-memory coordinate axis


class TransientAxis(AbstractAxis):
    """Axis in memory.

    Parameters
    ----------
    data : numpy.ndarray
        Array with data for axis.
    bounds : numpy.ndarray
        2D array containing bounds, should be shaped (N,2).
    id : str
        Identifier for axis.
    attributes : dict
        Mapping of attribute names and values.
    copy : int
        1: Store copy of data
        0: Store reference to data
    genericBounds : bool
        If ``True`` and bounds is ``None`` generic bounds will be generated.
    """

    axis_count = 0

    def __init__(self, data, bounds=None, id=None,
                 attributes=None, copy=0, genericBounds=False):
        AbstractAxis.__init__(self, None, None)
        if id is None:
            TransientAxis.axis_count = TransientAxis.axis_count + 1
            id = 'axis_' + str(TransientAxis.axis_count)
        if attributes is None:
            if hasattr(data, 'attributes'):
                attributes = data.attributes
        if attributes is not None:
            for name, value in list(attributes.items()):
                if name not in ['missing_value', 'name']:
                    setattr(self, name, value)
        self.id = id
        if isinstance(data, AbstractAxis):
            if copy == 0:
                self._data_ = data[:]
            else:
                self._data_ = numpy.array(data[:])
        elif isinstance(data, numpy.ndarray):
            if copy == 0:
                self._data_ = data
            else:
                self._data_ = numpy.array(data)
        elif isinstance(data, numpy.ma.MaskedArray):
            if numpy.ma.getmask(data) is not numpy.ma.nomask:
                raise CDMSError(
                    'Cannot construct an axis with a missing value.')
            data = data.data
            if copy == 0:
                self._data_ = data
            else:
                self._data_ = numpy.array(data)
        elif data is None:
            self._data_ = None
        else:
            self._data_ = numpy.array(data)

        self._doubledata_ = None
        self._genericBounds_ = genericBounds
        self.setBounds(bounds, isGeneric=genericBounds)

    def __getitem__(self, key):
        return self._data_[key]

    def __getslice__(self, low, high):
        return self._data_[low:high]

    def __setitem__(self, index, value):
        self._data_[index] = numpy.ma.filled(value)

    def __setslice__(self, low, high, value):
        self._data_[low:high] = numpy.ma.filled(value)

    def __len__(self):
        return len(self._data_)

    @base_doc(AbstractAxis)
    def getBounds(self, isGeneric=None):
        """getBounds.

        Parameters
        ----------
        isGeneric :
            isGeneric
        """
        if (isGeneric):
            isGeneric[0] = self._genericBounds_
        if self._bounds_ is not None:
            return copy.copy(self._bounds_)
        elif (getAutoBounds() == 1 or (getAutoBounds() == 2 and (self.isLatitude() or self.isLongitude()))):
            if (isGeneric):
                isGeneric[0] = True
            self._genericBounds_ = True
            return self.genGenericBounds()
        else:
            return None

    @base_doc(AbstractAxis)
    def getData(self):
        """getData.
        """
        return self._data_

    @base_doc(AbstractAxis)
    def getExplicitBounds(self):
        """getExplicitBounds.
        """
        if (self._genericBounds_):
            return None
        else:
            return copy.copy(self._bounds_)

    # Set bounds. The persistent argument is for compatibility with
    # persistent versions, is ignored. Same for boundsid and index.
    #
    # mf 20010308 - add validate key word, by default do not validate
    # isGeneric is False if bounds were generated, True if they were read from
    # a file
    def setBounds(self, bounds, persistent=0, validate=0,
                  index=None, boundsid=None, isGeneric=False):
        """Sets axis bounds.

        If ``bounds`` is None then generic bounds will be generated. See
        ``genGenericBounds`` for details.

        Parameters
        ----------
        bounds : numpy.ndarray
            2D array containing bounds for axis.
        persistent : int
            0: Stores bounds in memory
            1: Stores bounds in underlying file.
        validate : int
            0: No validation
            1: Validate bounds
        index :
            Not used.
        boundsid :
            Not used.
        isGeneric : bool
            True if bounds are generic.
        """
        if bounds is not None:
            if isinstance(bounds, numpy.ma.MaskedArray):
                bounds = numpy.ma.filled(bounds)
            if validate:
                bounds = self.validateBounds(bounds)
            else:                       # Just do the absolute minimum validation
                requiredShape = (len(self), 2)
                requiredShape2 = (len(self) + 1,)
                if bounds.shape != requiredShape and bounds.shape != requiredShape2:
                    raise CDMSError(
                        InvalidBoundsArray +
                        'shape is %s, should be %s or %s' %
                        (repr(
                            bounds.shape),
                            repr(requiredShape),
                            repr(requiredShape2)))
                if bounds.shape == requiredShape2:  # case of "n+1" bounds
                    bounds2 = numpy.zeros(requiredShape)
                    bounds2[:, 0] = bounds[:-1]
                    bounds2[:, 1] = bounds[1::]
                    bounds = bounds2
            self._bounds_ = copy.copy(bounds)
            self._genericBounds_ = isGeneric
        else:
            if (getAutoBounds() == 1 or (getAutoBounds() ==
                                         2 and (self.isLatitude() or self.isLongitude()))):
                self._bounds_ = self.genGenericBounds()
                self._genericBounds_ = True
            else:
                self._bounds_ = None

    @base_doc(AbstractAxis)
    def isLinear(self):
        return False

    @base_doc(AbstractAxis)
    def typecode(self):
        return self._data_.dtype.char


class TransientVirtualAxis(TransientAxis):
    """Virtual in-memory axis.

    Parameters
    ----------
    axisname : str
        Name of the axis.
    axislen : int
        Length of the axis.
    """

    def __init__(self, axisname, axislen):
        TransientAxis.__init__(self, None, id=axisname)
        self._virtualLength = axislen  # length of the axis

    def __len__(self):
        return self._virtualLength

    def __str__(self):
        return "<TransientVirtualAxis %s(%d)>" % (self.id, self._virtualLength)

    __repr__ = __str__

    def clone(self, copyData=1):
        return TransientVirtualAxis(self.id, len(self))

    @base_doc(AbstractAxis)
    def getData(self):
        return numpy.arange(float(self._virtualLength))

    @base_doc(AbstractAxis)
    def isCircular(self):
        # Circularity doesn't apply to index space.
        return False

    @base_doc(AbstractAxis)
    def isVirtual(self):
        return True

    @base_doc(AbstractAxis)
    def setBounds(self, bounds, isGeneric=False):
        self._bounds_ = None

    @base_doc(AbstractAxis)
    def __getitem__(self, key):
        return self.getData()[key]

    def __getslice__(self, low, high):
        return self.getData()[low:high]

# PropertiedClasses.initialize_property_class (TransientVirtualAxis)

# One-dimensional coordinate axis in a CdmsFile.


class FileAxis(AbstractAxis):
    """Axis stored in a file.

    Parameters
    ----------
    parent : cdms2.CdmsFile
        Underlying file.
    axisname : str
        Name of the axis.
    obj
    """

    def __init__(self, parent, axisname, obj=None):
        AbstractAxis.__init__(self, parent, None)
        val = self.__cdms_internals__ + ['name_in_file', ]
        self.___cdms_internals__ = val
        self.id = axisname
        self._obj_ = obj
        # Overshadows file boundary data, if not None
        self._boundsArray_ = None
        (units, typecode, name_in_file, parent_varname, dimtype, ncid) = \
            parent._file_.dimensioninfo[axisname]
        self.__dict__['_units'] = units
        att = self.attributes
        att['units'] = units
        self.attributes = att
        self.name_in_file = self.id
        if name_in_file:
            self.name_in_file = name_in_file
        # Combine the attributes of the variable object, if any
        if obj is not None:
            for attname in list(self._obj_.__dict__.keys()):
                attval = getattr(self._obj_, attname)
                if not isinstance(attval, types.BuiltinFunctionType):
                    self.__dict__[attname] = attval
                    att = self.attributes
                    att[attname] = attval
                    self.attributes = att

    @base_doc(AbstractAxis)
    def getData(self):
        if cdmsobj._debug == 1:
            print('Getting array for axis', self.id)
        if self.parent is None:
            raise CDMSError(FileWasClosed + self.id)
        try:
            result = self.parent._file_.readDimension(self.id)
            return result
        except BaseException:
            pass
        try:
            result = self._obj_.getitem(*(slice(None, None),))
        except BaseException:
            raise CDMSError('Data for dimension %s not found' % self.id)
        return result

    @base_doc(AbstractAxis)
    def typecode(self):
        if self.parent is None:
            raise CDMSError(FileWasClosed + self.id)
        (units, typecode, name_in_file, parent_varname, dimtype, ncid) = \
            self.parent._file_.dimensioninfo[self.id]
        return typecode

    def _setunits(self, value):
        """Sets axis units.

        Parameters
        ----------
        value : str
            Value to set "units" attribute.
        """
        self._units = value
        self.attributes['units'] = value
        if self.parent is None:
            raise CDMSError(FileWasClosed + self.id)
        setattr(self._obj_, 'units', value)
        (units, typecode, name_in_file, parent_varname, dimtype, ncid) = \
            self.parent._file_.dimensioninfo[self.id]
        self.parent._file_.dimensioninfo[self.id] = \
            (value, typecode, name_in_file, parent_varname, dimtype, ncid)

    def _getunits(self):
        """Gets units attribute.

        Returns
        -------
        str
            Value of units attribute.
        """
        return self._units

    def _delunits(self):
        """Delete units attribute.
        """
        del(self._units)
        del(self.attributes['units'])
        delattr(self._obj_, 'units')

    def __getattr__(self, name):
        if name == 'units':
            return self._units
        try:
            return self.__dict__[name]
        except BaseException:
            raise AttributeError
    # setattr writes external attributes to the file

    def __setattr__(self, name, value):
        if name == 'units':
            self._setunits(value)
            return
        if hasattr(self, 'parent') and self.parent is None:
            raise CDMSError(FileWasClosed + self.id)
#         s = self.get_property_s (name)
# if s is not None:
#             s(self, name, value)
# return
        if name not in self.__cdms_internals__ and name[0] != '_':
            setattr(self._obj_, name, value)
            self.attributes[name] = value
        self.__dict__[name] = value

    # delattr deletes external global attributes in the file
    def __delattr__(self, name):
        #         d = self.get_property_d(name)
        # if d is not None:
        #             d(self, name)
        # return
        if name == "units":
            self._delunits()
            return
        try:
            del self.__dict__[name]
        except KeyError:
            raise AttributeError("%s instance has no attribute %s." %
                                 (self.__class__.__name__, name))
        if name not in self.__cdms_internals__(name):
            delattr(self._obj_, name)
            del(self.attributes[name])

    # Read data
    # If the axis has a related Cdunif variable object, just read that variable
    # otherwise, cache the Cdunif (read-only) data values in self._data_. in this case,
    # the axis is not extensible, so it is not necessary to reread it each
    # time.
    def __getitem__(self, key):
        if self.parent is None:
            raise CDMSError(FileWasClosed + self.id)
        # See __getslice__ comment below.
        if (self._obj_ is not None) and (self.parent._mode_ != 'r') and not (
                hasattr(self.parent, 'format') and self.parent.format == "DRS"):
            # For negative strides, get the equivalent slice with positive stride,
            # then reverse the result.
            if (isinstance(key, slice)) and (
                    key.step is not None) and key.step < 0:
                posslice = reverseSlice(key, len(self))
                result = self._obj_.getitem(*(posslice,))
                return result[::-1]
            else:
                if isinstance(key, int) and key >= len(self):
                    raise IndexError('Index out of bounds: %d' % key)
                if not isinstance(key, tuple):
                    key = (key,)
                return self._obj_.getitem(*key)
        if self._data_ is None:
            self._data_ = self.getData()
        length = len(self._data_)
        if isinstance(key, int):  # x[i]
            if key >= length:
                raise IndexError('index out of bounds')
            else:
                return self._data_[key % length]
        elif isinstance(key, slice):  # x[i:j:k]
            return self._data_[key.start:key.stop:key.step]
        elif isinstance(key, type(Ellipsis)):  # x[...]
            return self._data_
        elif isinstance(key, tuple):
            raise IndexError('axis is one-dimensional')
        else:
            raise IndexError(
                'index must be an integer or slice: %s' %
                repr(key))

    def __getslice__(self, low, high):
        # Hack to prevent netCDF overflow error on 64-bit architectures
        high = min(Max32int, high)

        # Hack to fix a DRS bug: force use of readDimension for DRS axes.
        # Since DRS is read-only here, it is OK just to cache all dimensions.
        if self.parent is None:
            raise CDMSError(FileWasClosed + self.id)
        if (self._obj_ is not None) and (self.parent._mode_ != 'r') and not (
                hasattr(self.parent, 'format') and self.parent.format == "DRS"):
            return self._obj_.getslice(*(low, high))
        else:
            if self._data_ is None:
                self._data_ = self.getData()
            return self._data_[low:high]

    def __setitem__(self, index, value):
        if self._obj_ is None:
            raise CDMSError(ReadOnlyAxis + self.id)
        if self.parent is None:
            raise CDMSError(FileWasClosed + self.id)
        # need setslice to create a new shape using [newaxis]
        if(isinstance(index, slice)):
            if(index.start is not None):
                if(self.shape[0] < index.start):
                    low = index.start
                    high = index.stop
                    if(self.isUnlimited() and (high >= Max32int)):
                        high = self.__len__()
                    high = min(Max32int, high)
                    return self._obj_.setslice(
                        *(low, high, numpy.ma.filled(value)))
        return self._obj_.setitem(*(index, numpy.ma.filled(value)))

    def __setslice__(self, low, high, value):
        # Hack to prevent netCDF overflow error on 64-bit architectures
        if(self.isUnlimited() and (high >= Max32int)):
            high = self.__len__()
        high = min(Max32int, high)
        if self._obj_ is None:
            raise CDMSError(ReadOnlyAxis + self.id)
        if self.parent is None:
            raise CDMSError(FileWasClosed + self.id)
        return self._obj_.setslice(*(low, high, numpy.ma.filled(value)))

    def __len__(self):
        if self.parent is None:
            raise CDMSError(FileWasClosed + self.id)
        if self._obj_ is not None:
            length = len(self._obj_)
        elif self._data_ is None:
            self._data_ = self.getData()
            length = len(self._data_)
        else:
            length = len(self._data_)
        return length

    def isLinear(self):
        """isLinear.
        """
        return False                        # All file axes are vector representation

    # Return the bounds array, or generate a default if autobounds mode is set
    # If isGeneric is a list with one element, we set its element to True if the
    # bounds were generated and False if bounds were read from the file.
    @base_doc(AbstractAxis)
    def getBounds(self, isGeneric=None):
        if (isGeneric):
            isGeneric[0] = False
        boundsArray = self.getExplicitBounds()
        try:
            boundsArray = self.validateBounds(boundsArray)
        except Exception:
            boundsArray = None
        if boundsArray is None and (getAutoBounds() == 1 or (
                getAutoBounds() == 2 and (self.isLatitude() or self.isLongitude()))):
            if (isGeneric):
                isGeneric[0] = True
            boundsArray = self.genGenericBounds()

        return boundsArray

    # Return the bounds array, or None
    @base_doc(AbstractAxis)
    def getExplicitBounds(self):
        if self._boundsArray_ is None:
            boundsArray = None
            if hasattr(self, 'bounds'):
                boundsName = self.bounds
                try:
                    boundsVar = self.parent[boundsName]
                    boundsArray = numpy.ma.filled(boundsVar)
                    self._boundsArray_ = boundsArray  # for climatology performance
                except KeyError as err:
                    print(err)
                    boundsArray = None
        else:
            boundsArray = self._boundsArray_

        return boundsArray

    # Create and write boundary data variable. An exception is raised
    # if the bounds are already set. bounds is a numpy array.
    # If persistent==1, write to file, else save in self._boundsArray_
    # For a persistent axis, index=n writes the bounds starting at that
    # index in the extended dimension (default is index=0).
    # If the bounds variable is new, use the name boundsid, or 'bounds_<varid>'
    # if unspecified.
    # isGeneric is only used for TransientAxis
    @base_doc(AbstractAxis)
    def setBounds(self, bounds, persistent=0, validate=0,
                  index=None, boundsid=None, isGeneric=False):
        if persistent:
            if index is None:
                if validate:
                    bounds = self.validateBounds(bounds)
                index = 0

            # Create the bound axis, if necessary
            file = self.parent
            if file._boundAxis_ is None:

                # First look for 'bound' of length two
                if "bound" in file.axes and len(file.axes["bound"]) == 2:
                    file._boundAxis_ = file.axes["bound"]
                else:
                    file._boundAxis_ = file.createVirtualAxis("bound", 2)

            # Create the boundary variable if necessary
            if hasattr(self, 'bounds'):
                boundName = self.bounds
                boundVar = file.variables[boundName]
            else:
                if boundsid is None:
                    boundName = "bounds_" + self.id
                else:
                    boundName = boundsid
                boundVar = file.createVariable(
                    boundName, cdmsNode.NumericToCdType.get(
                        bounds.dtype.char), (self, file._boundAxis_))
                # And link to self
                self.bounds = boundName
                self._boundsArray_ = None

            boundVar[index:index + len(bounds)] = bounds

        else:
            self._boundsArray_ = copy.copy(bounds)

    @base_doc(AbstractAxis)
    def getCalendar(self):
        """getCalendar.
        """
        if hasattr(self, 'calendar'):
            calendar = self.calendar.lower()
        elif self.parent is not None and hasattr(self.parent, 'calendar'):
            calendar = self.parent.calendar.lower()
        else:
            calendar = None

        cdcal = tagToCalendar.get(calendar, cdtime.DefaultCalendar)
        return cdcal

    @base_doc(AbstractAxis)
    def isVirtual(self):
        "Return true iff coordinate values are implicitly defined."

        # No virtual axes in GrADS files
        if self.parent is not None and hasattr(
                self.parent, 'format') and self.parent.format == 'GRADS':
            return False
        return (self._obj_ is None)

    def isUnlimited(self):
        """Is axis unlimited.

        Returns
        -------
        bool
            True if axis is unlimited otherwise False.
        """
        if self.parent is not None and self.id in self.parent._file_.dimensions:
            return (self.parent._file_.dimensions[self.id] is None)
        else:
            return False
# PropertiedClasses.set_property (FileAxis, 'units',
# acts=FileAxis._setunits,
# nodelete=1
# )
# internattr.add_internal_attribute(FileAxis, 'name_in_file')


class FileVirtualAxis(FileAxis):
    """Virual FileAxis.

    Parameters
    ----------
    parent : CdmsFile
        Underlying file.
    axisname : str
        Name of the axis.
    axislen : int
        Length of the axis.
    """

    def __init__(self, parent, axisname, axislen):
        FileAxis.__init__(self, parent, axisname)
        self._virtualLength = axislen  # length of the axis

    def __len__(self):
        return self._virtualLength

    @base_doc(AbstractAxis)
    def getData(self):
        return numpy.arange(float(self._virtualLength))

    def isVirtual(self):
        """Checks if axis is virtual.

        Returns
        -------
        bool
            True if axis is virtual otherwise False.
        """
        return True

# PropertiedClasses.initialize_property_class (FileVirtualAxis)

# Functions for selecting axes


# Functions for selecting axes
def axisMatchAxis(axes, specifications=None, omit=None, order=None):
    """Match a list of axes following a specification or list of
     specificatons, and a specification or list of specifications
     of those axes to omit.

     Parameters
     ----------
     specifications :
         *  is None, include all axes less the omitted ones.

         *  Individual specifications must be integer indices into axes or
            matching criteria as detailed in axisMatches.

     omit :
         *  is None, do not omit any axis.

         *  Individual specifications must be integer indices into axes or
            matching criteria as detailed in axisMatches.

     order :
         *  A string containing the symbols `t,x,y,z` or `-`.  If a `-` is
            given, any elements of the result not chosen otherwise are filled
            in from left to right with remaining candidates.

     Returns
     -------
     A list of axes that match the specification omitting any axes that matches
     an omit specification.

     Axes are returned in the order they occur in the axes argument unless order is given.
    """
    return [axes[i] for i in
            axisMatchIndex(axes, specifications, omit, order)]


def axisMatchIndex(axes, specifications=None, omit=None, order=None):
    """Match a list of axes following a specification or list of
     specificatons, and a specification or list of specifications
     of those axes to omit.

     Parameters
     ----------
     specifications :
         *  is None, include all axes less the omitted ones.

         *  Individual specifications must be integer indices into axes or
            matching criteria as detailed in axisMatches.

     omit :
         *  is None, do not omit any axis.

         *  Individual specifications must be integer indices into axes or
            matching criteria as detailed in axisMatches.

     order :
         *  A string containing the symbols `t,x,y,z` or `-`.  If a `-` is
            given, any elements of the result not chosen otherwise are filled
            in from left to right with remaining candidates.

     Returns
     -------
     A list of axis' indices which match the specification omitting any axes that matches an omit specification.

     Axes are returned in the order they occur in the axes argument unless order is given.

    """
    if specifications is None:
        speclist = axes
    elif isinstance(specifications, bytes):
        speclist = [specifications]
    elif isinstance(specifications, list):
        speclist = specifications
    elif isinstance(specifications, tuple):
        speclist = list(specifications)
    elif isinstance(specifications, int):
        speclist = [specifications]
    elif isinstance(specifications, types.FunctionType):
        speclist = [specifications]
    else:  # to allow arange, etc.
        speclist = list(numpy.ma.filled(specifications))

    candidates = []
    for i in range(len(axes)):
        for s in speclist:
            if isinstance(s, int):
                r = (s == i)
            else:
                r = axisMatches(axes[i], s)
            if r:
                candidates.append(i)
                break

    if not candidates:
        return candidates  # list empty

    if omit is None:
        omitlist = []
    elif isinstance(omit, string_types):
        omitlist = [omit]
    elif isinstance(omit, list):
        omitlist = omit
    elif isinstance(omit, tuple):
        omitlist = list(omit)
    elif isinstance(omit, int):
        omitlist = [omit]
    elif isinstance(omit, types.FunctionType):
        omitlist = [omit]
    elif isinstance(omit, AbstractAxis):
        omitlist = [omit]
    else:
        raise CDMSError('Unknown type of omit specifier.')

    for s in omitlist:
        if isinstance(s, int):
            for i in range(len(candidates)):
                if axes[candidates[i]] is axes[s]:
                    del candidates[i]
                    break
        elif isinstance(s, AbstractAxis):
            for i in range(len(candidates)):
                if s is axes[candidates[i]]:
                    del candidates[i]
                    break
        else:
            for i in range(len(candidates)):
                r = axisMatches(axes[candidates[i]], s)
                if r:
                    del candidates[i]
                    break

    if order is None:
        return candidates

    n = len(candidates)
    m = len(order)
    result = [None] * n
# this loop is done this way for future escapes where elements of order
# are not single chars.
    j = 0
    io = 0
    while j < n:
        if j >= m or order[io] == '-':
            result[j] = candidates[0]
            del candidates[0]
            j += 1
            io += 1
            continue
        elif order[j] == 't':
            oj = 'time'
            io += 1
        elif order[j] == 'x':
            oj = 'longitude'
            io += 1
        elif order[j] == 'y':
            oj = 'latitude'
            io += 1
        elif order[j] == 'z':
            oj = 'level'
            io += 1
        else:
            # later could put in escaped ids or indices
            raise CDMSError('Unknown character in order string')

        for i in range(n):
            if axisMatches(axes[candidates[i]], oj):
                result[j] = candidates[i]
                del candidates[i]
                break
        else:
            raise CDMSError("Axis requested in order specification not there")
        j += 1
    return result


def axisMatches(axis, specification):
    """
       Axis Matches

       Parameters
       ----------
       axis : See note below
       specifications : See note below

       Returns
       -------
       1 or 0 depending on whether axis matches the specification.

       Notes

       Specification must be one of:

       #. a string representing an axis id or one of the keywords time,
          fctau0, latitude or lat, longitude or lon, or lev or level.

       #. Axis may be surrounded with parentheses or spaces.

          * We first attempt to match the axis id and the specification.
          * Keywords try to match using isTime, isLatitude, etc.
          * Comparisons to keywords and axis ids is case-insensitive.

       #. a function that takes an axis as an argument and returns a value.
          * if the value returned is true, the axis matches.

       #. an axis object; will match if it is the same object as axis.
    """
    if isinstance(specification, string_types):
        s = specification.lower()
        s = s.strip()
        while s[0] == '(':
            if s[-1] != ')':
                raise CDMSError('Malformed axis spec, ' + specification)
            s = s[1:-1].strip()
        if axis.id.lower() == s:
            return True
        elif (s == 'time') or (s in time_aliases):
            return axis.isTime()
        elif (s == 'fctau0') or (s in forecast_aliases):
            return axis.isForecast()
        elif (s[0:3] == 'lat') or (s in latitude_aliases):
            return axis.isLatitude()
        elif (s[0:3] == 'lon') or (s in longitude_aliases):
            return axis.isLongitude()
        elif (s[0:3] == 'lev') or (s in level_aliases):
            return axis.isLevel()
        else:
            return False

    elif isinstance(specification, types.FunctionType):
        r = specification(axis)
        if r:
            return True
        else:
            return False

    elif isinstance(specification, AbstractAxis):
        return (specification is axis)

    raise CDMSError("Specification not acceptable: " +
                    str(type(specification)) + ', ' + str(specification))


def concatenate(axes, id=None, attributes=None):
    """Concatenate multiple axes including boundaries.

    Parameters
    ----------
    axes : Axes to concatenate
    id : New axis identification (default None)
    attributes : Attributes to attached to the new Axis

    Returns
    -------
    Transient axis.
    """

    data = numpy.ma.concatenate([ax[:] for ax in axes])
    boundsArray = [ax.getBounds() for ax in axes]
    if any(elem is None for elem in boundsArray):
        bounds = None
    else:
        bounds = numpy.ma.concatenate(boundsArray)
    return TransientAxis(data, bounds=bounds, id=id, attributes=attributes)


def take(ax, indices):
    """Take elements form an array along an axis

    Parameters
    ----------
    ax : The source array.
    indices : The indices of the values to extract.

    Returns
    -------
    axis : TransientAxis
        The return array has the same type of ax.
    """

    # Bug in ma compatibility module
    data = numpy.ma.take(ax[:], indices)
    abounds = ax.getBounds()
    if abounds is not None:
        bounds = numpy.ma.take(abounds, indices, axis=0)
    else:
        bounds = None
    return TransientAxis(data, bounds=bounds, id=ax.id,
                         attributes=ax.attributes)
