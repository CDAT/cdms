import cdms2
import ESMF
import numpy
import unittest

HAS_MPI = False
try:
    from mpi4py import MPI
    HAS_MPI = True
except:
    pass

class TestEsmpSmall(unittest.TestCase):

    """
    Test pure ESMF regridding
    """

    def xFunct(self, j, i):
        dx = 1.0/float(self.dims[0])
        return 0.0 + i*dx
    
    def yFunct(self, j, i):
        dy = 1.0/float(self.dims[1])
        return 0.0 + j*dy

    def func(self, x, y):
        if x == 0 and y == 0:
            return 1
        elif x == 0 and y == 1:
            return 1
        elif x == 1 and y == 0:
            return 1
        elif x == 1 and y == 1:
            return 1
        else:
            return 0
        #return x * y

    def setUp(self):
        pass

    def test1_ESMF(self):

        rk = 0
        if HAS_MPI:
            rk = MPI.COMM_WORLD.Get_rank()
        
        coordSys = ESMF.CoordSys.CART
        
        nres = 4
        self.srcDims = (4*nres, 3*nres)
        self.dstDims = (4*nres, 3*nres)

        srcMaxIndex = numpy.array(self.srcDims, numpy.int32) # number of cells
        dstMaxIndex = numpy.array(self.dstDims, numpy.int32) # number of cells

        # grids
        srcGrid = ESMF.Grid(srcMaxIndex, num_peri_dims = 0,
                                        coord_sys = coordSys, staggerloc=[ESMF.StaggerLoc.CENTER])
        dstGrid = ESMF.Grid(dstMaxIndex, num_peri_dims = 0,
                                        coord_sys = coordSys, staggerloc=[ESMF.StaggerLoc.CENTER])

        srcGrid.add_coords(staggerloc=ESMF.StaggerLoc.CORNER)
        dstGrid.add_coords(staggerloc=ESMF.StaggerLoc.CORNER)

        # masks
        srcGrid.add_item(item=ESMF.GridItem.MASK)
        srcGridMaskPtr = srcGrid.get_item(ESMF.GridItem.MASK)

        dstGrid.add_item(item=ESMF.GridItem.MASK)
        dstGridMaskPtr = dstGrid.get_item(ESMF.GridItem.MASK)


        # coordinates
        srcXCorner = srcGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CORNER)
        srcYCorner = srcGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CORNER)
        srcXCenter = srcGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CENTER)
        srcYCenter = srcGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CENTER)

        srcLoCorner = srcGrid.lower_bounds[ESMF.StaggerLoc.CORNER]
        srcHiCorner = srcGrid.upper_bounds[ESMF.StaggerLoc.CORNER]
        srcLoCenter = srcGrid.lower_bounds[ESMF.StaggerLoc.CENTER]
        srcHiCenter = srcGrid.upper_bounds[ESMF.StaggerLoc.CENTER]

        dstXCorner = dstGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CORNER)
        dstYCorner = dstGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CORNER)
        dstXCenter = dstGrid.get_coords(0, staggerloc=ESMF.StaggerLoc.CENTER)
        dstYCenter = dstGrid.get_coords(1, staggerloc=ESMF.StaggerLoc.CENTER)

        dstLoCorner = dstGrid.lower_bounds[ESMF.StaggerLoc.CORNER]
        dstHiCorner = dstGrid.upper_bounds[ESMF.StaggerLoc.CORNER]
        dstLoCenter = dstGrid.lower_bounds[ESMF.StaggerLoc.CENTER]
        dstHiCenter = dstGrid.upper_bounds[ESMF.StaggerLoc.CENTER]

        # fields
        srcFld = ESMF.Field(srcGrid, name='srcFld', 
                            typekind = ESMF.TypeKind.R8,
                            staggerloc = ESMF.StaggerLoc.CENTER)
        dstFld = ESMF.Field(dstGrid, name='dstFld', 
                            typekind = ESMF.TypeKind.R8,
                            staggerloc = ESMF.StaggerLoc.CENTER)

        srcFieldPtr = srcFld.data
        dstFieldPtr = dstFld.data

        # set the coordinates and field values

        # src-corners
        srcNx1 = srcHiCorner[0] - srcLoCorner[0]
        srcNy1 = self.srcDims[1]+1
        self.dims = self.srcDims
        for iy in range(srcNy1):
            iyp = iy + srcLoCorner[0]
            for ix in range(srcNx1):
                ixp = ix + srcLoCorner[1]
                srcXCorner[ix, iy] = self.xFunct(iyp, ixp)
                srcYCorner[ix, iy] = self.yFunct(iyp, ixp)

        # src-centers and mask 
        srcNx = srcHiCenter[0] - srcLoCenter[0]
        srcNy = srcHiCenter[1] - srcLoCenter[1]
        self.dims = self.srcDims
        for iy in range(srcNy):
            iyp = iy + srcLoCenter[0]
            for ix in range(srcNx):
                ixp = ix + srcLoCenter[1]
                x = self.xFunct(iyp + 0.5, ixp + 0.5)
                y = self.yFunct(iyp + 0.5, ixp + 0.5)
                srcXCenter[ix, iy] = x
                srcYCenter[ix, iy] = y
                mask = 0
                if ((iyp*ixp) % 3) == 1: 
                    mask = 1
                srcGridMaskPtr[ix, iy] = mask # valid
                srcFieldPtr[ix, iy] = self.func(ixp, iyp)
        
        # dst-corners
        dstNx1 = dstHiCorner[0] - dstLoCorner[0]
        dstNy1 = dstHiCorner[1] - dstLoCorner[1]
        self.dims = self.dstDims
        for iy in range(dstNy1):
            iyp = iy + dstLoCorner[0]
            for ix in range(dstNx1):
                ixp = ix + dstLoCorner[1]
                dstXCorner[ix, iy] = self.xFunct(iyp, ixp)
                dstYCorner[ix, iy] = self.yFunct(iyp, ixp)

        # dst-centers and mask 
        dstNx = dstHiCenter[0] - dstLoCenter[0]
        dstNy = dstHiCenter[1] - dstLoCenter[1]
        self.dims = self.dstDims
        for iy in range(dstNy):
            iyp = iy + dstLoCenter[0]
            for ix in range(dstNx):
                ixp = ix + dstLoCenter[1]
                x = self.xFunct(iyp + 0.5, ixp + 0.5)
                y = self.yFunct(iyp + 0.5, ixp + 0.5)
                dstXCenter[ix, iy] = x
                dstYCenter[ix, iy] = y
                dstGridMaskPtr[ix, iy] = 0 # valid
                dstFieldPtr[ix, iy] = -20 # fill value

        srcAreaField = ESMF.Field(srcGrid, name='srcAreas',
                                                typekind = ESMF.TypeKind.R8,
                                                staggerloc = ESMF.StaggerLoc.CENTER)
        dstAreaField = ESMF.Field(dstGrid, name='dstAreas',
                                                typekind = ESMF.TypeKind.R8,
                                                staggerloc = ESMF.StaggerLoc.CENTER)
        srcFracField = ESMF.Field(srcGrid, name='srcFracAreas',
                                                typekind = ESMF.TypeKind.R8,
                                                staggerloc = ESMF.StaggerLoc.CENTER)
        dstFracField = ESMF.Field(dstGrid, name='dstFracAreas',
                                                typekind = ESMF.TypeKind.R8,
                                                staggerloc = ESMF.StaggerLoc.CENTER)


        # IF you want to set your own area. These lines are required. 
        # Otherwise, let ESMF do it.
#        ESMF.ESMF_GridAddItem(srcGrid, item = ESMF.ESMP_GRIDITEM_AREA)
#        srcAreas = ESMF.ESMP_GridGetItem(srcGrid, item = ESMP.ESMP_GRIDITEM_AREA)
#        ESMF.ESMF_GridAddItem(dstGrid, item = ESMP.ESMP_GRIDITEM_AREA)
#        dstAreas = ESMF.ESMP_GridGetItem(dstGrid, item = ESMP.ESMP_GRIDITEM_AREA)
#        srcAreas[:] = 0.02080333333
#        dstAreas[:] = 0.08333333333
        
        # interpolation
        maskVals = numpy.array([1], numpy.int32) # values defining mask
        regrid = ESMF.Regrid(srcFld, dstFld, 
                            src_mask_values=maskVals, 
                            dst_mask_values=None, 
                            regrid_method=ESMF.RegridMethod.CONSERVE, 
                            unmapped_action=ESMF.UnmappedAction.IGNORE, 
                            src_frac_field=srcFracField, 
                            dst_frac_field=None)

        regrid(srcFld, dstFld)

        # get the cell areas
        srcAreaField.get_area()
        dstAreaField.get_area()

        srcFieldPtr = srcFld.data
        srcFracPtr  = srcFracField.data

        dstFieldPtr = dstFld.data
        dstFracPtr  = dstFracField.data

        srcarea = srcAreaField.data
        dstarea = dstAreaField.data

        srcFracPtr = srcFracField.data

        # check conservation
        marr = numpy.array(mask == 0, dtype = numpy.int32)
        srcFldSum, dstFldSum = srcFieldPtr.sum(), dstFieldPtr.sum()
        srcFldIntegral = (srcFieldPtr * srcarea * srcFracPtr).sum()
        dstFldIntegral = (dstFieldPtr*dstarea).sum()

        lackConservLocal = srcFldIntegral - dstFldIntegral

        print '[%d] src corner lo = %s hi = %s dst corner lo = %s hi = %s' % (rk, 
                                                                              str(srcLoCorner), 
                                                                              str(srcHiCorner), 
                                                                              str(dstLoCorner), 
                                                                              str(dstHiCorner)) 
        print '[%d] src center lo = %s hi = %s dst center lo = %s hi = %s' % (rk, 
                                                                              str(srcLoCenter), 
                                                                              str(srcHiCenter), 
                                                                              str(dstLoCenter), 
                                                                              str(dstHiCenter)) 
                                                                              
        print '[%d] checksum of src: %f checksum of dst: %f' % (rk, srcFldSum, dstFldSum)
        print '[%d] src total area integral: %g dst total area integral: %g diff: %g\n' % \
            (rk, srcFldIntegral, dstFldIntegral, lackConservLocal)

        if HAS_MPI:
            lackConserv = MPI.COMM_WORLD.reduce(lackConservLocal, op=MPI.SUM, root=0)
        else:
            lackConserv = lackConservLocal
        
        if rk == 0:
            print '[0] total lack of conservation (should be small): %f' % lackConserv
            assert(abs(lackConserv) < 1.e-6)

        # cleanup
        regrid.destroy()
        srcFld.destroy()
        dstFld.destroy()
        srcGrid.destroy()
        dstGrid.destroy()

if __name__ == '__main__':

    print "" # Spacer
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEsmpSmall)
    unittest.TextTestRunner(verbosity = 1).run(suite)

        
