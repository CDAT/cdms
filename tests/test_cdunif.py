import sys
XY=str(sys.version_info.major)+"."+str(sys.version_info.minor)
sys.path.insert(3,sys.prefix + "/lib/python"+XY+"/site-packages/cdms2")
import basetest
import Cdunif
import unittest
import time
import cdat_info
import os


class TestCdunif(basetest.CDMSBaseTest):

    def setUp(self):
        super(TestCdunif, self).setUp()
        pth = cdat_info.get_sampledata_path()
        self.filename = os.path.join(
            pth,
            "161122_RobertPincus_multiple_input4MIPs_radiation_RFMIP_UColorado-RFMIP-20161122_none.nc")

    def testFile(self):
        f=Cdunif.CdunifFile(self.filename)
        f.variables.keys()
        var=f.variables['expt_label']
        self.assertEqual(var.getitem(slice(0,1,1))[0].decode('utf8'), 'Present day (PD)')
        self.assertEqual(var[0][0].decode('utf8'),'Present day (PD)')

if __name__ == '__main__':
    unittest.main()

