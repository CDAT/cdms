"""
$Id: testEsmfInterface.py 2389 2012-07-26 15:51:43Z dkindig $

Unit tests for esmf interface

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

HAS_MPI = False
try:
    from mpi4py import MPI
    HAS_MPI = True
except BaseException:
    pass

PLOT = False
if PLOT:
    from matplotlib import pylab


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def test_2d(self):

        mype = 0
        if HAS_MPI:
            mype = MPI.COMM_WORLD.Get_rank()

        f = cdms2.open(cdat_info.get_sampledata_path() +
                       '/so_Omon_ACCESS1-0_historical_r1i1p1_185001-185412_2timesteps.nc')
        so = f['so']  # [0, 0, :, :]
        clt = cdms2.open(cdat_info.get_sampledata_path() +
                         '/clt.nc')('clt')[0, :, :]

        # ESMF interface, assume so and clt are cell centered
        srcGrid = regrid2.esmf.EsmfStructGrid(so[0, 0, ...].shape,
                                              coordSys=ESMF.CoordSys.SPH_DEG,
                                              periodicity=0)
        dstGrid = regrid2.esmf.EsmfStructGrid(clt.shape,
                                              coordSys=ESMF.CoordSys.SPH_DEG,
                                              periodicity=0)
        grid = [so.getGrid().getLatitude(), so.getGrid().getLongitude()]
        srcGrid.setCoords(grid,
                          staggerloc=ESMF.StaggerLoc.CENTER,
                          globalIndexing=True)
        # convert to curvilinear
        ny, nx = clt.shape
        y = clt.getGrid().getLatitude()
        x = clt.getGrid().getLongitude()
        yy = numpy.outer(y, numpy.ones((nx,), numpy.float32))
        xx = numpy.outer(numpy.ones((ny,), numpy.float32), x)
        dstGrid.setCoords([yy, xx],
                          staggerloc=ESMF.StaggerLoc.CENTER,
                          globalIndexing=True)
#        mask = numpy.zeros(so[0, 0, ...].shape, numpy.int32)
#        mask[:] = (so[0, 0, ...] == so.missing_value)
        mask = so[0, 0, :].mask
        srcGrid.setMask(mask)
        srcFld = regrid2.esmf.EsmfStructField(srcGrid, 'srcFld', datatype=so[:].dtype,
                                              staggerloc=ESMF.StaggerLoc.CENTER)
        srcSlab = srcGrid.getLocalSlab(ESMF.StaggerLoc.CENTER)
        dstSlab = dstGrid.getLocalSlab(ESMF.StaggerLoc.CENTER)
        srcFld.setLocalData(numpy.array(so[0, 0, srcSlab[0], srcSlab[1]]),
                            staggerloc=ESMF.StaggerLoc.CENTER)
        dstFld = regrid2.esmf.EsmfStructField(dstGrid, 'dstFld',
                                              datatype=so.dtype,
                                              staggerloc=ESMF.StaggerLoc.CENTER)
        dstData = numpy.ones(clt.shape, numpy.float32)[dstSlab[0], dstSlab[1]]
        dstFld.setLocalData(so.missing_value * dstData,
                            staggerloc=ESMF.StaggerLoc.CENTER)

        rgrd1 = regrid2.esmf.EsmfRegrid(srcFld, dstFld,
                                        srcFrac=None, dstFrac=None,
                                        srcMaskValues=numpy.array(
                                            [1], numpy.int32),
                                        dstMaskValues=numpy.array(
                                            [1], numpy.int32),
                                        regridMethod=ESMF.RegridMethod.BILINEAR,
                                        unMappedAction=ESMF.UnmappedAction.IGNORE)

        # now interpolate
        rgrd1(srcFld, dstFld)

        # get the data on this proc
        soInterpEsmfInterface = dstFld.getData(rootPe=None)

        # gather the data on proc 0
        soInterpEsmfInterfaceRoot = dstFld.getData(rootPe=0)

        print(('[%d] esmfInterface chksum = %f' % (mype, soInterpEsmfInterface.sum())))
        if mype == 0:
            print(('ROOT esmfInterface chksum = %f' % soInterpEsmfInterfaceRoot.sum()))

        # Native ESMP
        srcMaxIndex = numpy.array(so[0, 0, ...].shape[::-1], dtype=numpy.int32)
#        srcMaxIndex = numpy.array(so[0, 0, ...].shape, dtype=numpy.int32)
        srcGrid = ESMF.Grid(
            srcMaxIndex,
            coord_sys=ESMF.CoordSys.SPH_DEG,
            staggerloc=[
                ESMF.StaggerLoc.CENTER])
#        srcGrid = ESMP.ESMP_GridCreateNoPeriDim(srcMaxIndex,
#                                                coordSys = ESMP.ESMP_COORDSYS_SPH_DEG)
#        ESMP.ESMP_GridAddCoord(srcGrid,
#                               staggerloc = ESMF.StaggerLoc.CENTER)
        srcDimsCenter = [srcGrid.lower_bounds[ESMF.StaggerLoc.CENTER],
                         srcGrid.upper_bounds[ESMF.StaggerLoc.CENTER]]
#        srcDimsCenter = ESMP.ESMP_GridGetCoord(srcGrid,
#                                               ESMF.StaggerLoc.CENTER)
        srcXCenter = srcGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CENTER)
        srcYCenter = srcGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CENTER)
#        srcXCenter = ESMP.ESMP_GridGetCoordPtr(srcGrid, 0,
#                                               ESMF.StaggerLoc.CENTER)
#        srcYCenter = ESMP.ESMP_GridGetCoordPtr(srcGrid, 1,
#                                               ESMF.StaggerLoc.CENTER)
        dstMaxIndex = numpy.array(clt.shape[::-1], dtype=numpy.int32)
#        dstMaxIndex = numpy.array(clt.shape, dtype=numpy.int32)
        dstGrid = ESMF.Grid(
            dstMaxIndex,
            coord_sys=ESMF.CoordSys.SPH_DEG,
            staggerloc=[
                ESMF.StaggerLoc.CENTER])
#        dstGrid = ESMP.ESMP_GridCreateNoPeriDim(dstMaxIndex,
#                                                coordSys = ESMP.ESMP_COORDSYS_SPH_DEG)
#        ESMP.ESMP_GridAddCoord(dstGrid,
#                               staggerloc = ESMF.StaggerLoc.CENTER)
        dstDimsCenter = [dstGrid.lower_bounds[ESMF.StaggerLoc.CENTER],
                         dstGrid.upper_bounds[ESMF.StaggerLoc.CENTER]]
#        dstDimsCenter = ESMP.ESMP_GridGetCoord(dstGrid,
#                                               ESMF.StaggerLoc.CENTER)
        dstXCenter = dstGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CENTER)
        dstYCenter = dstGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CENTER)

#        dstXCenter = ESMP.ESMP_GridGetCoordPtr(dstGrid, 0,
#                                               ESMF.StaggerLoc.CENTER)
#        dstYCenter = ESMP.ESMP_GridGetCoordPtr(dstGrid, 1,
#                                               ESMF.StaggerLoc.CENTER)
        # mask
        srcGrid.add_item(item=ESMF.GridItem.MASK)
#        ESMP.ESMP_GridAddItem(srcGrid, item=ESMP.ESMP_GRIDITEM_MASK)
        srcMask = srcGrid.get_item(item=ESMF.GridItem.MASK)
#        srcMask = ESMP.ESMP_GridGetItem(srcGrid, item=ESMP.ESMP_GRIDITEM_MASK)

        # create field
        srcFld = ESMF.Field(
            srcGrid,
            name='srcFld',
            typekind=ESMF.TypeKind.R4,
            staggerloc=ESMF.StaggerLoc.CENTER)
        srcFldPtr = srcFld.data

        dstFld = ESMF.Field(
            dstGrid,
            name='dstFld',
            typekind=ESMF.TypeKind.R4,
            staggerloc=ESMF.StaggerLoc.CENTER)
        dstFldPtr = dstFld.data

        # set coords, mask, and field values for src and dst

        srcNtot = reduce(
            operator.mul, [
                srcDimsCenter[1][i] - srcDimsCenter[0][i] for i in range(2)])

        srcXCenter[:] = so.getGrid().getLongitude()[:].T
        srcYCenter[:] = so.getGrid().getLatitude()[:].T
        srcFldPtr[:] = so[0, 0, :].T
        srcMask[:] = (srcFldPtr == so.missing_value)

        # clt grid is rectilinear, transform to curvilinear
        lons = clt.getGrid().getLongitude()
        lats = clt.getGrid().getLatitude()
        ny, nx = dstDimsCenter[1][1] - \
            dstDimsCenter[0][1], dstDimsCenter[1][0] - dstDimsCenter[0][0]
        localLons = lons[dstDimsCenter[0][0]:dstDimsCenter[1][0]]
        localLats = lats[dstDimsCenter[0][1]:dstDimsCenter[1][1]]
        xx = numpy.outer(localLons, numpy.ones((ny,), dtype=numpy.float32))
        yy = numpy.outer(numpy.ones((nx,), dtype=numpy.float32), localLats)

        dstXCenter[:] = xx
        dstYCenter[:] = yy
        dstFldPtr[:] = so.missing_value

        # regrid forward and backward
        maskVals = numpy.array([1], numpy.int32)  # values defining mask
        regrid1 = ESMF.Regrid(srcFld, dstFld,
                              src_mask_values=maskVals,
                              dst_mask_values=None,
                              regrid_method=ESMF.RegridMethod.BILINEAR,
                              unmapped_action=ESMF.UnmappedAction.IGNORE,
                              src_frac_field=None,
                              dst_frac_field=None)

        regrid1(srcFld, dstFld, zero_region=ESMF.Region.SELECT)

        jbeg, jend = dstDimsCenter[0][0], dstDimsCenter[1][0]
        ibeg, iend = dstDimsCenter[0][1], dstDimsCenter[1][1]
        soInterpESMP = numpy.ma.masked_where((dstFldPtr == so.missing_value), dstFldPtr).T
        soInterpEsmfInterface = numpy.ma.masked_where(soInterpEsmfInterface == so.missing_value,soInterpEsmfInterface)
        soInterpEsmfInterfaceRoot = numpy.ma.masked_where(soInterpEsmfInterfaceRoot == so.missing_value,soInterpEsmfInterfaceRoot)
        # check local diffs
        ntot = reduce(operator.mul, soInterpESMP.shape)
        avgdiff = numpy.sum(soInterpEsmfInterface - soInterpESMP) / float(ntot)
        self.assertLess(abs(avgdiff), 1.e-7)

        # check gather
        chksumESMP = numpy.sum(soInterpESMP)
        chksumEsmfInterface = numpy.sum(soInterpEsmfInterface)
        if HAS_MPI:
            chksumsESMP = MPI.COMM_WORLD.gather(chksumESMP, root=0)
        else:
            chksumsESMP = chksumESMP

        print(('[%d] ESMP chksum = %f' % (mype, chksumESMP)))
        if mype == 0:
            print(('ROOT ESMP chksum = %f' % numpy.sum(chksumsESMP)))

        if mype == 0:
            chksumESMPRoot = numpy.sum(chksumsESMP)
            chksumESMFInterfaceRoot = numpy.sum(soInterpEsmfInterfaceRoot)
            self.assertLess(abs(chksumESMFInterfaceRoot -
                                chksumESMPRoot), 1.e-5 * chksumESMPRoot)

        if PLOT:
            pylab.subplot(2, 2, 1)
            pylab.pcolor(so, vmin=20.0, vmax=40.0)
            pylab.colorbar()
            pylab.title('so')
            pylab.subplot(2, 2, 2)
            pylab.pcolor(
                soInterpEsmfInterface -
                soInterpESMP,
                vmin=-
                0.5,
                vmax=0.5)
            pylab.colorbar()
            pylab.title('[%d] EsmfInterface - ESMP' % mype)
            pylab.subplot(2, 2, 3)
            pylab.pcolor(soInterpEsmfInterface, vmin=20.0, vmax=40.0)
            pylab.colorbar()
            pylab.title('[%d] ESMFInterface' % mype)
            pylab.subplot(2, 2, 4)
            pylab.pcolor(soInterpESMP, vmin=20, vmax=40)
            pylab.colorbar()
            pylab.title('[%d] ESMP' % mype)

        # clean up
#        ESMP.ESMP_FieldRegridRelease(regrid1)
#        ESMP.ESMP_FieldDestroy(dstFld)
#        ESMP.ESMP_GridDestroy(dstGrid)
#        ESMP.ESMP_FieldDestroy(srcFld)
#        ESMP.ESMP_GridDestroy(srcGrid)


if __name__ == '__main__':
    print("")
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=1).run(suite)
    if PLOT:
        pylab.show()
