# Automatically adapted for numpy.oldnumeric Aug 02, 2007 by

import cdms2
import numpy
import copy
# from . import _regrid
import regrid2._regrid as _regrid
from .error import RegridError


class CrossSectionRegridder:
    """

        PURPOSE: To perform all the tasks required to regrid the input data into the ouput data in the
                 latitude-level plane for all times

        PROCEDURE: 
            Step One:
                  Make an instance of class CrossSectionRegridder passing it input and output grid information
            Step Two:
                  Pass the input data with some descriptive parameters and get the output data
                  in return

    """

    def __init__(self, latIn, latOut, levIn, levOut, latTypeIn=None, latSizeIn=None,
                 latTypeOut=None, latSizeOut=None):
        """
        To make an instance which entails setting up the input and output grids
        
        Parameters
        ----------
        latIn : the axis specifying the latitude grid for the input data
        latOut : the axis specifying the latitude grid for the output data
        levIn : the axis specifying the pressure grid for the input data
        levOut : the axis specifying the pressure grid for the output data

        * Additional information is required if a latitude grid is not global. It may be generic.
        Otherwise it is a subset of one of the standard global grids. Correspondingly, the choice
        for the grid type must be 'gaussian', 'equalarea', 'uniform' or 'generic'. In addition, the
        computation requires the size of the global grid from which the subset was choosen. Consequently,
        the user must assemble:

        latTypeIn : for input latitude, one of the following:
           * 'gaussian'
           * 'equalarea'
           * 'uniform'
           * 'generic'

        latSizeIn : for input latitude, the size of the goblal grid used in selecting the region
        latTypeOut : for output latitude, one of the following:
		   * 'gaussian'
		   * 'equalarea'
		   * 'uniform'
		   * 'generic'
        latSizeOut : for output latitude, the size of the goblal grid used in selecting the region
        
        Note
        ----
        To  make an instance preparing for a global to global regrid, type
           * r = CrossSectionRegridder(latIn, latOut, levIn, levOut)

        To  make an instance preparing for a global to a regional grid which, for example, is a subset of
        a global gaussian grid of size 64, type

           * r = CrossSectionRegridder(latIn, latOut, levIn, levOut, latTypeOut = 'gaussian', latSizeOut = 64)
                * where the latOut axis must have been selected from the global 64 length gaussian grid
        """

        # ---  set the instance grid data attributes used to describe input and output grid sizes

        self.latOut = latOut
        self.levIn = levIn
        self.levOut = levOut
        self.nlevi = len(levIn)
        self.nlevo = len(levOut)

        latIn, self.nlati = checkdimension(latIn, 'input latitude')
        latOut, self.nlato = checkdimension(latOut, 'output latitude')

        # --- check for a single grid point in the latitude-level plane

        if self.nlevo == 1 and self.nlato != 1:
            sendmsg(
                'Error  in output grid - a single level value requires a single latitude value')
            raise ValueError
        if self.nlevo != 1 and self.nlato == 1:
            sendmsg(
                'Error  in output grid - a single latitude value requires a single longitude value')
            raise ValueError
        if self.nlevo == 1 and self.nlato == 1:
            calculateMean = 1
            msg = 'Warning -- regridding a cross section to a single point does not produce the global mean'
            sendmsg(msg)
        else:
            calculateMean = 0

        # ---  get the latitude coordinate grid boundaries for the input grid

        if latTypeIn is None:                                                  # global latIn
            lat_wts_bndsIn = get_latitude_wts_bnds(latIn)
        else:
            lat_wts_bndsIn = get_region_latitude_wts_bnds(
                latIn, latTypeIn, latSizeIn)

        lat_bndsIn = lat_wts_bndsIn[1]
        bnin, bsin = latitude_bounds(lat_bndsIn)

        if calculateMean == 0:                                                   # meaningful grid

            # ---  get the latitude coordinate grid boundaries for the output grid

            if latTypeOut is None:                                                  # global latOut
                lat_wts_bndsOut = get_latitude_wts_bnds(latOut)
            else:
                lat_wts_bndsOut = get_region_latitude_wts_bnds(
                    latOut, latTypeOut, latSizeOut)

            lat_bndsOut = lat_wts_bndsOut[1]
            bnout, bsout = latitude_bounds(lat_bndsOut)

        else:
            bnout = numpy.array([90.0], numpy.float32)
            bsout = numpy.array([-90.0], numpy.float32)

        # ---  call maplength to get the rest of the self data needed by rgrdlength

        t = _regrid.maplength(self.nlati, self.nlato, bnin, bnout, bsin, bsout)

        self.latdx, self.latpt, self.wtlat = t

    def __call__(self, ar, missing=None, order=None, method="log"):
        """
        Call the regridder function.
        ar is the input array.
        missing is the missing data value, if any. It defaults to the missing/fill value
          defined for the input array, if any.
        order is of the form "tzyx", "tyx", etc.
        method is either 'log' to interpolate in the log of pressure, or 'linear' for linear interpolation.
        """

        from cdms2.avariable import AbstractVariable
        from cdms2.tvariable import TransientVariable

        # Save Variable metadata for output
        if isinstance(ar, AbstractVariable):
            attrs = copy.copy(ar.attributes)
            varid = ar.id
            axislist = list([x[0].clone() for x in ar.getDomain()])
            inputIsVariable = 1
            if order is None:
                order = ar.getOrder()
            # this expects contiguous arrays
            if isinstance(
                    ar, TransientVariable) and ar.iscontiguous() is False:
                ar = ar.ascontiguous()
        else:
            inputIsVariable = 0

        # Turn ar into a numpy array.
        if numpy.ma.isMaskedArray(ar):
            armiss = ar.fill_value
            ar = numpy.ma.filled(ar)
        elif isinstance(ar, AbstractVariable):
            tempar = ar.getValue(squeeze=0)
            armiss = ar.getMissing()
            ar = numpy.ma.filled(tempar)
        elif isinstance(ar, numpy.ndarray):
            armiss = None
        else:
            raise RegridError(
                "Input array is not a Variable, numpy.ma, or numpy array")

        # If neither mask nor missing value is specified, get them from
        # the input array.
        if missing is None:
            missing = armiss
        if isinstance(missing, numpy.ndarray):
            missing = missing[0]

        rank = len(ar.shape)
        assert 2 <= rank <= 3, 'Array rank is %i, must be 2, or 3' % rank

        # Set the default order to match the input grid order
        if order is None:
            if rank == 2:
                order = "zy"
            else:
                order = "tzy"

        assert rank == len(
            order), 'Order must be same length as array rank: %i' % len(ar.shape)

        order = str.lower(order)

        # Map order to positionIn
        positionIn = [None] * 3
        for i in range(len(order)):
            if order[i] == 'y':
                positionIn[0] = i
                if inputIsVariable:
                    axislist[i] = self.latOut
            elif order[i] == 'z':
                positionIn[1] = i
                if inputIsVariable:
                    axislist[i] = self.levOut
            else:
                positionIn[2] = i

        # Regrid
        if method == 'log':
            logYes = 'yes'
        else:
            logYes = 'no'
        outar = self.rgrd(ar, missing, 'greater', logYes, positionIn)

        # Reconstruct the same class as on input
        # Mask fill_value and return results
        if inputIsVariable == 1:
            result = numpy.ma.masked_values(outar, missing)
            result = cdms2.createVariable(result, fill_value=missing,
                                          axes=axislist, attributes=attrs, id=varid)
        else:
            result = numpy.ma.masked_array(outar, fill_value=missing)
            result = numpy.ma.masked_values(result, missing)

        return result

    def rgrd(self, dataIn, missingValueIn, missingMatch, logYes='yes',
             positionIn=None, maskIn=None, missingValueOut=None):
        """
        To perform all the tasks required to regrid the input data, dataIn, into the ouput data, dataout in
        the latitude-level plane.

        Parameters
        ----------
        dataIn : data to regrid

        missingValueIn : the missing data value to use in setting missing in the mask. It is required.
          * None -- there is no missing data
          * A number -- if  the value to use in the search for possible missing data.  
            The presence of missing data at a grid point leads to recording 0.0 in the mask.

        missingMatch : the comparison scheme used in searching for missing data in dataIn using the value passed in as missingValueIn. 
          * None -- used if None is the entry for missingValueIn
          * exact -- used if missingValue is the exact value from the file
          * greater -- the missing data value is equal to or greater than missingValueIn
          * less -- the missing data value is equal to or less than missingValueIn

        logYes : choose the level regrid as linear in log of level or linear in level. 
          * Set to 'yes' for log. Anything else is linear in level.

        positionIn : a tuple with the numerical position of the dimensions
          * in C or Python order specified in the sequence latitude,
            level and time. Latitude and level are required. If time is missing submit None in its
            slot in the tuple. Notice that the length of the tuple is
            always three.

            Explicitly, in terms of the shape of dataIn as returned by python's shape function

            positionIn[0] contains the position of latitude in dataIn
            positionIn[1] contains the position of level in dataIn or None
            positionIn[2] contains the position of time in dataIn or None

            If the c order shape of 3D data is
    		(number of times, number of levels, number of latitudes)
            submit
            (2, 1, 0).

            If the c order shape of 2D data is
            (number of times, number of latitudes)
            submit
            (1, None, 0).

            Send in None if the shape is a subset of (time, level, latitude) which is evaluated
            as follows:
    			* 2D -- code assumes (1,0,None)
    			* 3D -- code assumes (2,1,0)

        maskIn : an array of 1.0 and 0.0 values where the 0.0 value is used to mask the input data. 
          This mask only works on the latitude grid. It is not possible to mask out a region in the level
          plane. The 0.0 value removes the data from correponding grid point. The user can supply the
          following choices:

            * None -- an array of 1.0s is created followed by substituting 0.0s for grid points with missing
              data in the input data array, dataIn

            * array -- an array of 1.0s or 0.0s which must be either 2D or the actual size of the input data,
              dataIn. This user supplied mask might be used to mask a latitude region. It is not
              required to account for missing data in the input data. The code uses missingValueIn
              and missingMatch to supply the 0.0s for grid points with missing data in the input
              data array, dataIn.

        missingValueOut : the value for the missing data used in writing the output data. 
            * If left at the default entry, None, the code uses missingValueIn 
            * If present or as a last resort 1.0e20

        Returns
        -------
        dataOut : the regridded data

        Example
        -------

        To regrid dataIn into dataOut using all the defaults where None, None signifies no
        missing data.
			* dataOut = x.rgrd(dataIn, None, None)

        To regrid dataIn into dataOut using 1.0e20 and greater as the missing data
            * dataOut = x.rgrd(dataIn, 1.e20, 'greater')

        Note:  This code does not regrid cross sections which have a single dummy longitude value!
        """

        # check the required input -- dataIn, missingValueIn and  missingMatch

        # make sure that dataIn is an array

        try:
            len(dataIn)
        except TypeError:
            sendmsg('Error in calling the rgrd method -- dataIn must be an array')
            raise TypeError

        # try to identify a single dummy longitude

        dataShape = dataIn.shape

        if len(dataShape) > 3:
            msg = 'Error in call to rgrd -- cross section data can not have more than 3 dimensions'
            sendmsg(msg)
            raise TypeError

        if positionIn is not None:
            if self.nlati != (dataShape[positionIn[0]]):
                msg = 'Latitude vector is inconsistent with input data'
                sendmsg(msg)
                raise ValueError

            if self.nlevi != (dataShape[positionIn[1]]):
                msg = 'Level vector is inconsistent with input data'
                sendmsg(msg)
                raise ValueError

        # check the missingValueIn pass

        if missingValueIn is not None:
            try:
                abs(missingValueIn)
            except TypeError:
                sendmsg(
                    'Error in calling the rgrd method -- missingvalueIn must be None or a number. Now it is  ',
                    missingValueIn)
                raise TypeError

        # check the missingMatch pass

        missingPossibilities = ['greater', 'equal', 'less', None]
        if missingMatch not in missingPossibilities:
            msg = 'Error in missingMatch -- it must be None or the string greater, equal, or less. Now it is '
            sendmsg(msg, missingMatch)
            raise ValueError

        # set missing value to be used in dataOut

        if missingValueOut is None:
            if missingValueIn is not None:
                # default
                omit = missingValueIn
            else:
                # default
                omit = 1.0e20
        else:
            # user choice
            omit = missingValueOut

        # --- Check data type and change to float if necessary ----

        if dataIn.dtype.char != 'f':
            dataIn = dataIn.astype(numpy.float32)

        # produce the input for rgdlength not generated by maplength

        dataShape = dataIn.shape
        numberDim = len(dataShape)

        if numberDim < 2:
            msg = 'Error in call to rgrd -- data must have at least 2 dimensions'
            sendmsg(msg)
            raise TypeError

        if positionIn is None:               # construct the default positionIn tuple
            positionList = []
            for n in range(numberDim):       # insert a sequence of numbers
                positionList.append(n)
            positionList.reverse()

            if numberDim == 2:               # fill end of list with a None
                positionList.append(None)

            positionIn = tuple(positionList)

        if len(positionIn) != 3:
            msg = 'Error in call to rgrd -- positionIn must be a tuple of length 3'
            sendmsg(msg)
            raise TypeError

        # set ilon, ilat in Fortran order except that the first index is 0 -
        # not 1
        ilat = numberDim - 1 - positionIn[0]

        itim1 = itim2 = -1
        ntim1 = ntim2 = 0

        if numberDim == 2:                         # lat and level field
            itim1 = numberDim - 1 - positionIn[1]
            ntim1 = dataShape[positionIn[1]]

        if numberDim == 3:                         # lon_lat field + level + time
            itim1 = numberDim - 1 - positionIn[1]
            ntim1 = dataShape[positionIn[1]]
            itim2 = numberDim - 1 - positionIn[2]
            ntim2 = dataShape[positionIn[2]]

        # check for consistency between the grid axiss and the dataIn shape

        if self.nlati != (dataShape[positionIn[0]]):
            msg = 'Latitude vector is inconsistent with input data'
            sendmsg(msg)
            raise ValueError

        if self.nlevi != (dataShape[positionIn[1]]):
            msg = 'Level vector is inconsistent with input data'
            sendmsg(msg)
            raise ValueError

        # allocate memory for aout -- the array with original number of levels
        # but the new number of latitudes

        aoutList = list(dataIn.shape)
        aoutList[positionIn[0]] = self.nlato
        # memory for aout
        aout = numpy.zeros(tuple(aoutList), numpy.float32)

        # generate the mask

        amskin = sectionmask(
            dataIn,
            positionIn,
            maskIn,
            missingValueIn,
            missingMatch)

        #      ------------- call rgdlength to regrid latitude  ---------------

        _regrid.rgdlength(
            ilat,
            itim1,
            itim2,
            ntim1,
            ntim2,
            self.nlati,
            self.nlato,
            omit,
            self.latdx,
            self.latpt,
            self.wtlat,
            amskin,
            dataIn,
            aout)

        #      ------------- call rgdpressure to regrid pressure  -------------

        # allocate memory for ap -- the array with new number of levels and the
        # new number of latitudes

        apList = list(dataIn.shape)
        apList[positionIn[0]] = self.nlato
        apList[positionIn[1]] = self.nlevo
        # memory for ap
        ap = numpy.zeros(tuple(apList), numpy.float32)

        nlon = 0
        if missingMatch is None:                                                # if no missing do not pass None
            missingMatch = 'none'

        # if no missing do not pass None
        if missingValueIn is None:
            missingValueIn = 1.333e33

        if logYes != 'yes':
            logYes = 'no'

        levIn = self.levIn[:].astype(numpy.float64)
        levOut = self.levOut[:].astype(numpy.float64)
        _regrid.rgdpressure(
            self.nlevi,
            self.nlevo,
            self.nlato,
            nlon,
            ntim2,
            missingValueIn,
            missingMatch,
            logYes,
            levIn,
            levOut,
            aout,
            ap)

        if missingMatch == 'none':                    # if no missing do not pass None
            missingMatch = None
        if missingValueIn == 1.333e33:
            missingValueIn = None

        return ap


def checkdimension(x, name):
    """
    Purpose : dimension  checks
              1. has a len method
              2. data type is float32
              3. monotonically increasing vectors

    Parameters
    ----------
    x : coordinate vector

    name : coordinate vector ID

    Returns
    -------
    x, xsize -- dimension vector and its size
    """

    data = x[:]
    try:
        xsize = len(x)
    except TypeError:
        sendmsg('Hgrid instance error -- instance requires a ' + name)
        raise TypeError

    if data.dtype.char != 'f':
        x[:] = x[:].astype(numpy.float32)

    # -----  check for consistency  -----

    if x[0] > x[xsize - 1]:
        for n in range(1, xsize):
            if x[n] > x[n - 1]:
                sendmsg('Hgrid instance error -- ' + name + 'not monotonic')
                raise ValueError
                return
    else:
        for n in range(1, xsize):
            if x[n] < x[n - 1]:
                sendmsg('Hgrid instance error -- ' + name + 'not monotonic')
                raise ValueError
                return

    return x, xsize


def generic_wts_bnds(lat):
    try:
        bnds = lat.getBounds()
        if bnds is None:  # No bounds defined
            newLat = lat.clone()
            newLat.setBounds(None)
        bnds = lat.getBounds()
    except BaseException:  # just an array....
        newLat = cdms2.createAxis(lat)
        newLat.setBounds(None)
        bnds = newLat.getBounds()
    outBnds = bnds[:, 0].tolist()
    outBnds.append(bnds[-1][-1])
    outBnds = numpy.array(outBnds)
    wts = [outBnds[i + 1] - outBnds[i] for i in range(len(lat))]
    wts = numpy.array(wts) / numpy.sum(wts)
    return wts, outBnds


def get_latitude_wts_bnds(checklatpass):
    """get_latitude_wts_bnds

    Compare the passed checklatpass with the correct geophysical ones
    calculated here. After finding a match call the function to get the bounds.

    wts,bnds = get_latitude_wts_bnds(checklatpass)

    Parameters
    ----------
    checklatpass : is the grid to check

    Returns
    -------
    wts, bnds - tuple with weights and bounds

    """
    small = 0.001                     # use as tolerance in checking values

    nlat = len(checklatpass)

    reverse_latitude = 'no'

    # ------ set latitude direction to n to s for comparisons -------

    if checklatpass[0] < checklatpass[nlat -
                                      1]:                         # need a copy?
        checklat = numpy.array(checklatpass, numpy.float64)
        checklat = checklat[::-1]
        reverse_latitude = 'yes'
    else:
        checklat = checklatpass

    # ------ check the pass for evenly spaced latitudes -------

    firstdelta = abs(checklat[0] - checklat[1])
    maxdiff = 0.0
    for i in range(1, nlat - 1):
        diff = abs(firstdelta - (checklat[i] - checklat[i + 1]))
        if diff > maxdiff:
            maxdiff = diff

    if maxdiff < small:
        #        if abs(90. - checklat[0]) > small or abs(-90. -
        #                                                 checklat[nlat - 1]) > small:
        #            grid_type = 'even'                                # evenly spaced without poles
        #            wts, bnds = generic_wts_bnds(checklat)
        #            if reverse_latitude == 'yes':
        #                wts = wts[::-1]
        #                bnds = bnds[::-1]
        #            return (wts, bnds)
        #        else:
        grid_type = 'uniform'                             # evenly spaced with poles
        pts_wts_bnds = _regrid.gridattr(nlat, grid_type)
        wts = pts_wts_bnds[1]
        bnds = pts_wts_bnds[2]
        if reverse_latitude == 'yes':
            wts = wts[::-1]
            bnds = bnds[::-1]
        return (wts, bnds)

    # ------ check the pass for gaussian latitudes -------

    grid_type = 'gaussian'
    pts_wts_bnds = _regrid.gridattr(nlat, grid_type)
    latvals = pts_wts_bnds[0]
    laterror = max(abs(latvals - checklat))
    if laterror < small:
        wts = pts_wts_bnds[1]
        bnds = pts_wts_bnds[2]
        if reverse_latitude == 'yes':
            wts = wts[::-1]
            bnds = bnds[::-1]
        return (wts, bnds)

    # ------ check the pass for equalarea latitudes -------

    grid_type = 'equalarea'
    pts_wts_bnds = _regrid.gridattr(nlat, grid_type)
    latvals = pts_wts_bnds[0]
    laterror = max(abs(latvals - checklat))
    if laterror < small:
        wts = pts_wts_bnds[1]
        bnds = pts_wts_bnds[2]
        if reverse_latitude == 'yes':
            wts = wts[::-1]
            bnds = bnds[::-1]
        return (wts, bnds)

    # ------ must be generic latitude -------
    wts, bnds = generic_wts_bnds(checklatpass)
    return (wts, bnds)


def latitude_bounds(lat_bnds):
    """

    Purpose:

    set up the shape and bounds for use by maparea

    Usage:

    Returns
    -------

    tuple ( bn,bs )

    """

    latbnds = lat_bnds.astype(numpy.float32)

    if latbnds[0] > latbnds[len(latbnds) - 1]:
        bn = latbnds[:-1]
        bs = latbnds[1:]
    else:
        bn = latbnds[1:]
        bs = latbnds[:-1]

    return (bn, bs)


def get_region_latitude_wts_bnds(latRegionpass, latType, latSize):
    """

    Routine : get_region_latitude_wts_bnds

    Purpose : compare the passed latitudes, latRegion, with the global
              ones calculated here and extract the wts and bounds for
             the region

    Usage : wts,bnds = get_region_latitude_wts_bnds(latRegion, latType, latSize)
            where latRegion is the regional grid to check

    Returns
    -------

    wts, bnds - tuple with weights and bounds

    """

    latTypeList = ['gaussian', 'equalarea', 'uniform', 'generic']

    if latType not in latTypeList:
        sendmsg(
            "Error in latType -- it must be 'gaussian', 'equalarea', 'even' or 'generic' and not ",
            latType)
        raise ValueError
        return

    if latSize is None:
        sendmsg('Error in latSize -- it must be a number')
        raise ValueError
        return

    nlat = len(latRegionpass)
    reverse_latitude = 'no'

    # ------ set latitude direction to n to s for comparisons -------

    if latRegionpass[0] < latRegionpass[nlat -
                                        1]:                         # need a copy?
        latRegion = numpy.array(latRegionpass, numpy.float64)
        latRegion = latRegion[::-1]
        reverse_latitude = 'yes'
    else:
        latRegion = latRegionpass

    small = 0.001                     # use as tolerance in checking values

    # ------ check the pass for gaussian latitudes -------

    if latType != 'generic':
        # n to s global pts, wts and bnds
        pts_wts_bnds = _regrid.gridattr(latSize, latType)
        latvals = pts_wts_bnds[0]

        imatch = -1
        i = 0
        while(imatch == -1):
            if abs(latvals[i] - latRegion[0]) < small:    # first index found
                startIndex = i
                imatch = 0
            i = i + 1
        imatch = -1
        while(imatch == -1):
            if abs(latvals[i] - latRegion[nlat - 1]
                   ) < small:    # last index found
                lastIndex = i
                imatch = 0
            i = i + 1

        wts = pts_wts_bnds[1][startIndex:lastIndex + 1]
        bnds = pts_wts_bnds[2][startIndex:lastIndex + 2]

        if reverse_latitude == 'yes':
            wts = wts[::-1]
            bnds = bnds[::-1]

        return (wts, bnds)

#    else:                            # must be generic latitude -------
#
#        wts, bnds = generic_wts_bnds(latIn)
#        if reverse_latitude == 'yes':
#            wts = wts[::-1]
#            bnds = bnds[::-1]
#        return (wts, bnds)


def sectionmask(dataIn, positionIn, maskIn, missingValueIn, missingMatch):
    """

    Purpose : construct the mask for the input data for use by rgdlength

    Usage : amskin = mask(dataIn, positionIn, maskIn, missingValueIn, missingValueOut, flag2D)

    Returns
    -------

    amskin

    """
    # Logic outline
    # START NO USER MASK SECTION ?
    #
    # START USER MASK SECTION ?
    #    USER SUPPLIED MASK IS 2D ?
    #    USER SUPPLIED MASK IS FULL SIZE ?

    # ---- check the missingMatch pass --------

    missingPossibilities = ['greater', 'equal', 'less', None]
    if missingMatch not in missingPossibilities:
        msg = 'Error in missingMatch -- it must be None or the string greater, equal, or less'
        sendmsg(msg)
        raise ValueError

    # ----- Check for missing data in dataIn, set missingFlag and miss, the va

    # missingFlag = 0 if there is no missing data
    # missingFlag = 1 if there is missing data found using greater than missingValueIn
    # missingFlag = 1 if there is missing data found using the default 1.0e20
    # missingFlag = 2 if there is missing data found using equal to missingValueIn
    # missingFlag = 3 if there is missing data found using less than
    # missingValueIn

    missingFlag = 0

    # use value from the file
    if missingValueIn is not None:

        if missingMatch == 'greater':
            if missingValueIn > 0:
                miss = 0.99 * missingValueIn
            else:
                miss = 1.01 * missingValueIn
            n = numpy.add.reduce(
                numpy.where(
                    numpy.greater(
                        numpy.ravel(dataIn),
                        miss),
                    1,
                    0))
            if n > 0:
                missingFlag = 1

        elif missingMatch == 'equal':
            miss = missingValueIn
            n = numpy.add.reduce(
                numpy.where(
                    numpy.equal(
                        numpy.ravel(dataIn),
                        miss),
                    1,
                    0))
            if n > 0:
                missingFlag = 2

        elif missingMatch == 'less':
            if missingValueIn > 0:
                miss = 1.01 * missingValueIn
            else:
                miss = 0.99 * missingValueIn
            n = numpy.add.reduce(
                numpy.where(
                    numpy.less(
                        numpy.ravel(dataIn),
                        miss),
                    1,
                    0))
            if n > 0:
                missingFlag = 3

    # ----- get the shape of dataIn and set the number of dimensions in the da

    dataShape = dataIn.shape
    # set size and check against positionIn
    numberDataDim = len(dataShape)

    # remove the None fillers
    reducedPositionIn = []
    for i in range(len(positionIn)):
        if positionIn[i] is not None:
            reducedPositionIn.append(positionIn[i])

    if numberDataDim != len(reducedPositionIn):
        msg = 'positionIn does not describe the number of dimensions in the data'
        sendmsg(msg)
        raise ValueError

    # ----- Determine the order of latitude and level in the data -------

    # sequence is standard (lat,lon)
    if positionIn[0] > positionIn[1]:
        levlatFlag = 1
    else:
        levlatFlag = 0

    # ------------------------------------------------------------------------------------------------------
    # -----------------------------------------  Generate the mask -----------
    # ------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------
    # ---------- START NO USER MASK SECTION

    if maskIn is None:                                        # ---- need to generate the mask from scratch ----

        # allocate memory
        amskin = numpy.ones(dataShape, numpy.float32)

    # ---------- START USER MASK SECTION

    else:                                                   # ---- use the users supplied mask ----

        numberMaskDim = len(maskIn.shape)

        if numberMaskDim == 2:  # ----------------------- USER SUPPLIED MASK IS 2D

            # mask shape is (lat,lon)
            if levlatFlag == 1:
                checkmaskShape = (
                    dataShape[positionIn[1]], dataShape[positionIn[0]])
            # mask shape is (lon,lat)
            else:
                checkmaskShape = (
                    dataShape[positionIn[0]], dataShape[positionIn[1]])

            if maskIn.shape != checkmaskShape:                                             # check the mask shape
                msg = 'Error -- 2D mask supplied mask must have the same shape as corresponding slice in the input data'
                sendmsg(msg)
                raise IndexError

            # FINAL MASK IS FULL SIZED WITH USERS 2D MASK REPLICATED

            if numberDataDim > 2:
                # replicate the mask to size of dataIn
                amskin = numpy.resize(maskIn, dataShape)

        else:                                                 # ----------------------   USER SUPPLIED MASK IS FULL SIZE

            amskin = maskIn

            if numberMaskDim != numberDataDim:
                msg = 'Error -- user supplied mask must be 2D or the size of the data'
                sendmsg(msg)
                raise IndexError

            if amskin.shape != dataIn.shape:
                msg = 'Error -- full size mask supplied must have the same shape as the input data'
                sendmsg(msg)
                raise IndexError

    # there is missing data in dataIn to add to amskin
    if missingFlag != 0:
        if missingFlag == 1:
            amskin = numpy.where(numpy.greater(dataIn, miss), 0.0, amskin)
        elif missingFlag == 2:
            amskin = numpy.where(numpy.equal(dataIn, miss), 0.0, amskin)
        elif missingFlag == 3:
            amskin = numpy.where(numpy.greater(dataIn, miss), 0.0, amskin)

    amskin = amskin.astype(numpy.float32)

    return amskin


def sendmsg(msg, value1=None, value2=None):
    """

    Purpose : send the same message to the screen

    Passed : msg - the string


    Parmeters
    ---------
    value : the number associated with the string

    Returns
    -------

    return

    """

    print('*******************************************************************')
    if value1 is None:
        print(msg)
    elif value2 is None:
        print((msg, value1))
    else:
        print((msg, value1, value2))
    print('*******************************************************************')

    return None


def section(latvals, levvals):
    """

    Purpose : make the crossi section analytical test case

    Passed : the grid coordinate vectors

    Returns
    -------

    xsection : a temerature like cross section

    """

    nlev = len(levvals)

    nlat = len(latvals)
    theta = (math.pi / 180.) * latvals

    xsection = numpy.zeros((nlev, nlat), numpy.float32)     # memory

    t0 = 60.
    p0 = 1000.

    for j in range(nlat):
        for i in range(nlev):
            x = math.cos(theta[j])**2
            y = t0 * ((levvals[i] / p0)**.3)
            xsection[i, j] = x * y - 30.

    return xsection


def rmserror(data1, data2):
    """

    Purpose : compute the rms error for two data sets having the same shape


    Passed : the two data sets


    Returns
    -------

    rms error

   """

    if data1.shape != data2.shape:
        print('Error in shape in rmserror')
        print(('data1 shape = ', data1.shape))
        print(('data2 shape = ', data2.shape))
        raise ValueError

    d1 = numpy.ravel(data1)
    d2 = numpy.ravel(data2)

    sq = (d1 - d2) * (d1 - d2)
    error = numpy.sum(sq) / len(d1)
    rmserror = numpy.sqrt(error)

    return rmserror


if __name__ == '__main__':
    import math

    latIn = cdms2.createUniformLatitudeAxis(90.0, 46, -4.0)
    levList = [10., 40., 75., 100., 150., 250., 350., 500.,
               650., 850., 1000.]                  # pick some levels
    levIn = cdms2.createAxis(numpy.array(levList, numpy.float64), id='level')
    latOut = cdms2.createGaussianAxis(64)
    levList = [10., 30., 50., 70., 100., 200., 300., 400.,
               500., 700., 850., 1000.]         # pick some levels
    levOut = cdms2.createAxis(numpy.array(levList, numpy.float64), id='level')

    xregridf = CrossSectionRegridder(latIn, latOut, levIn, levOut)

    # make some artificial data
    dataIn = section(latIn[:], levIn[:])
    var = cdms2.createVariable(
        dataIn, axes=(
            levIn, latIn), attributes={
            'units': 'N/A'}, id='test')

    dataOut = xregridf(dataIn)

    # make the exact answer
    dataCheck = section(latOut[:], levOut[:])
    # find the rms error
    error = rmserror(dataOut, dataCheck)

    print('expected cross section test case rms error =  0.18581882')
    # print 'expected cross section test case rms error =  0.23062'
    print(('calculated cross section test case rms error = ', error))
