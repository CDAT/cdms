# Forecast test

import sys
import cdms2, os, numpy
import cdms2.forecast
import cdms2.tvariable
from cdms2.cdscan import main as cdscan
import cdat_info
import basetest


class TestForecastIO(basetest.CDMSBaseTest):
    def testForecast(self):

        # Generate some test data, then write it out.  This section doesn't test anything.
        xaxis = cdms2.createAxis( [ 0.1, 0.2 ], id='x' )
        taxis = cdms2.createAxis( [ 10.0, 20.0 ], id='t' )
        taxis.units='seconds'    # required!
        #...  Note that this is seconds since the forecast was generated, i.e. the appropriate
        # standard_name is "forecast_period".
        taxis.standard_name = 'forecast_period'

        taxis.designateTime()
        v1 = cdms2.tvariable.TransientVariable( [[1.1,1.2],[2.1,2.1]], axes=[taxis,xaxis], id='var' )
        v2 = cdms2.tvariable.TransientVariable( [[3.1,3.2],[4.1,4.1]], axes=[taxis,xaxis], id='var' )
        v3 = cdms2.tvariable.TransientVariable( [[5.1,5.2],[6.1,6.1]], axes=[taxis,xaxis], id='var' )
        date1 = cdms2.tvariable.TransientVariable( 20100825, id='nbdate' )
        sec1 = cdms2.tvariable.TransientVariable( 0, id='nbsec' )
        date2 = cdms2.tvariable.TransientVariable( 20100826, id='nbdate' )
        sec2 = cdms2.tvariable.TransientVariable( 0, id='nbsec' )
        date3 = cdms2.tvariable.TransientVariable( 20100827, id='nbdate' )
        sec3 = cdms2.tvariable.TransientVariable( 0, id='nbsec' )
        f1 = self.getTempFile('test_fc1','w')
        f2 = self.getTempFile('test_fc2','w')
        f3 = self.getTempFile('test_fc3','w')
        f1.write(v1)
        f1.write(date1)
        f1.write(sec1)
        f2.write(v2)
        f2.write(date2)
        f2.write(sec2)
        f3.write(v3)
        f3.write(date3)
        f3.write(sec3)
        f1.close()
        f2.close()
        f3.close()

        os.chdir(self.tempdir)
        cdscan("cdscan -q --forecast -x test_fc.xml test_fc1 test_fc2 test_fc3".split())
        print os.listdir(self.tempdir)
        # Read in the data.

        fcs = cdms2.forecast.forecasts('test_fc.xml', ("2010-08-25","2010-08-27"))
        vin = fcs('var')
        fcaxis = vin._TransientVariable__domain[0][0]
        tinaxis = vin._TransientVariable__domain[1][0]
        xinaxis = vin._TransientVariable__domain[2][0]

        # Test vin against original data, looking especially at the forecast axis.
        # The following should be True, error otherwise:
        self.assertEqual(vin.id, v1.id)
        self.assertTrue(numpy.alltrue( vin[0,:,:]==v1[:,:] ))
        self.assertTrue(numpy.alltrue( vin[1,:,:]==v2[:,:] ))
        self.assertEqual(vin.shape, (2,2,2))
        self.assertTrue(numpy.allclose( tinaxis._data_ , taxis._data_ ))
        self.assertTrue(numpy.allclose( xinaxis._data_ , xaxis._data_ ))
        tinaxis = vin.getAxis(1)
        self.assertTrue(tinaxis.isTime())
        self.assertFalse(xinaxis.isTime())
        self.assertFalse(fcaxis.isTime())
        self.assertTrue(fcaxis.isForecast())
        self.assertEqual(fcaxis.shape, (3,))
        #...Note that fcaxis is an Axis so its shape comes from len(fcaxis.node) which is the
        # number of forecasts described in test_fc.xml; in contrast for TransientAxis the shape
        # would be len(fcaxis._data_) which is the number of forecasts that have been read.
        self.assertEqual(fcaxis._data_, [2010082500000L, 2010082600000L])
        self.assertEqual(fcaxis.id, 'fctau0')

if __name__ == "__main__":
    basetest.run()