"""
$Id: testEsmf3DSmallesmf.py 2403 2012-07-31 23:07:16Z dkindig $
3D Bilinear test of ESMF through esmf, regrid, and standalone
With and without masking
"""

import pdb
import cdms2  # ESMP_Initialize()
import unittest
import ESMF
from regrid2 import esmf
from regrid2 import ESMFRegrid
import numpy
from ESMF.test.test_api.grid_utilities import *


HAS_MPI = False
try:
        from mpi4py import MPI
        HAS_MPI = True
except:
        pass

import re

ESMF.Manager(debug=True)


class TestESMPRegridderConserve(unittest.TestCase):
    def setUp(self):
        """
        Unit test set up
        """
        self.rootPe = 0
        self.pe = 0
        self.np = 1
        if HAS_MPI:
                self.pe = MPI.COMM_WORLD.Get_rank()
                self.np = MPI.COMM_WORLD.Get_size()

    def test_field_regrid_periodic(self):
        parallel = False
        # create a grid
        srcgrid = grid_create_periodic(60, 30, corners=True, domask=True)
        dstgrid = grid_create_periodic(55, 28, corners=True)

        srcGrid2D = esmf.EsmfStructGrid(srcgrid.coords[0][0].shape, periodicity = 1,
                                        coordSys = None,hasBounds=True)

        mycoords = [srcgrid.coords[0][1],srcgrid.coords[0][0]]
        srcGrid2D.setCoords(mycoords,
                            staggerloc = ESMF.StaggerLoc.CENTER,
                            globalIndexing = True)

        mycoords = [srcgrid.coords[3][1],srcgrid.coords[3][0]]
        srcGrid2D.setCoords(mycoords,
                            staggerloc = ESMF.StaggerLoc.CORNER,
                            globalIndexing = True)

        dstGrid2D = esmf.EsmfStructGrid(dstgrid.coords[0][0].shape, periodicity=1,
                                        coordSys = None, hasBounds=True)

        mycoords = [dstgrid.coords[0][1],dstgrid.coords[0][0]]
        dstGrid2D.setCoords(mycoords,
                            staggerloc = ESMF.StaggerLoc.CENTER,
                            globalIndexing = True)

        mycoords = [dstgrid.coords[3][1],dstgrid.coords[3][0]]
        dstGrid2D.setCoords(mycoords,
                            staggerloc = ESMF.StaggerLoc.CORNER,
                            globalIndexing = True)


        # create the Fields
        srcfield = esmf.EsmfStructField(srcGrid2D,
                                        'srcDataCtr', 
                                        srcgrid.coords[0][0].dtype,
                                        ESMF.StaggerLoc.CENTER)

        dstfield = esmf.EsmfStructField(dstGrid2D, 
                                        'dstDataCtr', 
                                        dstgrid.coords[0][0].dtype,
                                        ESMF.StaggerLoc.CENTER)

        exactfield = esmf.EsmfStructField(dstGrid2D, 
                                        'exactDataCtr', 
                                        dstgrid.coords[0][0].dtype,
                                        ESMF.StaggerLoc.CENTER)

#        srcfield = ESMF.Field(srcgrid, name='srcfield')
#        dstfield = ESMF.Field(dstgrid, name='dstfield')
#        exactfield = ESMF.Field(dstgrid, name='exactfield')

        # create the fraction fields
        srcfracfield = esmf.EsmfStructField(srcGrid2D,
                                        'srcfracfield', 
                                        srcgrid.coords[0][0].dtype,
                                        ESMF.StaggerLoc.CENTER)

        dstfracfield = esmf.EsmfStructField(dstGrid2D,
                                        'dstfracfield', 
                                        srcgrid.coords[0][0].dtype,
                                        ESMF.StaggerLoc.CENTER)

#        srcfracfield = ESMF.Field(srcgrid, name='srcfracfield')
#        dstfracfield = ESMF.Field(dstgrid, name='dstfracfield')

        # initialize the Fields to an analytic function
        pdb.set_trace()
        srcfield.field = initialize_field_grid_periodic(srcfield.field)
        exactfield.field = initialize_field_grid_periodic(exactfield.field)

        # run the ESMF regridding
        regridOut = esmf.EsmfRegrid(srcfield, dstfield,
                               srcMaskValues = np.array([0]),
                               regridMethod = ESMF.RegridMethod.CONSERVE,
                               unMappedAction = ESMF.UnmappedAction.ERROR,
                               srcFrac=srcfracfield,
                               dstFrac=dstfracfield)
        regridOut()

#        regridSrc2Dst = ESMF.Regrid(srcfield, dstfield,
#                                    src_mask_values=np.array([0]),
#                                    regrid_method=ESMF.RegridMethod.CONSERVE,
#                                    unmapped_action=ESMF.UnmappedAction.ERROR,
#                                    src_frac_field=srcfracfield,
#                                    dst_frac_field=dstfracfield)
#        dstfield = regridSrc2Dst(srcfield, dstfield)

        # compute the mass
        srcmass = compute_mass_grid(srcfield.field,
                                    dofrac=True, fracfield=srcfracfield.field)
        dstmass = compute_mass_grid(dstfield.field)

        # compare results and output PASS or FAIL
        meanrel, csrvrel = compare_fields_grid(dstfield.field, exactfield.field, 10E-2, 10e-15, parallel=parallel,
                            dstfracfield=dstfracfield.field, mass1=srcmass, mass2=dstmass)

        self.assertAlmostEqual(meanrel, 0.0016447124122954575)
        self.assertAlmostEqual(csrvrel, 0.0)

if __name__ == '__main__':
    print "" # Spacer
    ESMF.Manager(debug=True)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestESMPRegridderConserve)
    unittest.TextTestRunner(verbosity = 1).run(suite)
