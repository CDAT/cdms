import cdat_info
import cdms2
import unittest
import numpy
import os


class TestCDMSAutobounds(unittest.TestCase):

    def createFile(self, minLon, maxLon, offset):
        # Create a test netCDF file and load it with one grid of data.
        #
        testFile = cdms2.open('testFile.nc', 'w')
        latitudes = numpy.linspace(-89.975, 89.975,
                                   num=3600, dtype=numpy.float32)

        minVal = minLon
        maxVal = maxLon
        halfStep = 0.5 * (maxVal - minVal) / float(7200)
        minVal += halfStep
        maxVal -= halfStep
        values = numpy.linspace(minVal, maxVal, num=7200, dtype=numpy.float32)
        longitudes = values + offset

        times = numpy.array([0.5])

        lat = testFile.createAxis('latitude', latitudes)
        lat.standard_name = "latitude"
        lat.units = "degrees_north"
        lon = testFile.createAxis('longitude', longitudes)
        lon.standard_name = "longitude"
        lon.units = "degrees_east"
        time = testFile.createAxis('time', times)
        time.units = 'days since 1900-01-01 00:00:00'

        data = numpy.zeros((1, 3600, 7200), dtype=numpy.float32)
        data[0, :, :] = numpy.random.rand(3600, 7200)

        var = testFile.createVariable('tos', 'float32', [time, lat, lon])
        var.standard_name = 'sea_surface_temperature'
        var.units = 'K'
        var[:] = data[:]
        testFile.close()
        del var, testFile

    def setup(self):
        cdms2.setAutoBounds('on')

    def teardown(self):
        os.remove("testFile.nc")

    def test_Bounds10th(self):
        exponent = -10
        offset = 2.0**exponent
        self.createFile(-180, 180, offset)
        # Open the test file and get the CDMS2 longitude axis.
        #
        testFile = cdms2.open('testFile.nc')
        var = testFile.variables['tos']
        axes = var.getAxisList()
        for axis in axes:
            if 'longitude' == axis.id:
                break
        values = axis[:]
        bounds = axis.getBounds()
        self.assertAlmostEqual(bounds[0, 0], -179.999031067, 5)
        self.assertEqual(bounds[-1, 1], 180.00096893310547)
#        self.assertAlmostEqual(bounds[-1, 1], 180.000984192, 5)
        os.remove('testFile.nc')

    def test_BoundsReverse11th(self):
        exponent = -11
        offset = 2.0**exponent
        self.createFile(180, -180, offset)
        # Open the test file and get the CDMS2 longitude axis.
        #
        testFile = cdms2.open('testFile.nc')
        var = testFile.variables['tos']
        axes = var.getAxisList()
        for axis in axes:
            if 'longitude' == axis.id:
                break
        values = axis[:]
        bounds = axis.getBounds()
        self.assertEqual(bounds[0, 0], 180.0)
        self.assertEqual(bounds[-1, 1], -180.0)
        os.remove('testFile.nc')

    def test_Bounds11th(self):
        exponent = -11
        offset = 2.0**exponent
        self.createFile(-180, 180, offset)
        # Open the test file and get the CDMS2 longitude axis.
        #
        testFile = cdms2.open('testFile.nc')
        var = testFile.variables['tos']
        axes = var.getAxisList()
        for axis in axes:
            if 'longitude' == axis.id:
                break
        values = axis[:]
        bounds = axis.getBounds()
        self.assertEqual(bounds[0, 0], -180.0)
        self.assertEqual(bounds[-1, 1], 180.0)
        os.remove('testFile.nc')

    def test_BoundsPolar(self):
        f=cdms2.open(cdat_info.get_sampledata_path() + "/stereographic.nc")
        s=f('seaice_conc_cdr')
        firstBounds = s.getAxis(1).getBounds()[0]
        lastBounds = s.getAxis(1).getBounds()[-1]
        self.assertEqual(firstBounds[0], 5850000.)
        self.assertEqual(firstBounds[1], 5825000.)
        self.assertEqual(lastBounds[0], -5325000.)
        self.assertEqual(lastBounds[1], -5350000.)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCDMSAutobounds)
    unittest.TextTestRunner(verbosity=2).run(suite)
