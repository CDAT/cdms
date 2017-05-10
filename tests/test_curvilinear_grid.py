# Test curvilinear grids

import cdms2
import numpy
import os
import sys
import basetest


class TestCurvilinearGrids(basetest.CDMSBaseTest):
    def testCurvilinear(self):
        datb = numpy.array(
            [[697., 698., 699., 700., 701., 702., ],
             [745., 746., 747., 748., 749., 750., ],
             [793., 794., 795., 796., 797., 798., ],
             [841., 842., 843., 844., 845., 846., ],
             [889., 890., 891., 892., 893., 894., ]])

        latb = numpy.array(
            [[-4.10403354, -4.10403354, -4.10403354, -4.10403354, -4.10403354, -4.10403354, ],
             [4.18758287, 4.18338422, 4.17731439,
                 4.1696268, 4.16062822, 4.150657, ],
             [12.94714126, 12.9074324, 12.85002385,
                 12.7773095, 12.69218757, 12.59785563, ],
             [22.13468161, 22.02120307, 21.85711809,
                 21.6492418, 21.40582783, 21.1359872, ],
             [31.57154392, 31.3483558, 31.0255852, 30.61656963, 30.13745176, 29.60604602, ]])

        lonb = numpy.array(
            [[99.66846416, 109.38520711, 119.00985881, 128.50802363, 137.84762448,
                146.99940213, ],
             [99.66892374, 109.38595529, 119.01087021, 128.50926506, 137.84905702,
                147.00098336, ],
                [99.68231972, 109.40769163, 119.04011194, 128.54493672, 137.88992043,
                 147.04571884, ],
                [99.74090681, 109.50235408, 119.16667376, 128.69809779, 138.06369873,
                 147.23389768, ],
                [99.89478673, 109.74975596, 119.49504331, 129.09174691, 138.50528817,
                 147.70588394, ]])

        maskb = numpy.array(
            [[0, 0, 0, 0, 0, 0, ],
             [0, 0, 0, 0, 0, 0, ],
             [0, 0, 0, 0, 0, 0, ],
             [0, 0, 0, 0, 0, 0, ],
             [1, 1, 1, 1, 1, 0, ]], 'b')

        f = self.getDataFile('sampleCurveGrid4.nc')

        #-------------------------------------------------------------

        # Slice a file variable on a curvilinear grid: by coordinates ...
        samp = f['sample']
        x = samp()
        x = samp(lat=(-10, 30), lon=(90, 150))
        self.assertFalse(not numpy.ma.allequal(x.data, datb))
        self.assertFalse(not numpy.ma.allequal(x.mask, maskb))

        grid = x.getGrid()
        self.assertFalse(not (grid.shape == (5, 6)))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        # ... and by index
        y = samp[14:19, 25:31]
        self.assertFalse(not numpy.ma.allequal(y, datb))

        grid = y.getGrid()
        self.assertFalse(not (grid.shape == (5, 6)))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        #-------------------------------------------------------------

        # Slice a TRANSIENT variable on a curvilinear grid: by coordinates ...
        samp = f['sample']
        x = samp(lat=(-10, 30), lon=(90, 150))
        self.assertFalse(not numpy.ma.allequal(x.data, datb))
        self.assertFalse(not numpy.ma.allequal(x.mask, maskb))

        grid = x.getGrid()
        self.assertFalse(not (grid.shape == (5, 6)))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        # ... and by index
        y = samp[14:19, 25:31]
        self.assertFalse(not numpy.ma.allequal(y, datb))

        grid = y.getGrid()
        self.assertFalse(not (grid.shape == (5, 6)))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        #-------------------------------------------------------------

        # Computing with variables, coordinate variables
        x2 = (9. / 5.) * x + 32.
        lat2 = x2.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))

        #-------------------------------------------------------------

        # Slice a coordinate variable, computation

        latsamp = samp.getLatitude()
        latx = latsamp(x=(25, 30), y=(14, 18))
        self.assertFalse(not numpy.ma.allclose(latx.data, latb, atol=1.e-5))
        latx = latsamp[14:19, 25:31]
        self.assertFalse(not numpy.ma.allclose(latx.data, latb, atol=1.e-5))
        latrad = latsamp * numpy.pi / 180.0

        f.close()

        #-------------------------------------------------------------

        # Slice a DATASET variable on a curvilinear grid: by coordinates ...
        f = self.getDataFile('cdtest13.xml')

        samp = f['sample']
        x = samp(lat=(-10, 30), lon=(90, 150))
        self.assertFalse(not numpy.ma.allequal(x.data, datb))
        self.assertFalse(not numpy.ma.allequal(x.mask, maskb))

        grid = x.getGrid()
        self.assertFalse(not (grid.shape == (5, 6)))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        # ... and by index
        y = samp[14:19, 25:31]
        self.assertFalse(not numpy.ma.allequal(y, datb))

        grid = y.getGrid()
        self.assertFalse(not (grid.shape == (5, 6)))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        #-------------------------------------------------------------

        # Test grid conversion
        samp = f('sample')
        curveGrid = samp.getGrid()
        genGrid = curveGrid.toGenericGrid()
        f.close()

        g = self.getDataFile('u_2000.nc')
        samp = g('u')
        rectGrid = samp.getGrid()
        curveGrid = rectGrid.toCurveGrid()
        genGrid = curveGrid.toGenericGrid()


if __name__ == "__main__":
    basetest.run()
