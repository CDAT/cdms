import pdb
import cdms2
import os
import sys
import cdat_info
import basetest


class TestFormats(basetest.CDMSBaseTest):
    def testPP(self):
        f = self.getDataFile('testpp.pp')
        data=f['ps']
        self.assertEqual(data.missing_value, -1.07374182e+09)

    def testHDF(self):
        if cdat_info.CDMS_INCLUDE_HDF == "yes":
            f = self.getDataFile("tdata.hdf")

    def testDRS(self):
        f = self.getDataFile("dvtest1.dic")
        data = f['a']
        self.assertEqual(data.missing_value, 1e20)

    def testDAP(self):
        f = cdms2.open('http://test.opendap.org/opendap/hyrax/data/nc/coads_climatology.nc')
        data=f['SST']
        self.assertEqual(data.missing_value, -1e34)
        f.close()

    def testGRIB2(self):
        f = self.getDataFile("testgrib2.ctl")
        data=f['wvhgtsfc']
        self.assertEqual(data.missing_value, 9.999e20)


if __name__ == "__main__":
    basetest.run()
