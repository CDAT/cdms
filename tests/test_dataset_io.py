import cdms2
import numpy
import string
import os
import sys

cdms2.setNetcdfUseParallelFlag(0)

from cdms2.variable import WriteNotImplemented
from cdms2.avariable import NotImplemented
import basetest


class TestDatasetIO(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestDatasetIO, self).setUp()
        self.file = self.getDataFile('test.xml')
        self.u = self.file['u']
        self.v = self.file['v']

    def testFileAttributes(self):
        self.assertEqual(self.file.id, "test")

    def testScalarSlice(self):
        u = self.u
        scalar = u[0, 0, 0]
        self.assertEqual(scalar, 0.0)

    def testSize(self):
        u = self.u
        self.assertEqual(u.size(), 1536)

    def testStride(self):
        u = self.u
        uslice = u[:, 4:12, 8:24]
        comp = self.test_arr[0, :, 4:12, 8:24]
        self.assertTrue(numpy.ma.allequal(uslice, comp))

    def testNegativeSlice(self):
        u = self.u[0:-1]
        comp2 = self.test_arr[0, 0:-1]
        self.assertTrue(numpy.ma.allequal(u, comp2))

    def testVariableAttributeRead(self):
        u = self.u
        self.assertEqual(u.units, "m/s")

    def testTimeAxisRead(self):
        t = self.u.getTime()
        self.assertTrue(numpy.ma.allequal(t[:], [0., 366., 731., ]))
        self.assertEqual(t.units, "days since 2000-1-1")
        self.assertTrue(t.isVirtual() == 0)

    def testGrid(self):
        grid = self.u.getGrid()
        self.assertEqual(grid.id, "grid_16x32")

    def testExtendedWrite(self):
        out = self.getTempFile('testExtendWrite.nc', "w")
        u0 = self.u.subSlice(0)
        u1 = self.u.subSlice(1)
        u2 = self.u.subSlice(2)
        v0 = self.v.subSlice(0)
        v1 = self.v.subSlice(1)
        v2 = self.v.subSlice(2)
        uout = out.write(u0)
        vout = out.write(
            v2,
            attributes=self.v.attributes,
            id='v',
            extend=1,
            index=2)
        out.write(u1, index=1)
        out.write(v0)
        out.write(u2)
        out.write(v1)
        out.sync()
        tout = out.axes["time"]
        # Make sure reversed properly when read from file
        t_reversed = tout[::-1]
        self.assertEqual(len(t_reversed), len(tout))
        self.assertEqual(t_reversed[0], tout[-1])
        self.assertTrue(numpy.ma.allclose(uout.getSlice(), self.u[:]))
        out.close()

    def testStridePartitioned(self):
        strided = self.u[0:3:2, 0:16:2, 0:32:2]

    def testClosedOperations(self):
        u = self.u
        transient_u = self.u[:]
        self.file.close()
        with self.assertRaises(cdms2.CDMSError):
            badslice = u[:, 4:12, 8:24]
            badu = u.getValue()

        with self.assertRaises(cdms2.CDMSError):
            badu = u.getValue()

        with self.assertRaises(cdms2.CDMSError):
            badslice = u[0:1]

        with self.assertRaises(cdms2.CDMSError):
            u[0, 0, 0] = -99.9

        with self.assertRaises(cdms2.CDMSError):
            u[0:1] = -99.9

        with self.assertRaises(cdms2.CDMSError):
            u.assignValue(transient_u)


if __name__ == '__main__':
    basetest.run()
