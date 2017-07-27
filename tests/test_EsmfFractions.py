"""
$Id: testEsmfFractions.py 2354 2012-07-11 15:28:14Z pletzer $

Unit test for src/dst AreaFractions return nan. It only fails in tripolar grids.

"""

import operator
import numpy
import cdat_info
import cdms2
import regrid2.esmf
import regrid2
import unittest
import time
import ESMF
import copy
from functools import reduce
try:
    from mpi4py import MPI
    has_mpi = True
except BaseException:
    has_mpi = False
import sys

PLOT = False
if PLOT:
    from matplotlib import pylab as pl


class Test(unittest.TestCase):
    def setUp(self):
        pass

    def test1_2d_esmf_native_tripolar_fraction(self):

        if has_mpi:
            mype = MPI.COMM_WORLD.Get_rank()
        else:
            mype = 0

        f = cdms2.open(cdat_info.get_sampledata_path() +
                       '/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc')
        so = f('so')[0, 0, :, :]

        h = cdms2.open(cdat_info.get_sampledata_path() +
                       '/so_Omon_HadGEM2-CC_historical_r1i1p1_185912-186911_2timesteps.nc')
        hadGEM2Model = h('so')[0, 0, ...]

        ny, nx = so.shape
        soBounds = so.getGrid().getBounds()

        srcLatCorner = numpy.zeros((ny + 1, nx + 1), numpy.float32)
        srcLatCorner[:ny, :nx] = soBounds[0][:, :, 0]
        srcLatCorner[:ny, nx] = soBounds[0][:ny, nx - 1, 1]
        srcLatCorner[ny, nx] = soBounds[0][ny - 1, nx - 1, 2]
        srcLatCorner[ny, :nx] = soBounds[0][ny - 1, :nx, 3]

        srcLonCorner = numpy.zeros((ny + 1, nx + 1), numpy.float32)
        srcLonCorner[:ny, :nx] = soBounds[1][:, :, 0]
        srcLonCorner[:ny, nx] = soBounds[1][:ny, nx - 1, 1]
        srcLonCorner[ny, nx] = soBounds[1][ny - 1, nx - 1, 2]
        srcLonCorner[ny, :nx] = soBounds[1][ny - 1, :nx, 3]

        srcCells = [so.getLatitude(), so.getLongitude()]
        srcNodes = [srcLatCorner, srcLonCorner]

        clt = cdms2.open(cdat_info.get_sampledata_path() +
                         '/clt.nc')('clt')[0, :, :]
        cltBounds = clt.getGrid().getBounds()

        ny, nx = clt.shape

        # clt grid is rectilinear, transform to curvilinear
        CLGrid = clt.getGrid().toCurveGrid()
        #lats = CLGrid.getLatitude()[:].data
        lons = CLGrid.getLongitude()[:].data

        # Make the bounds go from -90, 90 with uniform spacing and the
        # Cell Centers go from -88.something to 88.something
        yb = numpy.linspace(-90, 90, ny + 1)
        interval = abs(yb[0] - yb[1])
        y = numpy.linspace(-90 + interval / 2., 90 - interval / 2., ny)
        lats = numpy.outer(y, numpy.ones((nx), numpy.float32))

        ny, nx = clt.shape
        #yb = numpy.zeros((ny+1,), numpy.float32)
        #yb[:ny] = cltBounds[0][:, 0]
        #yb[ny] = cltBounds[0][ny-1, 1]
        xb = numpy.zeros((nx + 1,), numpy.float32)
        xb[:nx] = cltBounds[1][:, 0]
        xb[nx] = cltBounds[1][nx - 1, 1]

        # make curvilinear
        dstLatCorner = numpy.outer(yb, numpy.ones((nx + 1,), numpy.float32))
        dstLonCorner = numpy.outer(numpy.ones((ny + 1,), numpy.float32), xb)

        dstCells = [lats, lons]
        dstNodes = [dstLatCorner, dstLonCorner]

        print 'running test2_2d_esmf_native_tripolar_fraction...'
        tic = time.time()
        # create grid
        srcMaxIndex = numpy.array(so.shape, dtype=numpy.int32)
        srcGrid = ESMF.Grid(
            srcMaxIndex,
            num_peri_dims=0,
            coord_sys=ESMF.CoordSys.SPH_DEG,
            staggerloc=[
                ESMF.StaggerLoc.CENTER])
        srcLoCenter = srcGrid.lower_bounds[ESMF.StaggerLoc.CENTER]
        srcHiCenter = srcGrid.upper_bounds[ESMF.StaggerLoc.CENTER]
        srcDimsCenter = [srcLoCenter, srcHiCenter]

        srcGrid.add_coords(staggerloc=ESMF.StaggerLoc.CORNER)
        srcLoCorner = srcGrid.lower_bounds[ESMF.StaggerLoc.CORNER]
        srcHiCorner = srcGrid.upper_bounds[ESMF.StaggerLoc.CORNER]
        srcDimsCorner = [srcLoCorner, srcHiCorner]

        srcXCenter = srcGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CENTER)
        srcYCenter = srcGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CENTER)
        srcXCorner = srcGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CORNER)
        srcYCorner = srcGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CORNER)

        dstMaxIndex = numpy.array(clt.shape, dtype=numpy.int32)
        dstGrid = ESMF.Grid(
            dstMaxIndex,
            num_peri_dims=0,
            coord_sys=ESMF.CoordSys.SPH_DEG,
            staggerloc=[
                ESMF.StaggerLoc.CENTER])
        dstLoCenter = dstGrid.lower_bounds[ESMF.StaggerLoc.CENTER]
        dstHiCenter = dstGrid.upper_bounds[ESMF.StaggerLoc.CENTER]
        dstDimsCenter = [dstLoCenter, dstHiCenter]

        dstGrid.add_coords(staggerloc=ESMF.StaggerLoc.CORNER)
        dstLoCorner = dstGrid.lower_bounds[ESMF.StaggerLoc.CORNER]
        dstHiCorner = dstGrid.upper_bounds[ESMF.StaggerLoc.CORNER]
        dstDimsCorner = [dstLoCorner, dstHiCorner]

        dstXCenter = dstGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CENTER)
        dstYCenter = dstGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CENTER)
        dstXCorner = dstGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CORNER)
        dstYCorner = dstGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CORNER)

        # mask
        srcGrid.add_item(item=ESMF.GridItem.MASK)
        srcMask = srcGrid.get_item(item=ESMF.GridItem.MASK)

        # create field
        srcFld = ESMF.Field(srcGrid, name='srcFld',
                            typekind=ESMF.TypeKind.R8,
                            staggerloc=ESMF.StaggerLoc.CENTER)
        srcFldPtr = srcFld.data

        dstFld = ESMF.Field(dstGrid, name='dstFld',
                            typekind=ESMF.TypeKind.R8,
                            staggerloc=ESMF.StaggerLoc.CENTER)
        dstFldPtr = dstFld.data

        # Create the field for the fractional areas
        srcFracFld = ESMF.Field(srcGrid, name='srcFrac',
                                typekind=ESMF.TypeKind.R8,
                                staggerloc=ESMF.StaggerLoc.CENTER)
        srcFracPtr = srcFracFld.data
        dstFracFld = ESMF.Field(dstGrid, name='dstFrac',
                                typekind=ESMF.TypeKind.R8,
                                staggerloc=ESMF.StaggerLoc.CENTER)
        dstFracPtr = dstFracFld.data

        # set coords, mask, and field values for src and dst

        srcXCenter[:] = srcCells[1][:]
        srcYCenter[:] = srcCells[0][:]
        srcXCorner[:] = srcNodes[1][:]
        srcYCorner[:] = srcNodes[0][:]
        srcFldPtr[:] = so[:]
        srcMask[:] = (srcFldPtr == so.missing_value)

        srcFracPtr[:] = -999
        dstFracPtr[:] = -999

        dstNtotCenter = reduce(
            operator.mul, [
                dstDimsCenter[1][i] - dstDimsCenter[0][i] for i in range(2)])
        dstNtotCorner = reduce(
            operator.mul, [
                dstDimsCorner[1][i] - dstDimsCorner[0][i] for i in range(2)])

        dstXCenter[:] = dstCells[1][:]
        dstXCenter[:] = dstCells[0][:]
        dstXCorner[:] = dstNodes[1][:]
        dstYCorner[:] = dstNodes[0][:]
        dstFldPtr[:] = 0

        srcAreaFld = ESMF.Field(srcGrid, name='srcArea')
        dstAreaFld = ESMF.Field(dstGrid, name='dstArea')

        # regrid forward and backward
        maskVals = numpy.array([1], numpy.int32)  # values defining mask
        regrid1 = ESMF.Regrid(srcFld, dstFld,
                              src_mask_values=maskVals,
                              dst_mask_values=None,
                              regrid_method=ESMF.RegridMethod.CONSERVE,
                              unmapped_action=ESMF.UnmappedAction.IGNORE,
                              src_frac_field=srcFracFld,
                              dst_frac_field=dstFracFld)

        regrid1(srcFld, dstFld)

        srcAreas = srcAreaFld.get_area()
        dstAreas = dstAreaFld.get_area()

        srcAreaPtr = srcAreaFld.data
        dstAreaPtr = dstAreaFld.data

        if mype == 0:
            srcHasNan = numpy.any(numpy.isnan(srcFracPtr))
            dstHasNan = numpy.any(numpy.isnan(dstFracPtr))

            aa = numpy.isnan(srcFracPtr)
            bb = numpy.isnan(dstFracPtr)

            cc = srcFldPtr == 0
            dd = dstFldPtr == 0

            if PLOT:
                pl.figure(1)
                pl.subplot(2, 1, 1)
                pl.pcolor(numpy.reshape(aa, so.shape))
                pl.colorbar()
                pl.title('source')
                pl.subplot(2, 1, 2)
                pl.pcolor(numpy.reshape(bb, clt.shape))
                pl.colorbar()
                pl.title('destination')
                pl.suptitle("Red == location of nan's")

            print srcHasNan, dstHasNan

            # Do they have nans?
            self.assertFalse(srcHasNan, True)
            self.assertFalse(dstHasNan, True)

            jbeg, jend = dstDimsCenter[0][1], dstDimsCenter[1][1]
            ibeg, iend = dstDimsCenter[0][0], dstDimsCenter[1][0]
            soInterp = dstFldPtr

        toc = time.time()

        # clean up
        regrid1.destroy()
        dstFld.destroy()
        dstGrid.destroy()
        srcFld.destroy()
        srcGrid.destroy()


if __name__ == '__main__':
    print ""
    ESMF.Manager(debug=True)
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=1).run(suite)
    pl.show()
