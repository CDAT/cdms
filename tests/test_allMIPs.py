import urllib
import cdms2
import os
import sys
import cdat_info
import basetest


class TestMIPS(basetest.CDMSBaseTest):
    def setUp(self):
        myurl = "http://uvcdat.llnl.gov/cdat/sample_data/161122_RobertPincus_multiple_input4MIPs_radiation_RFMIP_UColorado-RFMIP-20161122_none.nc"
        super(TestMIPS, self).setUp()
        urllib.urlretrieve(myurl, "161122_RobertPincus_multiple_input4MIPs_radiation_RFMIP_UColorado-RFMIP-20161122_none.nc")

    def tearDown(self):
        super(TestMIPS, self).tearDown()
        os.remove("161122_RobertPincus_multiple_input4MIPs_radiation_RFMIP_UColorado-RFMIP-20161122_none.nc")

    def testinput4MIPs(self):
        f=cdms2.open("161122_RobertPincus_multiple_input4MIPs_radiation_RFMIP_UColorado-RFMIP-20161122_none.nc")
        self.assertEqual(f['water_vapor'].getLatitude()[0:4].tolist(), [-28.5, 28.5, 31.5, 87.])
        self.assertEqual(f['water_vapor'].getLongitude()[0:4].tolist(), [27., 24., 162., 126.])
        labels=f['expt_label'][:]
        self.assertEqual(labels.tolist(), ['Present day (PD)', 'Pre-industrial (PI) greenhouse gas concentrations', '4xCO2', '"future"', '0.5xCO2', '2xCO2', '3xCO2', '8xCO2', 'PI CO2', 'PI CH4', 'PI N2O', 'PI O3', 'PI HCs', '+4K', '+4K, const. RH', 'PI all', '"future" all', 'LGM'])


if __name__ == "__main__":
    basetest.run()
