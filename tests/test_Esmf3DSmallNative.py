"""
$Id: testEsmf3DSmallNative.py 2389 2012-07-26 15:51:43Z dkindig $
3D Bilinear test of ESMF through esmf, regrid, and standalone
With and without masking
"""

import operator
import cdms2
import regrid2
import unittest
import ESMF
from regrid2 import esmf
from regrid2 import ESMFRegrid
from regrid2 import GenericRegrid
import numpy
import time
import os
from functools import reduce
try:
    from mpi4py import MPI
    has_mpi = True
except BaseException:
    has_mpi = False

import re
import warnings


ESMF.Manager(debug=True)


def esmfGrid(grid, cds, sloc):
    """
    @param grid ESMF grid
    @param cds list of coordinates
    @param sloc ESMF staggerlocation
    """
    # Destination Centers
    grid.add_coords(sloc)

    lo = grid.lower_bounds[sloc]
    hi = grid.upper_bounds[sloc]
    ndims = len(lo)
    # Dimensions for local processor
    Ntot = reduce(operator.mul, [hi[i] - lo[i] for i in range(ndims)])
    ijkBE = []
    shape = []
    for i in range(ndims):
        ind = (ndims - 1) - i
        ind = i
        ijkBE.append(slice(lo[ind], hi[ind], None))
        shape.append(hi[ind] - lo[ind])

    print(ijkBE)
    xyzPtr = []
    for i in range(ndims):
        xyzPtr.append(grid.get_coords(i, staggerloc=sloc))
        xyzPtr[i][:] = cds[i][ijkBE]
    shape = tuple(shape)

    return xyzPtr, ijkBE, shape


def makeGrid(nx, ny, nz):
    dims = (nz, ny, nx)
    dimb = (nz + 1, ny + 1, nx + 1)
    xbot, xtop, ybot, ytop, zbot, ztop = 1, 4, 1, 5, .5, 6
    xbob, xtob, ybob, ytob, zbob, ztob = .5, 4.5, .5, 5.5, 0, 6.5
    x = numpy.linspace(xbot, xtop, nx)
    y = numpy.linspace(ybot, ytop, ny)
    z = numpy.linspace(zbot, ztop, nz)

    xb = numpy.linspace(xbob, xtob, nx + 1)
    yb = numpy.linspace(ybob, ytob, ny + 1)
    zb = numpy.linspace(zbob, ztob, nz + 1)

    print((x, xb))
    print((y, yb))
    print((z, zb))

    xx = numpy.outer(numpy.ones(ny), x)
    yy = numpy.outer(y, numpy.ones(nx))
    ones = numpy.outer(numpy.ones(ny), numpy.ones(nx))
    xxx = numpy.outer(numpy.ones(nz), xx).reshape(dims)
    yyy = numpy.outer(numpy.ones(nz), yy).reshape(dims)
    zzz = numpy.outer(z, ones).reshape(dims)

    xxb = numpy.outer(numpy.ones(ny + 1), xb)
    yyb = numpy.outer(yb, numpy.ones(nx + 1))
    ones = numpy.outer(numpy.ones(ny + 1), numpy.ones(nx + 1))
    xxxb = numpy.outer(numpy.ones(nz + 1), xxb).reshape(dimb)
    yyyb = numpy.outer(numpy.ones(nz + 1), yyb).reshape(dimb)
    zzzb = numpy.outer(zb, ones).reshape(dimb)

    theVolume = [xxx, yyy, zzz]
    theBounds = [xxxb, yyyb, zzzb]

    theData = xxx * yyy + zzz

    return dims, theVolume, theData, theBounds


class TestESMPRegridderConserve(unittest.TestCase):
    def setUp(self):
        """
        Unit test set up
        """
        if has_mpi:
            self.pe = MPI.COMM_WORLD.Get_rank()
            self.np = MPI.COMM_WORLD.Get_size()
        else:
            self.pe = 0
            self.np = 1
        self.rootPe = 0

    def test1_3D_Native_Bilinear(self):
        if not has_mpi:
            warnings.warn("mpi4py needed for this test, skipping")
            return
        srcDims, srcXYZCenter, srcData, srcBounds = makeGrid(5, 4, 3)
        dstDims, dstXYZCenter, dstData, dstBounds = makeGrid(5, 4, 3)

        # Initialize the grids **without** coordinates
        maxIndex = numpy.array(dstDims, dtype=numpy.int32)
        dstGrid3D = ESMF.Grid(
            maxIndex,
            coord_sys=ESMF.CoordSys.CART,
            staggerloc=[
                ESMF.StaggerLoc.CENTER])
        maxIndex = numpy.array(srcDims, dtype=numpy.int32)
        srcGrid3D = ESMF.Grid(
            maxIndex,
            coord_sys=ESMF.CoordSys.CART,
            staggerloc=[
                ESMF.StaggerLoc.CENTER])

        # Populate the Grids
        dstXYZCtrPtr, dstIJKbe, dstCtrShape = esmfGrid(dstGrid3D, dstXYZCenter,
                                                       ESMF.StaggerLoc.CENTER_VCENTER)
        dstXYZCnrPtr, dstIJKbe, dstCnrShape = esmfGrid(dstGrid3D, dstBounds,
                                                       ESMF.StaggerLoc.CORNER_VFACE)
        srcXYZCtrPtr, srcIJKbe, srcCtrShape = esmfGrid(srcGrid3D, srcXYZCenter,
                                                       ESMF.StaggerLoc.CENTER_VCENTER)
        srcXYZCnrPtr, srcIJKbe, srcCnrShape = esmfGrid(srcGrid3D, srcBounds,
                                                       ESMF.StaggerLoc.CORNER_VFACE)

        # initialize the fields **without** data, after ESMP_GridAddCoord
        dstField = ESMF.Field(dstGrid3D, name='dstDataCtr',
                              staggerloc=ESMF.StaggerLoc.CENTER_VCENTER,
                              typekind=ESMF.TypeKind.R4)
        srcField = ESMF.Field(srcGrid3D, name='srcDataCtr',
                              staggerloc=ESMF.StaggerLoc.CENTER_VCENTER,
                              typekind=ESMF.TypeKind.R4)
        srcIntFd = ESMF.Field(srcGrid3D, name='srcDataCtr',
                              staggerloc=ESMF.StaggerLoc.CENTER_VCENTER,
                              typekind=ESMF.TypeKind.R4)

        # Populate the fields
        dstFieldPtr = dstField.data
        dstFieldPtr[:] = 0
        srcFieldPtr = srcField.data
        srcFieldPtr[:] = srcData[srcIJKbe]
        srcIntFdPtr = srcIntFd.data
        srcIntFdPtr[:] = -1

        srcMaskValues = numpy.array([1], numpy.int32)
        # Regrid
        regridOut = ESMF.Regrid(srcField, dstField,
                                src_mask_values=srcMaskValues,
                                dst_mask_values=None,
                                src_frac_field=None,
                                dst_frac_field=None,
                                regrid_method=ESMF.RegridMethod.BILINEAR,
                                unmapped_action=ESMF.UnmappedAction.IGNORE)
        regridOut(srcField, dstField)

        regridBck = ESMF.Regrid(dstField, srcIntFd,
                                src_mask_values=None,
                                dst_mask_values=None,
                                src_frac_field=None,
                                dst_frac_field=None,
                                regrid_method=ESMF.RegridMethod.BILINEAR,
                                unmapped_action=ESMF.UnmappedAction.IGNORE)
        regridBck(dstField, srcIntFd)

        minlsd, maxlsd = srcData.min(), srcData.max()
        minlsi, maxlsi = dstFieldPtr.min(), dstFieldPtr.max()
        minlii, maxlii = srcIntFdPtr.min(), srcIntFdPtr.max()
        minsd = MPI.COMM_WORLD.reduce(minlsd, op=MPI.MIN, root=self.rootPe)
        maxsd = MPI.COMM_WORLD.reduce(maxlsd, op=MPI.MAX, root=self.rootPe)
        minsi = MPI.COMM_WORLD.reduce(minlsi, op=MPI.MIN, root=self.rootPe)
        maxsi = MPI.COMM_WORLD.reduce(maxlsi, op=MPI.MAX, root=self.rootPe)
        minii = MPI.COMM_WORLD.reduce(minlii, op=MPI.MIN, root=self.rootPe)
        maxii = MPI.COMM_WORLD.reduce(maxlii, op=MPI.MAX, root=self.rootPe)

        if self.pe == self.rootPe:
            print((minsd, minsi))
            print((minsd, minii))
            print((maxsd, maxsi))
            print((maxsd, maxii))
            self.assertEqual(minsd, minsi)
            self.assertEqual(minsd, minii)
            self.assertEqual(maxsd, maxsi)
            self.assertEqual(maxsd, maxii)

    def xtest2_3D_Native_Conserve(self):
        srcDims, srcXYZCenter, srcData, srcBounds = makeGrid(5, 4, 3)
        dstDims, dstXYZCenter, dstData, dstBounds = makeGrid(5, 4, 3)

        # Establish the destination grid
        maxIndex = numpy.array(dstDims, dtype=numpy.int32)
        dstGrid3D = ESMF.Grid(
            maxIndex,
            num_peri_dims=0,
            coord_sys=ESMF.CoordSys.CART,
            staggerloc=[
                ESMF.StaggerLoc.CENTER])
        maxIndex = numpy.array(srcDims, dtype=numpy.int32)
        srcGrid3D = ESMF.Grid(
            maxIndex,
            num_peri_dims=0,
            coord_sys=ESMF.CoordSys.CART,
            staggerloc=[
                ESMF.StaggerLoc.CENTER])

        dstXYZCtrPtr, dstIJKCtrbe, dstCtrShape = esmfGrid(dstGrid3D, dstXYZCenter,
                                                          ESMF.StaggerLoc.CENTER_VCENTER)
        srcXYZCtrPtr, srcIJKCtrbe, srcCtrShape = esmfGrid(srcGrid3D, srcXYZCenter,
                                                          ESMF.StaggerLoc.CENTER_VCENTER)
        dstXYZCnrPtr, dstIJKCnrbe, dstCnrShape = esmfGrid(dstGrid3D, dstBounds,
                                                          ESMF.StaggerLoc.CORNER_VFACE)
        srcXYZCnrPtr, srcIJKCnrbe, srcCnrShape = esmfGrid(srcGrid3D, srcBounds,
                                                          ESMF.StaggerLoc.CORNER_VFACE)

        # initialize the fields **without** data
        dstField = ESMF.Field(dstGrid3D, name='dstDataCtr',
                              staggerloc=ESMF.StaggerLoc.CENTER_VCENTER,
                              typekind=ESMF.TypeKind.R4)
        srcField = ESMF.Field(srcGrid3D, name='srcDataCtr',
                              staggerloc=ESMF.StaggerLoc.CENTER_VCENTER,
                              typekind=ESMF.TypeKind.R4)
        srcIntFd = ESMF.Field(srcGrid3D, name='srcIntDataCtr',
                              staggerloc=ESMF.StaggerLoc.CENTER_VCENTER,
                              typekind=ESMF.TypeKind.R4)

        # Populate the fields
        dstFieldPtr = dstField.data[dstIJKCtrbe] = dstData * 0
        srcFieldPtr = srcField.data[:] = srcData
        srcIntFdPtr = srcIntFd.data

        srcIntFdPtr[:] = -1

        soInterpInterp = numpy.reshape(srcIntFdPtr, srcCtrShape)

        srcMaskValues = None
        # Regrid
        regridOut = ESMF.Regrid(srcField, dstField,
                                src_mask_values=srcMaskValues,
                                dst_mask_values=None,
                                src_frac_field=None,
                                dst_frac_field=None,
                                regrid_method=ESMF.RegridMethod.BILINEAR,
                                unmapped_action=ESMF.UnmappedAction.ERROR)
        regridOut(srcField, dstField)

        soInterp = numpy.reshape(dstFieldPtr, dstCtrShape)

        regridBck = ESMF.Regrid(dstField, srcIntFd,
                                src_mask_values=None,
                                dst_mask_values=None,
                                src_frac_field=None,
                                dst_frac_field=None,
                                regrid_method=ESMF.RegridMethod.BILINEAR,
                                unmapped_action=ESMF.UnmappedAction.ERROR)

        regridBck(dstField, srcIntFd)

        soInterpInterp = numpy.reshape(srcIntFdPtr, srcCtrShape)

        minlsd, maxlsd = srcData.min(), srcData.max()
        minlsi, maxlsi = soInterp.min(), soInterp.max()
        minlii, maxlii = soInterpInterp.min(), soInterpInterp.max()
        minsd = MPI.COMM_WORLD.reduce(minlsd, op=MPI.MIN, root=self.rootPe)
        maxsd = MPI.COMM_WORLD.reduce(maxlsd, op=MPI.MAX, root=self.rootPe)
        minsi = MPI.COMM_WORLD.reduce(minlsi, op=MPI.MIN, root=self.rootPe)
        maxsi = MPI.COMM_WORLD.reduce(maxlsi, op=MPI.MAX, root=self.rootPe)
        minii = MPI.COMM_WORLD.reduce(minlii, op=MPI.MIN, root=self.rootPe)
        maxii = MPI.COMM_WORLD.reduce(maxlii, op=MPI.MAX, root=self.rootPe)

        if self.pe == self.rootPe:

            self.assertEqual(minsd, minsi)
            self.assertEqual(minsd, minii)
            self.assertEqual(maxsd, maxsi)
            self.assertEqual(maxsd, maxii)

    def xtest3_mvESMFRegrid_pregenSlabs(self):
        print('\ntest3')
        srcDims, srcXYZCenter, srcData, srcBounds = makeGrid(5, 4, 3)
        dstDims, dstXYZCenter, dstData, dstBounds = makeGrid(5, 4, 3)

        ro = ESMFRegrid(srcXYZCenter[0].shape, dstXYZCenter[0].shape, srcData.dtype,
                        'conserve', 'center', 0, 'cart', staggerloc='center',
                        hasSrcBounds=True,
                        hasDstBounds=True)
        srcSlab = ro.getSrcLocalSlab('center')
        dstSlab = ro.getDstLocalSlab('center')
        srcCds = [coord[srcSlab] for coord in srcXYZCenter]
        dstCds = [coord[dstSlab] for coord in dstXYZCenter]
        srcSlab = ro.getSrcLocalSlab('vface')
        dstSlab = ro.getDstLocalSlab('vface')
        srcBnd = [bound[srcSlab] for bound in srcBounds]
        dstBnd = [bound[dstSlab] for bound in dstBounds]

        ro.setCoords(srcCds, dstCds,
                     srcBounds=srcBnd, dstBounds=dstBnd)
        ro.computeWeights()

        srcDataSec = numpy.array(srcData[srcSlab], srcData.dtype)
        dstDataSec = numpy.array(dstData[dstSlab], dstData.dtype)

        ro.apply(srcDataSec, dstDataSec, rootPe=None)

        print(('src', srcDataSec.min(), srcDataSec.max(), srcDataSec.shape))
        print(('dst', dstDataSec.min(), dstDataSec.max(), dstDataSec.shape))

        sA = ro.getSrcAreas(rootPe=self.rootPe)
        dA = ro.getDstAreas(rootPe=self.rootPe)
        sF = ro.getSrcAreaFractions(rootPe=self.rootPe)
        dF = ro.getDstAreaFractions(rootPe=self.rootPe)

    def Xtest4_mvESMFRegrid_esmfSlabs(self):
        print('\ntest4')
        srcDims, srcXYZCenter, srcData, srcBounds = makeGrid(5, 4, 3)
        dstDims, dstXYZCenter, dstData, dstBounds = makeGrid(5, 4, 3)

        ro = ESMFRegrid(srcXYZCenter[0].shape, dstXYZCenter[0].shape, srcData.dtype,
                        'conserve', 'center', 0, 'cart', staggerloc='center',
                        hasSrcBounds=True,
                        hasDstBounds=True)
        ro.setCoords(srcXYZCenter, dstXYZCenter,
                     srcBounds=srcBounds, dstBounds=dstBounds,
                     globalIndexing=True)
        ro.computeWeights()

        ro.apply(srcData, dstData, rootPe=self.rootPe, globalIndexing=True)
        print(('src', srcData.min(), srcData.max(), srcData.shape))
        print(('dst', dstData.min(), dstData.max(), dstData.shape))

        sA = ro.getSrcAreas(rootPe=self.rootPe)
        dA = ro.getDstAreas(rootPe=self.rootPe)
        sF = ro.getSrcAreaFractions(rootPe=self.rootPe)
        dF = ro.getDstAreaFractions(rootPe=self.rootPe)

    def xtest5_mvGenericRegrid(self):
        print('\ntest5')
        srcDims, srcXYZCenter, srcData, srcBounds = makeGrid(5, 4, 3)
        dstDims, dstXYZCenter, dstData, dstBounds = makeGrid(5, 4, 3)

        ro = GenericRegrid(srcXYZCenter, dstXYZCenter, srcData.dtype,
                           'conserve', 'esmf', staggerloc='center',
                           periodicity=0, coordSys='cart',
                           srcBounds=srcBounds, dstBounds=dstBounds)
        ro.computeWeights()

        diag = {'srcAreas': None, 'srcAreaFractions': None,
                'dstAreas': None, 'dstAreaFractions': None}
        ro.apply(srcData, dstData, rootPe=self.rootPe)
        print(('src', srcData.min(), srcData.max(), srcData.shape))
        print(('dst', dstData.min(), dstData.max(), dstData.shape))

        sA = diag['srcAreas']
        dA = diag['dstAreas']
        sF = diag['srcAreaFractions']
        dF = diag['dstAreaFractions']


if __name__ == '__main__':
    print("")  # Spacer
    ESMF.Manager(debug=True)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestESMPRegridderConserve)
    unittest.TextTestRunner(verbosity=1).run(suite)
