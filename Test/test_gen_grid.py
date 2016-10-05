## Automatically adapted for numpy.oldnumeric Aug 01, 2007 by 

#!/usr/bin/env python



import cdms2, numpy, os, sys
import basetest


class TestGenericGrids(basetest.CDMSBaseTest):
    def testGenGrids(self):

        datb = numpy.array([ 693., 694.,])
        latb = numpy.array([-26.67690036,-30.99890917,])
        lonb = numpy.array([92.41822415, 94.4512163 ,])

        f = self.getDataFile('sampleGenGrid3.nc')

        # Slice a file variable on a curvilinear grid: by coordinates ...
        samp = f['sample']
        x = samp(lat=(-32,-25), lon=(90,95))
        self.assertFalse(not numpy.ma.allequal(x.data, datb))

        grid = x.getGrid()
        self.assertFalse(grid.shape!=(2,))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        # ... and by index
        y = samp[693:695]
        self.assertFalse(not numpy.ma.allequal(y, datb))
        grid = y.getGrid()
        self.assertFalse(not (grid.shape==(2,)))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        #-------------------------------------------------------------

        # Slice a TRANSIENT variable on a curvilinear grid: by coordinates ...

        samp = f['sample']
        x = samp(lat=(-32,-25), lon=(90,95))
        self.assertFalse(not numpy.ma.allequal(x.data, datb))

        grid = x.getGrid()
        self.assertFalse(grid.shape!=(2,))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        # ... and by index
        y = samp[693:695]
        self.assertFalse(not numpy.ma.allequal(y, datb))
        grid = y.getGrid()
        self.assertFalse(not (grid.shape==(2,)))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        #-------------------------------------------------------------

        # Computing with variables, coordinate variables
        x2 = (9./5.)*x + 32.
        lat2 = x2.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))

        #-------------------------------------------------------------

        # Slice a coordinate variable, computation

        latsamp = samp.getLatitude()
        latx = latsamp(cell=(693,694))
        self.assertFalse(not numpy.ma.allclose(latx.data, latb, atol=1.e-5))
        latx = latsamp[693:695]
        self.assertFalse(not numpy.ma.allclose(latx.data, latb, atol=1.e-5))
        latrad = latsamp*numpy.pi/180.0

        #-------------------------------------------------------------

        f = self.getDataFile('cdtest14.xml')

        # Slice a DATASET variable on a curvilinear grid: by coordinates ...
        samp = f['sample']
        x = samp(lat=(-32,-25), lon=(90,95))
        self.assertFalse(not numpy.ma.allequal(x.data, datb))

        grid = x.getGrid()
        self.assertFalse(grid.shape!=(2,))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

        # ... and by index
        y = samp[693:695]
        self.assertFalse(not numpy.ma.allequal(y, datb))
        grid = y.getGrid()
        self.assertFalse(not (grid.shape==(2,)))
        lat = grid.getLatitude()
        self.assertFalse(not numpy.ma.allclose(lat.data, latb, atol=1.e-5))
        lon = grid.getLongitude()
        self.assertFalse(not numpy.ma.allclose(lon.data, lonb, atol=1.e-5))

if __name__ == "__main__":
    basetest.run()
