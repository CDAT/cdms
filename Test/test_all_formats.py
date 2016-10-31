import cdms2
import os
import sys
import cdat_info
import basetest


class TestFormats(basetest.CDMSBaseTest):
    def testPP(self):
        f = self.getDataFile('testpp.pp')

    def testHDF(self):
        if cdat_info.CDMS_INCLUDE_HDF == "yes":
            f = self.getDataFile("tdata.hdf")

    def testDRS(self):
        f = self.getDataFile("dvtest1.dic")

    def testDAP(self):
        f = cdms2.open('http://test.opendap.org/opendap/hyrax/data/nc/coads_climatology.nc')
        f.close()

    def testGRIB2(self):
        f = self.getDataFile("testgrib2.ctl")

if __name__ == "__main__":
    basetest.run()
