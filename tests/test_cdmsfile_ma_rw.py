import cdms2
import numpy
import os
import sys
import basetest


class TestCDMSFileMaskedArrayReadWrite(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestCDMSFileMaskedArrayReadWrite, self).setUp()
        self.file = self.getTempFile("readwrite4.nc", "w")
        self.readonly = self.getDataFile("readonly.nc")
        self.timearr = numpy.ma.array([0.0, 366.0, 731.0])
        self.latarr = numpy.ma.arange(
            self.NLAT) * (180. / (self.NLAT - 1)) - 90.
        self.lonarr = numpy.ma.arange(self.NLON) * (360.0 / self.NLON)
        self.timestr = ['2000', '2001', '2002']
        self.u = self.test_arr[0]
        tobj = self.file.createAxis('time', numpy.ma.array([self.timearr[1]]))
        tobj.units = 'days since 2000-1-1'
        latobj = self.file.createAxis('latitude', self.latarr)
        latobj.units = 'degrees_north'
        lonobj = self.file.createAxis('longitude', self.lonarr)
        lonobj.units = 'degrees_east'
        self.var = self.file.createVariable(
            'u', numpy.float, (tobj, latobj, lonobj))
        self.var.units = 'm/s'

    def testSetSlice(self):
        self.var[:] = self.u[0]
        self.assertTrue(numpy.ma.allequal(self.var, self.u[0]))

    def testAssignValue(self):
        self.var.assignValue(self.u[0])
        self.assertTrue(numpy.ma.allequal(self.var, self.u[0]))

    def testSetItem(self):
        self.var[0, 4:12] = -self.u[0, 4:12]
        self.assertTrue(numpy.ma.allequal(self.var[0, 4:12], -self.u[0, 4:12]))

    def setVarAttributes(self):
        attrs = var.attributes
        self.var.long_name = "Test variable"
        self.var.param = -99
        self.assertEqual(self.var.param, -99)

    def setFileAttributes(self):
        attrs = f.attributes
        f.Conventions = "CF1.0"
        self.assertEqual(f.Conventions, "CF1.0")

    def testRewriteAxis(self):
        latAttrs = self.var.getLatitude().attributes
        self.var.getLatitude()[self.NLAT // 2] = 6.5
        self.assertNotEqual(self.var.getLatitude()[
                            self.NLAT // 2], self.latarr[self.NLAT // 2])
        self.var.getLatitude().standard_name = "Latitude"
        self.assertEqual(self.var.getLatitude().standard_name, "Latitude")
        self.latarr[self.NLAT // 2] = 6.5

    def testMaskedVariable(self):
        masked = self.file.createVariable(
            "umasked",
            cdms2.CdDouble,
            (self.var.getTime(),
             self.var.getLatitude(),
             self.var.getLongitude()),
            fill_value=-99.9)
        umask = self.test_arr[0, 0]
        umask.set_fill_value(-111.1)
        umask[4:12, 8:24] = numpy.ma.masked
        fmask = numpy.ma.getmask(umask)
        masked[:] = umask
        masked.units = "m/s"
        masked.long_name = "Eastward wind velocity"

        uh = self.readonly["u"]
        u2 = self.file.createVariableCopy(uh, "u2")
        u2[:] = uh[:]

        x0 = self.test_arr[0, 0]
        um2 = numpy.ma.where(numpy.ma.less(x0, 128.0), numpy.ma.masked, x0)
        self.file.write(um2, id="u3")
        self.file.close()
        test_file = self.getTempFile("readwrite4.nc", "r+")
        var = test_file["umasked"]
        var = var.subSlice(squeeze=1)
        self.assertEqual(var.getMissing(), -99.9)
        mask = numpy.ma.getmask(var)
        self.assertIsNotNone(mask)
        self.assertTrue(numpy.ma.allequal(mask, fmask))

        grid = var.getGrid()
        grid.setMask(mask)
        m = grid.getMask()
        self.assertTrue(numpy.ma.allequal(m, mask))

        u3 = test_file['u3']
        lon = u3.getAxis(1)
        lon.designateLongitude()
        b = lon.getBounds()
        self.assertTrue(isinstance(b, numpy.ndarray))


if __name__ == "__main__":
    basetest.run()
