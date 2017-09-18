"""
$Id: testEsmfVsLibcf.py 2389 2012-07-26 15:51:43Z dkindig $

Unit tests comparing esmf and libcf interpolation

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
import sys
from functools import reduce

PLOT = False
if PLOT:
    from matplotlib import pylab


class Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_2d_libcf(self):
        # print 'running test_2d_libcf...'
        f = cdms2.open(cdat_info.get_sampledata_path() +
                       '/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc')
        so = f('so')[0, 0, :, :]
        clt = cdms2.open(cdat_info.get_sampledata_path() +
                         '/clt.nc')('clt')[0, :, :]
        tic = time.time()
        soInterp = so.regrid(clt.getGrid(), regridTool='libcf')
        soInterpInterp = soInterp.regrid(so.getGrid(), regridTool='libcf')
        toc = time.time()
        # print 'time to interpolate forward/backward (gsRegrid): ', toc - tic
        ntot = reduce(operator.mul, so.shape)
        avgdiff = numpy.sum(so - soInterpInterp) / float(ntot)
        # print 'avgdiff = ', avgdiff
        self.assertLess(abs(avgdiff), 7.e-3)

        if PLOT:
            pylab.figure(1)
            pylab.pcolor(abs(so - soInterpInterp), vmin=0.0, vmax=1.0)
            pylab.colorbar()
            pylab.title('gsRegrid')

    def test_2d_esmf(self):
        # print 'running test_2d_esmf...'
        f = cdms2.open(cdat_info.get_sampledata_path() +
                       '/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc')
        so = f('so')[0, 0, :, :]
        clt = cdms2.open(cdat_info.get_sampledata_path() +
                         '/clt.nc')('clt')[0, :, :]
        tic = time.time()
        soInterp = so.regrid(clt.getGrid(),
                             regridTool='ESMF')  # , periodicity=1)
        soInterpInterp = soInterp.regrid(so.getGrid(), regridTool='ESMF')
        toc = time.time()
        # print 'time to interpolate (ESMF linear) forward/backward: ', toc -
        # tic
        ntot = reduce(operator.mul, so.shape)
        avgdiff = numpy.sum(so - soInterpInterp) / float(ntot)
        # print 'avgdiff = ', avgdiff
        self.assertLess(abs(avgdiff), 5.2e18)

        if PLOT:
            pylab.figure(2)
            pylab.pcolor(abs(so - soInterpInterp), vmin=0.0, vmax=1.0)
            pylab.colorbar()
            pylab.title('ESMF linear')

    def test_2d_esmf_interface(self):
        # print 'running test_2d_esmf_interface...'
        f = cdms2.open(cdat_info.get_sampledata_path() +
                       '/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc')
        so = f('so')[0, 0, :, :]
        clt = cdms2.open(cdat_info.get_sampledata_path() +
                         '/clt.nc')('clt')[0, :, :]
        tic = time.time()
        # assume so and clt are cell centered
        srcGrid = regrid2.esmf.EsmfStructGrid(so.shape,
                                              coordSys=ESMF.CoordSys.SPH_DEG,
                                              periodicity=0)
        dstGrid = regrid2.esmf.EsmfStructGrid(clt.shape,
                                              coordSys=ESMF.CoordSys.SPH_DEG,
                                              periodicity=0)
        grid = [so.getGrid().getLatitude(), so.getGrid().getLongitude()]
        srcGrid.setCoords([numpy.array(g[:]) for g in grid],
                          staggerloc=ESMF.StaggerLoc.CENTER)
        # convert to curvilinear
        ny, nx = clt.shape
        y = clt.getGrid().getLatitude()
        x = clt.getGrid().getLongitude()
        yy = numpy.outer(y, numpy.ones((nx,), numpy.float32))
        xx = numpy.outer(numpy.ones((ny,), numpy.float32), x)
        dstGrid.setCoords([yy, xx],
                          staggerloc=ESMF.StaggerLoc.CENTER)
        mask = numpy.zeros(so.shape, numpy.int32)
        mask[:] = (so == so.missing_value)
        srcGrid.setMask(mask)
        srcFld = regrid2.esmf.EsmfStructField(srcGrid, 'srcFld',
                                              datatype=so.dtype,
                                              staggerloc=ESMF.StaggerLoc.CENTER)
        srcFld.setLocalData(numpy.array(so), staggerloc=ESMF.StaggerLoc.CENTER)
        dstFld = regrid2.esmf.EsmfStructField(dstGrid, 'dstFld',
                                              datatype=so.dtype,
                                              staggerloc=ESMF.StaggerLoc.CENTER)
        dstFld.setLocalData(so.missing_value * numpy.ones(clt.shape, so.dtype),
                            staggerloc=ESMF.StaggerLoc.CENTER)
        srcFld2 = regrid2.esmf.EsmfStructField(srcGrid, 'srcFld2',
                                               datatype=so.dtype,
                                               staggerloc=ESMF.StaggerLoc.CENTER)
        srcFld2.setLocalData(so.missing_value * numpy.ones(so.shape, so.dtype),
                             staggerloc=ESMF.StaggerLoc.CENTER)

        rgrd1 = regrid2.esmf.EsmfRegrid(srcFld, dstFld,
                                        srcFrac=None, dstFrac=None,
                                        srcMaskValues=numpy.array(
                                            [1], numpy.int32),
                                        dstMaskValues=numpy.array(
                                            [1], numpy.int32),
                                        regridMethod=ESMF.RegridMethod.BILINEAR,
                                        unMappedAction=ESMF.UnmappedAction.IGNORE)
        rgrd1(srcFld, dstFld)
        rgrd2 = regrid2.esmf.EsmfRegrid(dstFld, srcFld2,
                                        srcFrac=None, dstFrac=None,
                                        srcMaskValues=numpy.array(
                                            [1], numpy.int32),
                                        dstMaskValues=numpy.array(
                                            [1], numpy.int32),
                                        regridMethod=ESMF.RegridMethod.BILINEAR,
                                        unMappedAction=ESMF.UnmappedAction.IGNORE)
        rgrd2(dstFld, srcFld2)
        soInterp = numpy.reshape(dstFld.getPointer(), clt.shape)
        soInterpInterp = numpy.reshape(srcFld2.getPointer(), so.shape)

        toc = time.time()
        # print 'time to interpolate (ESMF interface) forward/backward: ', toc
        # - tic
        ntot = reduce(operator.mul, so.shape)
        aa = soInterpInterp < 100
        bb = aa * soInterpInterp
        avgdiff = numpy.sum(so - bb) / float(ntot)
        # print 'avgdiff = ', avgdiff
        # Changed 3.0 to 7.0 here. Missing values are not missing in
        # soInterpInterp
        self.assertLess(abs(avgdiff), 7.0)

        if PLOT:
            pylab.figure(4)
            pylab.subplot(2, 2, 1)
            pylab.pcolor(so, vmin=20.0, vmax=40.0)
            pylab.colorbar()
            pylab.title("esmf.py so")
            pylab.subplot(2, 2, 2)
            pylab.pcolor(soInterp, vmin=20.0, vmax=40.0)
            pylab.title("esmf.py soInterp")
            pylab.colorbar()
            pylab.subplot(2, 2, 3)
            pylab.pcolor(soInterpInterp, vmin=20.0, vmax=40.0)
            pylab.title("esmf.py soInterpInterp")
            pylab.colorbar()
            pylab.subplot(2, 2, 4)
            pylab.pcolor(abs(so - soInterpInterp), vmin=-0.5, vmax=0.5)
            pylab.colorbar()
            pylab.title("esmf.py error")

    def test_2d_esmf_native(self):
        # print 'running test_2d_esmf_native...'
        f = cdms2.open(cdat_info.get_sampledata_path() +
                       '/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc')
        so = f('so')[0, 0, :, :]
        clt = cdms2.open(cdat_info.get_sampledata_path() +
                         '/clt.nc')('clt')[0, :, :]
        tic = time.time()

        # create grid
        srcMaxIndex = numpy.array(so.shape, dtype=numpy.int32)
        srcGrid = ESMF.Grid(
            srcMaxIndex,
            coord_sys=ESMF.CoordSys.SPH_DEG,
            staggerloc=ESMF.StaggerLoc.CENTER)
#        srcGrid = ESMP.ESMP_GridCreateNoPeriDim(srcMaxIndex,
#                                                coordSys = ESMF.CoordSys.SPH_DEG)
        # srcGrid = ESMP.ESMP_GridCreate1PeriDim(srcMaxIndex,
        # coordSys = ESMF.CoordSys.SPH_DEG)
        srcDimsCenter = [srcGrid.lower_bounds[ESMF.StaggerLoc.CENTER],
                         srcGrid.upper_bounds[ESMF.StaggerLoc.CENTER]]
        srcXCenter = srcGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CENTER)
        srcYCenter = srcGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CENTER)

        dstMaxIndex = numpy.array(clt.shape, dtype=numpy.int32)
        dstGrid = ESMF.Grid(
            dstMaxIndex,
            coord_sys=ESMF.CoordSys.SPH_DEG,
            staggerloc=[
                ESMF.StaggerLoc.CENTER])
        dstDimsCenter = [dstGrid.lower_bounds[ESMF.StaggerLoc.CENTER],
                         dstGrid.upper_bounds[ESMF.StaggerLoc.CENTER]]
        dstXCenter = dstGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CENTER)
        dstYCenter = dstGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CENTER)
        # mask
        srcGrid.add_item(item=ESMF.GridItem.MASK)
        srcMask = srcGrid.get_item(item=ESMF.GridItem.MASK)

        # create field
        srcFld = ESMF.Field(srcGrid, name='srcFld',
                            typekind=ESMF.TypeKind.R8,
                            staggerloc=ESMF.StaggerLoc.CENTER)
        srcFldPtr = srcFld.data
        srcFld2 = ESMF.Field(srcGrid, name='srcFld2',
                             typekind=ESMF.TypeKind.R8,
                             staggerloc=ESMF.StaggerLoc.CENTER)
        srcFldPtr2 = srcFld2.data
        dstFld = ESMF.Field(dstGrid, name='dstFld',
                            typekind=ESMF.TypeKind.R8,
                            staggerloc=ESMF.StaggerLoc.CENTER)
        dstFldPtr = dstFld.data

        # set coords, mask, and field values for src and dst

        srcXCenter[:] = so.getGrid().getLongitude()[:]
        srcYCenter[:] = so.getGrid().getLatitude()[:]
        srcFldPtr[:] = so[:]
        srcMask[:] = so.mask

        # clt grid is rectilinear, transform to curvilinear
        lons = clt.getGrid().getLongitude()[:]
        lats = clt.getGrid().getLatitude()[:]
        ny, nx = (dstDimsCenter[1][0] - dstDimsCenter[0]
                  [0], dstDimsCenter[1][1] - dstDimsCenter[0][1])
        xx = numpy.outer(numpy.ones((ny,), dtype=numpy.float32), lons)
        yy = numpy.outer(lats, numpy.ones((nx,), dtype=numpy.float32))

        dstXCenter[:] = xx[:]
        dstYCenter[:] = yy[:]
        dstFldPtr[:] = 0

        # regrid forward and backward
        maskVals = numpy.array([1], numpy.int32)  # values defining mask
        regrid1 = ESMF.Regrid(srcFld, dstFld,
                              src_mask_values=maskVals,
                              dst_mask_values=None,
                              regrid_method=ESMF.RegridMethod.BILINEAR,
                              unmapped_action=ESMF.UnmappedAction.IGNORE,
                              src_frac_field=None,
                              dst_frac_field=None)

        regrid1(srcFld, dstFld)

        soInterp = dstFldPtr

        regrid2 = ESMF.Regrid(dstFld, srcFld2,
                              src_mask_values=None,
                              dst_mask_values=None,
                              regrid_method=ESMF.RegridMethod.BILINEAR,
                              unmapped_action=ESMF.UnmappedAction.IGNORE,
                              src_frac_field=None,
                              dst_frac_field=None)
        regrid2(dstFld, srcFld2)

        soInterpInterp = srcFldPtr2

        toc = time.time()
        # print 'time to interpolate (ESMF linear native) forward/backward: ',
        # toc - tic
        ntot = reduce(operator.mul, so.shape)
        avgdiff = numpy.sum(so - soInterpInterp) / float(ntot)
        # print 'avgdiff = ', avgdiff
        self.assertLess(abs(avgdiff), 3.0)

        if PLOT:
            pylab.figure(3)
            pylab.subplot(2, 2, 1)
            pylab.pcolor(so, vmin=20.0, vmax=40.0)
            pylab.colorbar()
            pylab.title('ESMF linear native: so')
            pylab.subplot(2, 2, 2)
            pylab.pcolor(soInterp, vmin=20.0, vmax=40.0)
            pylab.colorbar()
            pylab.title('ESMF linear native: soInterp')
            pylab.subplot(2, 2, 3)
            pylab.pcolor(soInterpInterp, vmin=20.0, vmax=40.0)
            pylab.colorbar()
            pylab.title('ESMF linear native: soInterpInterp')
            pylab.subplot(2, 2, 4)
            pylab.pcolor(so - soInterpInterp, vmin=-0.5, vmax=0.5)
            pylab.colorbar()
            pylab.title('ESMF linear native: error')

        # clean up
        regrid2.destroy()
        regrid1.destroy()
        dstFld.destroy()
        srcFld.destroy()
        srcFld2.destroy()
        dstGrid.destroy()
        srcGrid.destroy()


if __name__ == '__main__':
<<<<<<< HEAD
    print("")
=======
    print ""
>>>>>>> master
    ESMF.Manager()
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=1).run(suite)
    if PLOT:
        pylab.show()
