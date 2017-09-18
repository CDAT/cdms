"""
$Id: testEsmf_3x4_6x8_Bilinear_Masked.py 2354 2012-07-11 15:28:14Z pletzer $


Plotting routine for tests in regrid2.ESMF using ginned up data
"""

import cdms2
import regrid2
from openCreateData import dataMaskedNoPeri
import unittest
import ESMF

import re


class TestESMFRegridderMasked(unittest.TestCase):
    def setUp(self):

        # This is to show how to use dataNoPeri
        # class dataNoPeri:
        #   def __init__(self, nx, ny, xBnds, yBnds):
        fd3x4 = dataMaskedNoPeri(4, 3, (45, 315), (-60, 60))
        fd5x7 = dataMaskedNoPeri(7, 5, (45, 315), (-60, 60))

        # Each Grid below is the same. This is just to make it clear which
        # grid is being used
        self.fromGrid3x4 = fd3x4.cdmsFromGrid
        self.toGrid3x4 = fd3x4.cdmsFromGrid

        self.fromGrid5x7 = fd5x7.cdmsFromGrid
        self.toGrid5x7 = fd5x7.cdmsFromGrid

        # Get the data for each grid
        self.data3x4 = fd3x4.cdmsFromData
        self.data5x7 = fd5x7.cdmsFromData

        self.data3x4.mask[:] = False
        self.data3x4.mask[2, 2] = True
        self.data3x4[1, 1] = 0
        self.data3x4[2, 2] = 0
        self.data5x7.mask[:] = False
        self.data5x7.mask[2, 2] = True
        self.data5x7[1, 1] = 0
        self.data5x7[2, 2] = 0

        self.eps = 1e-7

    def test1_3x4_to_3x4(self):
        # Test non-periodic grid returning same grid
        roESMF = cdms2.CdmsRegrid(self.fromGrid3x4, self.toGrid3x4,
                                  dtype=self.data3x4.dtype,
                                  srcGridMask=self.data3x4.mask,
                                  regridTool='ESMF',
                                  coordSys='CART')
        ESMF3x4 = roESMF(self.data3x4)
        self.assertEqual(self.data3x4[0, 0], ESMF3x4[0, 0])
        self.assertEqual(1.0, ESMF3x4[0, 0])
        self.assertEqual(0.0, self.data3x4[1, 1])

    def test2_3x4_to_5x7(self):
        # Test NonPeriodic grid Returning double grid resolution
        roESMF = cdms2.CdmsRegrid(self.fromGrid3x4, self.toGrid5x7,
                                  dtype=self.data3x4.dtype,
                                  srcMask=self.data3x4.mask,
                                  periodicity=0,
                                  regridTool='ESMF', coordSys='cart')
        ESMF5x7 = roESMF(self.data3x4)
        self.assertEqual(self.data3x4[0, 0], ESMF5x7[0, 0])
        self.assertEqual(0.25, ESMF5x7[1, 1])
        self.assertEqual(0.0, ESMF5x7[2, 2])

    def test3_5x7_to_3x4(self):
        # Test double grid resolution original grid resolution
        # Just the corner is one valued
        roESMF = cdms2.CdmsRegrid(self.fromGrid5x7, self.toGrid3x4,
                                  dtype=self.data5x7.dtype,
                                  srcMask=self.data5x7.mask,
                                  periodicity=0,
                                  regridTool='ESMF', coordSys='carT')
        ESMF3x4 = roESMF(self.data5x7)
        self.assertEqual(self.data5x7[0, 0], ESMF3x4[0, 0])
        self.assertEqual(0., ESMF3x4[1, 1])

    def test4_5x7_to_3x4_4Corner_Cells_equal_1(self):
        # Test double grid resolution original grid resolution.
        # Reset the data in 0:2, 0:2 to 1
        self.data5x7[:2, :2] = 1

        roESMF = cdms2.CdmsRegrid(self.fromGrid5x7, self.toGrid3x4,
                                  dtype=self.data5x7.dtype,
                                  srcMask=self.data5x7.mask,
                                  periodicity=0,
                                  regridTool='ESMF')
        ESMF3x4 = roESMF(self.data5x7)
        self.assertEqual(self.data5x7[0, 0], ESMF3x4[0, 0])
        self.assertEqual(self.data5x7[0, 0], 1.0)
        self.assertEqual(ESMF3x4[0, 0], 1.0)


if __name__ == '__main__':
<<<<<<< HEAD
    print("")  # Spacer
=======
    print ""  # Spacer
>>>>>>> master
    ESMF.Manager()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestESMFRegridderMasked)
    unittest.TextTestRunner(verbosity=1).run(suite)
