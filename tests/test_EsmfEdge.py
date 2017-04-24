"""

Test the new EDGE stagger locations

$Id: $
"""

import unittest
import ESMF
import cdms2
import numpy
try:
    from mpi4py import MPI
    has_mpi = True
except:
    has_mpi = False

class TestESMFEDGE(unittest.TestCase):
    def setUp(self):

        if has_mpi:
            self.pe = MPI.COMM_WORLD.Get_rank()
            self.nprocs = MPI.COMM_WORLD.Get_size()
        else:
            self.pe = 0
            self.nprocs = 1

        nxe, nye = 4, 3
        nxs, nys = 1, 1
        nx,  ny  = 8, 6
        y = numpy.linspace(nys, nye, ny)
        x = numpy.linspace(nxs, nxe, nx)
        y1 = numpy.linspace(nys-.5, nye+.5, ny+1)
        x1 = numpy.linspace(nxs-.5, nxe+.5, nx+1)

        # v
        dEdge1 = []
        dEdge1.append(numpy.outer(y1, numpy.ones(nx)))
        dEdge1.append(numpy.outer(numpy.ones(ny+1), x))
        self.dEdge1 = dEdge1

        # u
        dEdge2 = []
        dEdge2.append(numpy.outer(y, numpy.ones(nx+1)))
        dEdge2.append(numpy.outer(numpy.ones(ny), x1))
        self.dEdge2 = dEdge2

        # Cells
        dstGrid = []
        dstGrid.append(numpy.outer(y, numpy.ones(nx)))
        dstGrid.append(numpy.outer(numpy.ones(ny), x))
        self.dstGrid = dstGrid

        #  Corners
        dstCr = []
        dstCr.append(numpy.outer(y1, numpy.ones(nx+1)))
        dstCr.append(numpy.outer(numpy.ones(ny+1), x1))
        self.dstCr = dstCr

        self.dataEdge2 = numpy.array(dEdge2[0] + 2, numpy.float32)
        self.dataEdge1 = numpy.array(dEdge1[0] + 5, numpy.float32)
        self.datadstGrid = numpy.array(dstGrid[0] + 2, numpy.float32)
        self.datadstCr = numpy.array(dstCr[0] + 2, numpy.float32)

    def test1_EDGE1_linear_cart_nopd_native(self):
        # Cells
        maxIndexdstGrid = numpy.array(self.datadstGrid.shape[::-1], numpy.int32)
        grid = ESMF.Grid(maxIndexdstGrid, num_peri_dims=0, coord_sys = ESMF.CoordSys.CART, staggerloc=[ESMF.StaggerLoc.CENTER])

        cGrdXPtr = grid.get_coords(0, staggerloc=ESMF.StaggerLoc.CENTER)
        cGrdYPtr = grid.get_coords(1, staggerloc=ESMF.StaggerLoc.CENTER)

        # Destination u and v fields in the cell centers
        cuFld = ESMF.Field(grid, name='cell_U_Fld',
                           typekind = ESMF.TypeKind.R8,
                           staggerloc = ESMF.StaggerLoc.CENTER)

        cvFld = ESMF.Field(grid, name='cell_V_Fld',
                            typekind = ESMF.TypeKind.R8,
                            staggerloc = ESMF.StaggerLoc.CENTER)
        cuFldPtr = cuFld.data
        cvFldPtr = cvFld.data

        # u Grid
        grid.add_coords(staggerloc = ESMF.StaggerLoc.EDGE1)
        uGrdXPtr = grid.get_coords(0, staggerloc=ESMF.StaggerLoc.EDGE1)
        uGrdYPtr = grid.get_coords(1, staggerloc=ESMF.StaggerLoc.EDGE1)
        uFld = ESMF.Field(grid, name='srcEdge1', 
                          typekind = ESMF.TypeKind.R8,
                          staggerloc = ESMF.StaggerLoc.EDGE1)
        uFldPtr = uFld.data

        # v Grid
        grid.add_coords(staggerloc = ESMF.StaggerLoc.EDGE2)
        vGrdXPtr = grid.get_coords(0, staggerloc=ESMF.StaggerLoc.EDGE2)
        vGrdYPtr = grid.get_coords(1, staggerloc=ESMF.StaggerLoc.EDGE2)
        vFld = ESMF.Field(grid, name='srcEdge2', 
                            typekind = ESMF.TypeKind.R8,
                            staggerloc = ESMF.StaggerLoc.EDGE2)
        vFldPtr = vFld.data

        # Set the data
        cGrdXPtr[:] = self.dstGrid[1][:].T
        cGrdYPtr[:] = self.dstGrid[0][:].T

        uGrdXPtr[:] = self.dEdge2[1][:].T
        uGrdYPtr[:] = self.dEdge2[0][:].T

        vGrdXPtr[:] = self.dEdge1[1][:].T
        vGrdYPtr[:] = self.dEdge1[0][:].T

        cuFldPtr[:] = self.datadstGrid[:].T
        cvFldPtr[:] = self.datadstGrid[:].T

        uFldPtr[:] = self.dataEdge2[:].T
        vFldPtr[:] = self.dataEdge1[:].T

        # Regrid
        regridObj1 = ESMF.Regrid(uFld, cuFld,
                              src_mask_values = None, 
                              dst_mask_values = None,
                              regrid_method = ESMF.RegridMethod.BILINEAR,
                              unmapped_action = ESMF.UnmappedAction.IGNORE,
                              src_frac_field = None, 
                              dst_frac_field = None)
        regridObj1(uFld, cuFld)

        regridObj2 = ESMF.Regrid(vFld, cvFld,
                              src_mask_values = None, 
                              dst_mask_values = None,
                              regrid_method = ESMF.RegridMethod.BILINEAR,
                              unmapped_action = ESMF.UnmappedAction.IGNORE,
                              src_frac_field = None, 
                              dst_frac_field = None)
        regridObj1(vFld, cvFld)
        
        if self.pe == 0:
            print cuFldPtr.shape, self.datadstGrid.shape
            cuFldArr = numpy.reshape(cuFldPtr, self.datadstGrid.shape)
            cvFldArr = numpy.reshape(cvFldPtr, self.datadstGrid.shape)
    
            print
            print "U's"
            print self.dataEdge2
            print cuFldArr
            print
            print self.dataEdge1
            print cvFldArr

if __name__ == "__main__":
    ESMF.Manager()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestESMFEDGE)
    unittest.TextTestRunner(verbosity = 2).run(suite)

