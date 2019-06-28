# Automatically adapted for numpy.oldnumeric Aug 01, 2007 by
# Further modified to be pure new numpy June 24th 2008

"""Bin index for non-rectilinear grids"""

from . import _bindex
import numpy


def bindexHorizontalGrid(latlin, lonlin):
    """Create a bin index for a horizontal grid.

    Parameters
    ----------
    latlin : latlin is the raveled latitude values.
    latlon : lonlin is the raveled longitude values.

    Returns
    -------
    resulting index.
    """
    lonlin = numpy.mod(lonlin, 360)
    NI, NJ = _bindex.getLens()
    # This should match NBINI, NBINJ in bindex.c
    head = numpy.zeros(NI * NJ, dtype='l')
    next = numpy.zeros(len(latlin), dtype='l')
    _bindex.bindex(latlin, lonlin, head, next)

    return (head, next)


def intersectHorizontalGrid(latspecs, lonspecs, latlin, lonlin, index):
    """Intersect a horizontal grid with a lat-lon region.

    Parameters
    ----------
    latspecs : latitude specs as defined in the grid module.
    lonspecs : longitude specs as defined in the grid module.
    latlin : latlin is the raveled latitude array.
    lonlin : lonlin is the raveled longitude array.
    index : index is the bin index as returned from bindex.

    Returns
    -------
    an array of indices, in latlin/lonlin, of the points in the intersection.
    """
    points = numpy.zeros(len(latlin), dtype='l')
    if latspecs is None:
        slat = -90.0
        elat = 90.0
        latopt = 'cc'
    else:
        slat = latspecs[0]
        elat = latspecs[1]
        latopt = latspecs[2]

    if slat > elat:
        tmp = slat
        slat = elat
        elat = tmp

    # If the longitude range is >=360.0, just intersect with the full range.
    # Otherwise, the points array could overflow and generate a seg fault.
    if lonspecs is None or abs(lonspecs[1] - lonspecs[0]) >= 360.0:
        slon = 0.0
        elon = 360.0
        lonopt = 'co'
    else:
        slon = lonspecs[0]
        elon = lonspecs[1]
        lonopt = lonspecs[2]

    if slon > elon:
        tmp = slon
        slon = elon
        elon = tmp

    npoints = _bindex.intersect(
        slat,
        slon,
        elat,
        elon,
        latlin,
        lonlin,
        index[0],
        index[1],
        points,
        latopt,
        lonopt)

    return points[:npoints]
