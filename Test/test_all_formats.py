import cdms2
import os
import sys
import cdat_info
import basetest


class TestFormats(basetest.CDMSBaseTest):

    def testPP(self):
        f = self.getDataFile('testpp.pp')

    def testHDF(self):
        f = self.getDataFile("tdata.hdf")

    def testDRS(self):
        f = self.getFile(os.path.join(cdat_info.get_sampledata_path(), 'ta_300_850_PCM_O_mm_xy_wa_r0000_0000.dic'))

    def testDAP(self):
        f = cdms2.open('http://test.opendap.org/opendap/hyrax/data/nc/coads_climatology.nc')
        f.close()

if __name__ == "__main__":
    basetest.run()
