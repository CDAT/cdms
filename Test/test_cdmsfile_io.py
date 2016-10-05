import basetest
import cdms2
import numpy
import string
import os
import sys
from numpy.ma import masked


class TestCDMSFileIO(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestCDMSFileIO, self).setUp()
        self.readOnly = self.getDataFile("readonly.nc")
        self.u = self.readOnly["u"]
        self.u_masked = self.readOnly["umasked"]

    def tearDown(self):
        super(TestCDMSFileIO, self).tearDown()

    def testSize(self):
        self.assertEqual(self.u.size(), 512)

    def testAxisRead(self):
        lon = self.readOnly["longitude"]
        self.assertTrue(numpy.ma.allequal(lon.getValue(), lon[:]))
        self.assertTrue(lon.isVirtual() == 0)

    def testSliceRead(self):
        uslice = self.u[:, 4:12, 8:24]
        compare = self.test_arr[0, 0, 4:12, 8:24]
        self.assertTrue(numpy.ma.allequal(uslice, compare))

    def testMaskedSlice(self):
        sliceMasked = self.u_masked[:, 0:4, 8:24]
        compmask = self.test_arr[0, 0, 0:4, 8:24]
        self.assertTrue(numpy.ma.allequal(sliceMasked, compmask))

    def testVarAttributes(self):
        self.assertEqual(self.u.units, "m/s")

    def testVarAxis(self):
        t = self.u.getTime()
        self.assertTrue(numpy.ma.allequal(t[:], [0.]))
        self.assertEqual(t.units, "days since 2000-1-1")

    def testVarGrid(self):
        g = self.u.getGrid()
        self.assertEqual(g.id, "grid_16x32")

    def testFileAppend(self):
        # Just make sure we don't get any exceptions
        f = cdms2.open(os.path.join(self.tempdir, "junk.nc"), "a")
        xx = self.u.subSlice()
        f.write(xx)
        f.close()

    def testWraparoundGrid(self):
        uwrap = self.u.subRegion(longitude=(-180, 180))
        self.assertIsNotNone(uwrap.getGrid())

    def testClosedOperations(self):
        u = self.u
        transient_u = self.u[:]
        self.readOnly.close()
        with self.assertRaises(cdms2.CDMSError):
            badslice = u[:,4:12,8:24]
            badu = u.getValue()

        with self.assertRaises(cdms2.CDMSError):
            badu = u.getValue()

        with self.assertRaises(cdms2.CDMSError):
            badslice = u[0:1]

        with self.assertRaises(cdms2.CDMSError):
            u[0,0,0]=-99.9

        with self.assertRaises(cdms2.CDMSError):
            u[0:1]=-99.9

if __name__ == '__main__':
    basetest.run()