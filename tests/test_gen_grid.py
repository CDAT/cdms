import cdms2
import numpy
import basetest


class TestGenericGrids(basetest.CDMSBaseTest):
    def testSetGrid(self):

        inc = 1
        nb_lat = 180
        startLat, nlat, deltaLat, startLon, nlon, deltaLon = (-90 + inc/2., nb_lat, inc,
                                                              -180 + inc/2., 2*nb_lat, inc)

        uniform_grid = cdms2.createUniformGrid(startLat, nlat, deltaLat, startLon, nlon, deltaLon)

        lat_weights, lon_weights = uniform_grid.getWeights()
        grid_weights = numpy.outer(lat_weights, lon_weights)

        weight_var = cdms2.createVariable(grid_weights, grid=uniform_grid, id='cell_weight')

        weight_var2 = cdms2.MV2.array(grid_weights)
        weight_var2.setGrid(uniform_grid)

        weight_var3 = cdms2.createVariable(grid_weights, axes=[uniform_grid.getLatitude(),
                                                               uniform_grid.getLongitude()], id='cell_weights')
        from io import StringIO
        import sys

        old_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result

        print(weight_var.info())
        result_string = result.getvalue()
        sys.stdout = old_stdout
        self.assertIn('latitude', result_string)

        result = StringIO()
        sys.stdout = result
        print(weight_var2.info())
        result_string = result.getvalue()
        sys.stdout = old_stdout
        self.assertIn('latitude', result_string)

        result = StringIO()
        sys.stdout = result
        print(weight_var3.info())
        result_string = result.getvalue()
        sys.stdout = old_stdout
        self.assertIn('latitude', result_string)



    def testGenGrids2(self):
        latb = [62.47686472, 69.70600048]
        lonb = [102.87075526, 105.51598035]
        fn = self.getDataFile('sampleCurveGrid4.nc')
        s = fn("sample")
        g = s.getGrid()
        lat = g.getLatitude()
        lon = g.getLongitude()
        g2 = cdms2.createGenericGrid(lat, lon)
        datalat = g2.getLatitude().getBounds()[22, 25]
        datalon = g2.getLongitude().getBounds()[22, 25]
        self.assertTrue(numpy.ma.allclose(datalat, latb))
        self.assertTrue(numpy.ma.allclose(datalon, lonb))

    def testGenGrids(self):

        datb = numpy.array([693., 694., ])
        latb = numpy.array([-26.67690036, -30.99890917, ])
        lonb = numpy.array([92.41822415, 94.4512163, ])
        f = self.getDataFile('sampleGenGrid3.nc')

        # Slice a file variable on a curvilinear grid: by coordinates ...
        samp = f['sample']
        x = samp(lat=(-32, -25), lon=(90, 95))
        self.assertFalse(not numpy.ma.allequal(x.data, datb))

        grid = x.getGrid()
        self.assertFalse(grid.shape != (2,))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        # ... and by index
        y = samp[693:695]
        self.assertFalse(not numpy.ma.allequal(y, datb))
        grid = y.getGrid()
        self.assertFalse(not (grid.shape == (2,)))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        # -------------------------------------------------------------

        # Slice a TRANSIENT variable on a curvilinear grid: by coordinates ...

        samp = f['sample']
        x = samp(lat=(-32, -25), lon=(90, 95))
        self.assertFalse(not numpy.ma.allequal(x.data, datb))

        grid = x.getGrid()
        self.assertFalse(grid.shape != (2,))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        # ... and by index
        y = samp[693:695]
        self.assertFalse(not numpy.ma.allequal(y, datb))
        grid = y.getGrid()
        self.assertFalse(not (grid.shape == (2,)))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        # -------------------------------------------------------------

        # Computing with variables, coordinate variables
        x2 = (9. / 5.) * x + 32.
        lat2 = x2.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))

        # -------------------------------------------------------------

        # Slice a coordinate variable, computation

        latsamp = samp.getLatitude()
        latx = latsamp(cell=(693, 694))
        self.assertFalse(not numpy.ma.allclose(latx.data, latb, atol=1.e-5))
        latx = latsamp[693:695]
        self.assertFalse(not numpy.ma.allclose(latx.data, latb, atol=1.e-5))
        latrad = latsamp * numpy.pi / 180.0

        # -------------------------------------------------------------

        f = self.getDataFile('cdtest14.xml')

        # Slice a DATASET variable on a curvilinear grid: by coordinates ...
        samp = f['sample']
        x = samp(lat=(-32, -25), lon=(90, 95))
        self.assertFalse(not numpy.ma.allequal(x.data, datb))

        grid = x.getGrid()
        self.assertFalse(grid.shape != (2,))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        # ... and by index
        y = samp[693:695]
        self.assertFalse(not numpy.ma.allequal(y, datb))
        grid = y.getGrid()
        self.assertFalse(not (grid.shape == (2,)))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))


if __name__ == "__main__":
    basetest.run()
