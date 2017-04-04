import requests
import cdms2
import cdutil
import os
import sys
import cdat_info
import basetest
import numpy


class TestMIPS(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestMIPS, self).setUp()
        self.filename="obs_timeseries.nc"
        myurl = "http://uvcdat.llnl.gov/cdat/sample_data/" + self.filename
        r = requests.get(myurl, stream=True)
        with open(self.filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)

    def tearDown(self):
        super(TestMIPS, self).tearDown()
        os.remove(self.filename)

    def testAnnualSeasonalAverage(self):
        f=cdms2.open(self.filename, "r")

        # Read in the raw data EXCLUDING a leap year
        obs_timeseries1 = f('obs',  time=slice(0,48)) # 1900.1. to 1903.12.
        # Read in the raw data INCLUDING a leap year
        obs_timeseries2 = f('obs',  time=slice(0,60)) # 1900.1. to 1904.12., 1904 is year lear

        ### Truncate first Jan, Feb and last Dec before get Annual cycle anomaly ... (to have fair DJF seasonal mean later)
        obs_timeseries1 = obs_timeseries1[2:-1]
        obs_timeseries2 = obs_timeseries2[2:-1]

        ### Set monthly time bounds ...
        cdutil.setTimeBoundsMonthly(obs_timeseries1)
        cdutil.setTimeBoundsMonthly(obs_timeseries2)

        #### Removing Annual cycle ...
        obs_timeseries_ano1 = cdutil.ANNUALCYCLE.departures(obs_timeseries1)
        obs_timeseries_ano2 = cdutil.ANNUALCYCLE.departures(obs_timeseries2)

        #### Calculate time average ...
        obs_timeseries_ano_timeave1 = cdutil.averager(obs_timeseries_ano1, axis='t')  ## This should be zero and it does
        obs_timeseries_ano_timeave2 = cdutil.averager(obs_timeseries_ano2, axis='t')  ## This should be zero BUT it does NOT

        #### SEASONAL MEAN TEST ####
        obs_timeseries_ano1_DJF = cdutil.DJF(obs_timeseries_ano1, criteriaarg=[0.95,None]) 
        obs_timeseries_ano2_DJF = cdutil.DJF(obs_timeseries_ano2, criteriaarg=[0.95,None])
        obs_timeseries_ano1_JJA = cdutil.JJA(obs_timeseries_ano1, criteriaarg=[0.95,None])
        obs_timeseries_ano2_JJA = cdutil.JJA(obs_timeseries_ano2, criteriaarg=[0.95,None])

        #### Calculate time average ...
        obs_timeseries_ano1_DJF_timeave = cdutil.averager(obs_timeseries_ano1_DJF, axis='t') ## This should be zero and it does
        obs_timeseries_ano2_DJF_timeave = cdutil.averager(obs_timeseries_ano2_DJF, axis='t') ## This should be zero BUT it does NOT

        obs_timeseries_ano1_JJA_timeave = cdutil.averager(obs_timeseries_ano1_JJA, axis='t') ## This should be zero and it does
        obs_timeseries_ano2_JJA_timeave = cdutil.averager(obs_timeseries_ano2_JJA, axis='t') ## This should be zero and it does

        numpy.testing.assert_almost_equal(obs_timeseries_ano_timeave2, obs_timeseries_ano_timeave1,10)
        numpy.testing.assert_almost_equal(obs_timeseries_ano1_JJA_timeave, obs_timeseries_ano2_JJA_timeave, 10)
        numpy.testing.assert_almost_equal(obs_timeseries_ano1_DJF_timeave, obs_timeseries_ano2_DJF_timeave, 10)

if __name__ == "__main__":
    basetest.run()


