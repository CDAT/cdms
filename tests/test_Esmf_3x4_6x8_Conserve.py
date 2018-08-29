"""
$Id: testEsmf_3x4_6x8_Conserve.py 2354 2012-07-11 15:28:14Z pletzer $


Plotting routine for tests in regrid2.ESMF using ginned up data
"""

import cdms2
from cdms2.mvCdmsRegrid import CdmsRegrid
from openCreateData import dataNoPeri
import unittest
import ESMF

import re


class TestESMFRegridderConserve(unittest.TestCase):

    def setUp(self):

        # This is to show how to use dataNoPeri
        # class dataNoPeri:
        #   def __init__(self, nx, ny, xBnds, yBnds):
        fd3x4 = dataNoPeri(4, 3, (45, 315), (-60, 60))
        fd5x7 = dataNoPeri(7, 5, (45, 315), (-60, 60))

        # Each Grid below is the same. This is just to make it clear which
        # grid is being used
        self.fromGrid3x4 = fd3x4.cdmsFromCell
        self.toGrid3x4 = fd3x4.cdmsFromCell

        self.fromGrid5x7 = fd5x7.cdmsFromCell
        self.toGrid5x7 = fd5x7.cdmsFromCell

        # Get the data for each grid
        self.data3x4 = fd3x4.cdmsFromData
        self.data5x7 = fd5x7.cdmsFromData

        self.eps = 1.e-8

    def test1_3x4_to_3x4(self):
        for d in dir(unittest):
            if re.search('assert', d):
                print(d)
        # Test NonPeriodic grid Returning same grid
        roESMF = CdmsRegrid(self.fromGrid3x4, self.toGrid3x4,
                            dtype='float64',
                            regridTool='ESMF',
                            regridMethod='Conserve',
                            coordSys='degr')
        diag = {
            'srcAreas': 0,
            'dstAreas': 0,
            'srcAreaFractions': 0,
            'dstAreaFractions': 0}
        ESMF3x4 = roESMF(self.data3x4, diag=diag)
        dstResult = (ESMF3x4 * diag['dstAreas']).sum()
        srcResult = (self.data3x4 * diag['srcAreas'] *
                     diag['srcAreaFractions']).sum()
        self.assertLess(abs(srcResult - dstResult), self.eps)
        self.assertEqual(self.data3x4[0, 0], ESMF3x4.data[0, 0])
        self.assertEqual(1.0, ESMF3x4.data[0, 0])

    def test2_3x4_to_5x7_cart(self):
        # Test NonPeriodic grid Returning double grid resolution
        roESMF = CdmsRegrid(self.fromGrid3x4, self.toGrid5x7,
                            dtype='float64',
                            regridTool='ESMF',
                            regridMethod='Conserve',
                            periodicity=0,
                            coordSys='cart')
        diag = {'srcAreas': 0, 'dstAreas': 0, 'srcAreaFractions': 0,
                'dstAreaFractions': 0}
        ESMF5x7 = roESMF(self.data3x4, diag=diag)
        dstResult = (ESMF5x7 * diag['dstAreas']).sum()
        srcResult = (self.data3x4 * diag['srcAreas'] *
                     diag['srcAreaFractions']).sum()
        self.assertLess(abs(srcResult - dstResult), self.eps)
        self.assertEqual(self.data3x4[0, 0], ESMF5x7.data[0, 0])
        self.assertEqual(1.0, ESMF5x7.data[0, 0])
#        self.assertLess(0.249, ESMF5x7[1,1])
#        self.assertGreater(0.251, ESMF5x7[1,1])

    def test2_3x4_to_5x7_degr(self):
        # Test NonPeriodic grid Returning double grid resolution
        roESMF = CdmsRegrid(self.fromGrid3x4, self.toGrid5x7,
                            dtype='float64',
                            regridTool='ESMF',
                            regridMethod='cOnserve',
                            periodicity=0,
                            coordSys='cart')
        diag = {'srcAreas': 0, 'dstAreas': 0, 'srcAreaFractions': 0,
                'dstAreaFractions': 0}
        ESMF5x7 = roESMF(self.data3x4, diag=diag)
        dstResult = (ESMF5x7 * diag['dstAreas']).sum()
        srcResult = (self.data3x4 * diag['srcAreas'] *
                     diag['srcAreaFractions']).sum()
        self.assertLess(abs(srcResult - dstResult), self.eps)

    def test3_5x7_to_3x4(self):
        # Test double grid resolution original grid resolution
        # Just the corner is one valued
        roESMF = CdmsRegrid(self.fromGrid5x7, self.toGrid3x4,
                            dtype='float64',
                            regridTool='esmf',
                            regridMethod='Conserve',
                            periodicity=0,
                            coordSys='degr')
        diag = {
            'srcAreas': 0,
            'dstAreas': 0,
            'srcAreaFractions': 0,
            'dstAreaFractions': 0}
        ESMF3x4 = roESMF(self.data5x7, diag=diag)
        dstResult = (ESMF3x4 * diag['dstAreas']).sum()
        srcResult = (self.data5x7 * diag['srcAreas'] *
                     diag['srcAreaFractions']).sum()
        self.assertLess(abs(srcResult - dstResult), self.eps)

    def test4_5x7_to_3x4_4Corner_Cells_equal_1(self):
        # Test double grid resolution original grid resolution.
        # Reset the data in 0:2, 0:2 to 1
        self.data5x7[:2, :2] = 1

        roESMF = CdmsRegrid(self.fromGrid5x7, self.toGrid3x4,
                            dtype='float64',
                            regridTool='esmp',
                            regridMethod='Conserve',
                            periodicity=0,
                            coordSys='cart')
        diag = {
            'srcAreas': 0,
            'dstAreas': 0,
            'srcAreaFractions': 0,
            'dstAreaFractions': 0}
        ESMF3x4 = roESMF(self.data5x7, diag=diag)
        dstResult = (ESMF3x4 * diag['dstAreas']).sum()
        srcResult = (self.data5x7 * diag['srcAreas'] *
                     diag['srcAreaFractions']).sum()
        self.assertLess(abs(srcResult - dstResult), self.eps)


if __name__ == '__main__':
    print("")  # Spacer
    ESMF.Manager()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestESMFRegridderConserve)
    unittest.TextTestRunner(verbosity=1).run(suite)
