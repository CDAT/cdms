"""
$Id: testEsmf_3x4_6x8_Bilinear.py 2369 2012-07-11 23:51:51Z dkindig $


Plotting routine for tests in regrid2.ESMF using ginned up data
"""

import cdms2
from regrid2 import esmf
from regrid2.mvGenericRegrid import GenericRegrid
from openCreateData import dataNoPeri
import unittest
import ESMF
import numpy

import re


def makeGrid(nx, ny):
    dims = (nx, ny)
    xbot, xtop, ybot, ytop = 0, 4, 0, 4
    x = numpy.linspace(xbot, xtop, nx)
    y = numpy.linspace(ybot, ytop, ny)

    xx = numpy.outer(x, numpy.ones(ny))
    yy = numpy.outer(numpy.ones(nx), y)

    theGrid = [xx, yy]

    theData = xx + yy

    return dims, theGrid, theData


class TestESMFRegridderConserve(unittest.TestCase):
    def setUp(self):

        # This is to show how to use dataNoPeri
        # class dataNoPeri:
        fd3x4 = dataNoPeri(4, 3, (1, 4), (1, 3))
        fd5x7 = dataNoPeri(7, 5, (1, 4), (1, 3))

        # Each Grid below is the same. This is just to make it clear which
        # grid is being used
        self.fromGrid3x4 = [fd3x4.coords[1], fd3x4.coords[0]]
        self.toGrid3x4 = self.fromGrid3x4

        self.fromGrid5x7 = [fd5x7.coords[1], fd5x7.coords[0]]
        self.toGrid5x7 = self.fromGrid5x7

        # Get the data for each grid
        self.data3x4 = fd3x4.data
        self.data5x7 = fd5x7.data

        self.data3x4[:] = 1
        self.data3x4[1, 1] = 0

        self.dimsSml, self.gridSml, self.dataSml = makeGrid(4, 3)
        self.dimsLrg, self.gridLrg, self.dataLrg = makeGrid(6, 5)

        self.eps = 1.e-5

    def test1_esmf(self):
        """
        Simple test using esmf.py directly
        """
        srcMaxIndex = numpy.array(self.dimsSml, dtype=numpy.int32)
        srcGrid = esmf.EsmfStructGrid(srcMaxIndex, coordSys=ESMF.CoordSys.CART)
        srcGrid.setCoords(self.gridSml)

        dstMaxIndex = numpy.array(self.dimsLrg, dtype=numpy.int32)
        dstGrid = esmf.EsmfStructGrid(dstMaxIndex, coordSys=ESMF.CoordSys.CART)
        dstGrid.setCoords(self.gridLrg)

        srcField = esmf.EsmfStructField(srcGrid, 'srcData', datatype=self.dataSml.dtype,
                                        staggerloc=ESMF.StaggerLoc.CENTER)
        srcField.setLocalData(self.dataSml * 0.0 - 1, ESMF.StaggerLoc.CENTER)
        dstField = esmf.EsmfStructField(dstGrid, 'dstData', datatype=self.dataLrg.dtype,
                                        staggerloc=ESMF.StaggerLoc.CENTER)
        dstField.setLocalData(self.dataLrg, ESMF.StaggerLoc.CENTER)

        # The grids should be different
        self.assertFalse(
            numpy.all(
                srcField.getPointer() == dstField.getPointer()))

        ro = esmf.EsmfRegrid(dstField, srcField)
        ro()

        srcAr = numpy.reshape(srcField.getPointer(), self.dimsSml)
        dstAr = numpy.reshape(dstField.getPointer(), self.dimsLrg)
        self.assertEqual(srcAr[-1, -1], dstAr[-1, -1])

    def test2_Increase_Res(self):
        """
        Simple change in resolution
        """

        roESMF = GenericRegrid(self.gridSml, self.gridLrg, self.dataSml.dtype,
                               'linear', 'ESMF', coordSys='Cart')
        roESMF.computeWeights()
        dstESMF = self.gridLrg[0] * 0 - 1
        roESMF.apply(self.dataSml, dstESMF)
        self.assertLess(self.dataSml[-1, -1] - dstESMF[-1, -1], self.eps)

    def test3_3x4_to_3x4(self):
        for d in dir(unittest):
            if re.search('assert', d):
                print(d)
        # Test NonPeriodic grid Returning same grid

        roESMF = GenericRegrid(self.fromGrid3x4, self.toGrid3x4, self.data3x4.dtype,
                               'linear', 'ESMF', coordSys='Cart')
        roESMF.computeWeights()
        ESMF3x4 = numpy.ones(self.data3x4.shape) * (-999)
        roESMF.apply(self.data3x4, ESMF3x4)
        self.assertEqual(self.data3x4[0, 0], ESMF3x4[0, 0])
        self.assertEqual(1.0, ESMF3x4[0, 0])

    def test4_3x4_to_5x7(self):
        # Test NonPeriodic grid Returning double grid resolution
        roLibCF = GenericRegrid(self.fromGrid3x4, self.toGrid5x7, self.data3x4.dtype,
                                'linear', 'LibCF')
        roLibCF.computeWeights()
        LibCF5x7 = numpy.ones(self.data5x7.shape, dtype=numpy.float32) * (-999)
        roLibCF.apply(self.data3x4, LibCF5x7)
        roESMF = GenericRegrid(self.fromGrid3x4, self.toGrid5x7, self.data3x4.dtype,
                               'linear', 'ESMF', coordSys='cart')
        roESMF.computeWeights()
        ESMF5x7 = numpy.ones(self.data5x7.shape) * (-999)
        roESMF.apply(self.data3x4, ESMF5x7)
        ro2 = GenericRegrid(self.fromGrid5x7, self.toGrid3x4, self.data5x7.dtype,
                            'linear', 'ESMF', coordSys='Cart')
        ro2.computeWeights()
        ESMF3x4 = numpy.ones(self.data3x4.shape) * (-999)
        ro2.apply(ESMF5x7, ESMF3x4)
        self.assertEqual(self.data3x4[0, 0], ESMF5x7[0, 0])
        self.assertEqual(0.75, ESMF5x7[1, 1])

    def test5_5x7_to_3x4(self):
        # Test double grid resolution original grid resolution
        # Just the corner is one valued
        roESMF = GenericRegrid(self.fromGrid5x7, self.toGrid3x4, self.data5x7.dtype,
                               'linear', 'ESMF', coordSys='Cart')
        roESMF.computeWeights()
        ESMF3x4 = numpy.ones(self.data3x4.shape) * (-999)
        roESMF.apply(self.data5x7, ESMF3x4)
        self.assertEqual(ESMF3x4[0, 0], self.data5x7[0, 0])
        self.assertEqual(ESMF3x4[1, 1], 0.0)


if __name__ == '__main__':
    print("")  # Spacer
    ESMF.Manager()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestESMFRegridderConserve)
    unittest.TextTestRunner(verbosity=2).run(suite)
