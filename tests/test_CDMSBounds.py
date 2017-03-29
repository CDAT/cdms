import cdms2
import unittest
import numpy
import os

class TestCDMSAutobounds(unittest.TestCase):

    def createFile(self, offset):
        # Create a test netCDF file and load it with one grid of data.
        #
        testFile = cdms2.open('testFile.nc', 'w')
        latitudes = numpy.linspace(-89.975, 89.975,
                                   num=3600, dtype=numpy.float32)

        minVal = float('-180.0')
        maxVal = float('180.0')
        halfStep = 0.5 * (maxVal - minVal) / float(7200)
        minVal += halfStep
        maxVal -= halfStep
        values = numpy.linspace(minVal, maxVal, num=7200, dtype=numpy.float32)
        longitudes = values + offset

        times = numpy.array([0.5])

        lat = testFile.createAxis('latitude', latitudes)
        lon = testFile.createAxis('longitude', longitudes)
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
        self.createFile(offset)
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
        self.assertAlmostEqual(bounds[-1, 1], 180.000984192, 5)

    def test_Bounds11th(self):
        exponent = -11
        offset = 2.0**exponent
        self.createFile(offset)
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


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCDMSAutobounds)
    unittest.TextTestRunner(verbosity=2).run(suite)
