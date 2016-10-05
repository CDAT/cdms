import sys,cdms2,cdat_info
import basetest


class TestSlicingMetadata(basetest.CDMSBaseTest):
    def testSliceMetadata(self):
        f = self.getFile(cdat_info.get_sampledata_path() + "/clt.nc")
        s = f("clt")
        s0 = s[0]
        self.assertTrue(s0.getAxis(0).isLatitude())
        self.assertTrue(s0.getAxis(1).isLongitude())

if __name__ == "__main__":
    basetest.run()
