import numpy
import cdms2, cdtime, copy, os, sys
import basetest


class TestTransientVariables(basetest.CDMSBaseTest):
    def testTV(self):
        f = self.getDataFile("test.xml")

        x = self.test_arr
        v = f.variables['v']
        vp = x[1, 1:, 4:12, 8:25]
        vp2 = vp[1, 1:-1, 1:]
        tv = v.subRegion((366., 731., 'ccn'), (-42., 42., 'ccn'), (90., 270.))
        tvv = v[0:2, 0:10, 30:40]

        # Make sure we retrieve a scalar
        xx = tv[1, 7, 15]
        self.assertFalse(isinstance(xx, numpy.ndarray))

        # Variable get: axis, grid, latitude, level, longitude, missing, order, time, len, typecode

        vaxis0 = v.getAxis(0)
        axis0 = tv.getAxis(0)
        self.assertFalse(not numpy.ma.allequal(axis0[:], vaxis0[1:]))

        taxis = tv.getTime()
        taxisarray = taxis[:]
        vaxisarray = vaxis0[1:]
        self.assertFalse(not numpy.ma.allequal(taxisarray, vaxisarray))

        vaxis1 = v.getAxis(1)
        lataxis = tv.getLatitude()
        self.assertFalse(not numpy.ma.allequal(lataxis[:], vaxis1[4:12]))

        vaxis2 = v.getAxis(2)
        lonaxis = tv.getLongitude()

        #
        #  default is 'ccn' -- now it 8:25
        #
        self.assertFalse(not numpy.ma.allequal(lonaxis[:], vaxis2[8:25]))

        tv = v.subRegion((366., 731., 'ccn'), (-42., 42., 'ccn'), (90., 270.))
        missing_value = v.getMissing()
        self.assertEqual(missing_value, -99.9)

        tmv = tv.fill_value
        # TODO: Did the default value of fill_value/missing change? This is failing.
        self.assertEqual(tmv, -99.9)

        grid = tv.getGrid()
        self.assertFalse(grid is None)

        order = tv.getOrder()
        self.assertEqual(order, 'tyx')

        self.assertEqual(len(tv), 2)

        # get TV domain
        domain = tv.getDomain()
        self.assertEqual(len(domain), 3)

        # getRegion of a TV
        tv2 = tv.getRegion(731., (-30., 30., 'ccn'), (101.25, 270.0))
        self.assertFalse(not numpy.ma.allequal(tv2, vp2))

        # Axis get: bounds, calendar, value, isXXX, len, subaxis, typecode
        axis1 = tv.getAxis(1)
        axis2 = tv.getAxis(2)
        bounds = axis1.getBounds()
        self.assertFalse(bounds is None)
        self.assertEqual(axis0.getCalendar(), cdtime.MixedCalendar)
        val = axis1.getValue()
        self.assertFalse(not numpy.ma.allequal(axis1.getValue(), axis1[:]))
        self.assertFalse(not axis0.isTime())
        self.assertFalse(not axis1.isLatitude())
        self.assertFalse(not axis2.isLongitude())
        self.assertTrue(axis2.isCircular())
        self.assertEqual(len(axis2), 17)

        saxis = axis2.subAxis(1, -1)
        self.assertFalse(not numpy.ma.allequal(saxis[:], axis2[1:-1]))
        self.assertEqual(axis1.typecode(), numpy.sctype2char(numpy.float))
        self.assertEqual(axis2.shape, (17, ))

        # Axis set: bounds, calendar
        savebounds = copy.copy(bounds)
        bounds[0, 0]=-90.0
        axis1.setBounds(bounds)
        nbounds = axis1.getBounds()
        self.assertFalse(not numpy.ma.allequal(bounds, nbounds))
        axis0.setCalendar(cdtime.NoLeapCalendar)
        self.assertEqual(axis0.getCalendar(), cdtime.NoLeapCalendar)
        gaussaxis = cdms2.createGaussianAxis(32)
        try:
            testaxis = cdms2.createGaussianAxis(31)
        except:
            markError('Gaussian axis with odd number of latitudes')

        # Grid get: axis, bounds, latitude, longitude, mask, order, type, weights, subgrid, subgridRegion
        a1 = grid.getAxis(1)
        self.assertFalse(not numpy.ma.allequal(a1[:], axis2[:]))

        bounds[0, 0]=savebounds[0, 0]
        axis1.setBounds(bounds)
        latbounds, lonbounds = grid.getBounds()
        self.assertFalse(not numpy.ma.allequal(latbounds, savebounds))
        glat = grid.getLatitude()
        glon = grid.getLongitude()
        mask = grid.getMask()
        order = grid.getOrder()
        self.assertEqual(order, 'yx')
        gtype = grid.getType()
        weights = grid.getWeights()
        subg = grid.subGrid((1, 7), (1, 15))
        subg2 = grid.subGridRegion((-30., 30., 'ccn'), (101.25, 247.5, 'ccn'))
        self.assertFalse(not numpy.ma.allequal(subg.getLongitude()[:], subg2.getLongitude()[:]))
        self.assertEqual(grid.shape, (8, 17))

        # Grid set: bounds, mask, type
        latbounds[0, 0] = -90.0
        grid.setBounds(latbounds, lonbounds)
        nlatb, nlonb = grid.getBounds()
        self.assertFalse(not numpy.ma.allequal(latbounds, nlatb))
        grid.setType('uniform')
        self.assertEqual(grid.getType(), 'uniform')

        yy = numpy.ma.reshape(numpy.ma.arange(272.0), tv.shape)
        tv.assignValue(yy)
        self.assertFalse(not numpy.ma.allequal(tv, yy))
        tv3 = tv[0:-1]
        self.assertEqual(tv3.shape, (1, 8, 17))

        # Create a transient variable from scratch
        oldlat = tv.getLatitude()
        oldBounds = oldlat.getBounds()
        newlat = cdms2.createAxis(numpy.ma.array(oldlat[:]), numpy.ma.array(oldBounds))
        b = newlat.getBounds()
        b[0, 0] = -48.
        newlat.setBounds(b)

        tv4 = cdms2.createVariable(tv[:], copy=1, fill_value=255.)
        tv4[0, 1:4] = 20.0

        self.assertEqual(tv[:, ::-1, :].shape, tv.shape)

        # Test asVariable
        www = cdms2.asVariable(tv4)
        self.assertFalse(www is not tv4)
        www = cdms2.asVariable(v, 0)
        self.assertFalse(www is not v)
        www = cdms2.asVariable([1., 2., 3.])
        self.assertFalse(not cdms2.isVariable(www))

        # Check that createAxis allows an axis as an argument
        lon = f.axes['longitude']
        newlon = cdms2.createAxis(lon)
        self.assertFalse(newlon.typecode() == 'O')

        # Test take of axis without bounds
        newlat.setBounds(None)
        samp = cdms2.axis.take(newlat, (2, 4, 6))

if __name__ == "__main__":
    basetest.run()
