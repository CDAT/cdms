import basetest
import cdms2
import numpy


class TestCDMSFileReadWrite(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestCDMSFileReadWrite, self).setUp()
        self.timearr = numpy.array([0.0,366.0,731.0])
        self.latarr = numpy.arange(self.NLAT)*(180./(self.NLAT-1))-90.
        self.lonarr = numpy.arange(self.NLON)*(360.0/self.NLON)
        self.timestr = ['2000', '2001', '2002']
        self.u = self.test_arr[0]
        self.file = self.getTempFile('readwrite3.nc', "w")
        tobj = self.file.createAxis('time', numpy.array([self.timearr[1]]))
        tobj.units = 'days since 2000-1-1'
        latobj = self.file.createAxis('latitude', self.latarr)
        latobj.units = 'degrees_north'
        lonobj = self.file.createAxis('longitude', self.lonarr)
        lonobj.units = 'degrees_east'
        self.var = self.file.createVariable('u', cdms2.CdDouble, (tobj, latobj, lonobj))
        self.var.units = 'm/s'

    def testSetSlice(self):
        self.var[:] = self.u[0]
        self.assertTrue(numpy.ma.allequal(self.var, self.u[0]))

    def testAssignValue(self):
        self.var.assignValue(self.u[0])
        self.assertTrue(numpy.ma.allequal(self.var, self.u[0]))

    def testSetItem(self):
        self.var[0,4:12] = -self.u[0, 4:12]
        self.assertTrue(numpy.ma.allequal(self.var[0,4:12], -self.u[0, 4:12]))

    def testReadWriteAttrs(self):
        self.var.long_name = "Test variable"
        self.var.param = -99
        self.assertEqual(self.var.long_name, "Test variable")
        self.assertEqual(self.var.param, -99)

    def testSetFileAttrs(self):
        self.file.Conventions = "CF1.0"
        self.assertEqual(self.file.Conventions, "CF1.0")

    def testRewriteAxis(self):
        self.var.getLatitude()[self.NLAT / 2] = 6.5
        self.assertNotEqual(self.var.getLatitude()[self.NLAT/2], self.latarr[self.NLAT/2])
        self.var.getLatitude().standard_name = "Latitude"
        self.assertEqual(self.var.getLatitude().standard_name, "Latitude")
        self.latarr[self.NLAT / 2] = 6.5

    def testWriteVariable(self):
        p = self.file.createVariable("p0", cdms2.CdDouble, ())
        p.assignValue(-99.9)

    def testReread(self):
        self.testSetFileAttrs()
        self.testWriteVariable()
        self.testReadWriteAttrs()
        self.testSetItem()
        self.testRewriteAxis()
        self.file.close()
        g = self.getTempFile("readwrite3.nc", "r+")
        self.assertEqual(g.Conventions, "CF1.0")
        var = g.variables["u"]
        self.assertEqual(var.long_name, "Test variable")
        self.assertEqual(var[0, 4, 0], -self.u[0, 4, 0])
        self.assertEqual(var.getLatitude()[self.NLAT/2], self.latarr[self.NLAT/2])
        self.assertEqual(var.getLatitude().standard_name, "Latitude")
        p0 = g["p0"]
        val = p0.getValue()
        self.assertEqual(val, -99.9)
        newlat = var.getLatitude()[:]
        newlat[0] = newlat[0] - 1
        var.getLatitude().assignValue(newlat)
        g.close()
        h = self.getTempFile("readwrite3.nc")
        self.assertEqual(h["u"].getLatitude()[0], newlat[0])

if __name__ == '__main__':
    import unittest
    unittest.main()
