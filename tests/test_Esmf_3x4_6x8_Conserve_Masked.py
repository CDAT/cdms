"""
$Id: testEsmf_3x4_6x8_Conserve_Masked.py 2354 2012-07-11 15:28:14Z pletzer $


Plotting routine for tests in regrid2.ESMF using ginned up data
"""

import cdms2
from cdms2.mvCdmsRegrid import CdmsRegrid
from openCreateData import dataMaskedNoPeri
import unittest
import ESMF
PLOT = False
if PLOT:
    import matplotlib.pylab as pylab


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

        self.eps = 1e-4

    def test1_3x4_to_3x4(self):
        # Test non-periodic grid returning same grid
        roESMF = CdmsRegrid(self.fromGrid3x4, self.toGrid3x4,
                            dtype='float64',
                            srcGridMask=self.data3x4.mask,
                            periodicity=0,
                            regridTool='ESMF',
                            regridMethod='Conserve', coordSys='cart')
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
        self.assertEqual(self.data3x4[0, 0], ESMF3x4[0, 0])
        self.assertEqual(1.0, ESMF3x4[0, 0])

    def test2_3x4_to_5x7_cart(self):
        # Test non-periodic grid returning double grid resolution
        roESMF = CdmsRegrid(self.fromGrid3x4, self.toGrid5x7,
                            dtype='float64',
                            srcGridMask=self.data3x4.mask,
                            regridTool='ESMF',
                            periodicity=0,
                            regridMethod='Conserve',
                            coordSys='cart')
        diag = {'srcAreas': 0, 'dstAreas': 0,
                'srcAreaFractions': 0, 'dstAreaFractions': 0}
        ESMF5x7 = roESMF(self.data3x4, diag=diag)
        dstMass = (ESMF5x7 * diag['dstAreas']).sum()
        srcMass = (self.data3x4 * diag['srcAreas']
                                * diag['srcAreaFractions']).sum()

        if PLOT:
            pylab.figure(1)
            pylab.pcolor(self.data3x4)
            pylab.colorbar()
            pylab.title('original self.data3x4')
            pylab.figure(2)
            pylab.pcolor(ESMF5x7)
            pylab.colorbar()
            pylab.title('interpolated ESMF5x7')
#        self.assertLess(abs(srcMass - dstMass), self.eps)
        self.assertEqual(self.data3x4[0, 0], ESMF5x7[0, 0])
        self.assertEqual(1.0, ESMF5x7[0, 0])
        self.assertEqual(0.25, ESMF5x7[1, 1])
        self.assertEqual(0.0, ESMF5x7[2, 2])

    def test2_3x4_to_5x7_degr(self):
        # Test non-periodic grid returning double grid resolution
        roESMF = CdmsRegrid(self.fromGrid3x4, self.toGrid5x7,
                            dtype='float64',
                            srcGridMask=self.data3x4.mask,
                            regridTool='ESMF',
                            periodicity=0,
                            regridMethod='Conserve',
                            coordSys='degrees')
        diag = {'srcAreas': 0, 'dstAreas': 0,
                'srcAreaFractions': 0, 'dstAreaFractions': 0}
        ESMF5x7 = roESMF(self.data3x4, diag=diag)
        dstMass = (ESMF5x7 * diag['dstAreas']).sum()
        srcMass = (self.data3x4 * diag['srcAreas']
                                * diag['srcAreaFractions']).sum()
#        self.assertLess(abs(srcMass - dstMass), self.eps)
        self.assertEqual(self.data3x4[0, 0], ESMF5x7[0, 0])

    def test3_5x7_to_3x4(self):
        # Test double grid resolution original grid resolution
        # Just the corner is one valued
        roESMF = CdmsRegrid(self.fromGrid5x7, self.toGrid3x4,
                            dtype='float64',
                            srcGridMask=self.data5x7.mask,
                            regridTool='ESMF',
                            periodicity=0,
                            regridMethod='Conserve', coordSys='cart')
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
        self.assertNotEqual(self.data5x7[0, 0], ESMF3x4[0, 0])
        self.assertLess(0.25 - ESMF3x4[0, 0], self.eps)

    def test4_5x7_to_3x4_4Corner_Cells_equal_1(self):
        # Test double grid resolution original grid resolution.
        # Reset the data in 0:2, 0:2 to 1
        self.data5x7[:2, :2] = 1
        self.data5x7.mask[1, 1] = True

        roESMF = CdmsRegrid(self.fromGrid5x7, self.toGrid3x4,
                            dtype='float64',
                            srcGridMask=self.data5x7.mask,
                            regridTool='ESMF',
                            periodicity=0,
                            regridMethod='Conserve', coordSys='cart')
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
        self.assertNotEqual(self.data5x7[0, 0], ESMF3x4[0, 0])
        self.assertEqual(self.data5x7[0, 0], 1.0)
        self.assertEqual(ESMF3x4[0, 0], 0.5)


if __name__ == '__main__':
    print ""  # Spacer
    ESMF.Manager(debug=True)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestESMFRegridderMasked)
    unittest.TextTestRunner(verbosity=1).run(suite)
    if PLOT:
        pylab.show()
