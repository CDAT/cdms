import cdms2
import os
import basetest


class TestCompression(basetest.CDMSBaseTest):
    def testDefault(self):
        a = cdms2.MV2.zeros((1000, 2100), 'd')
        f = self.getTempFile("default.nc", 'w')
        f.write(a)

    def testZeroAllSettings(self):
        a = cdms2.MV2.zeros((1000, 2100), 'd')
        cdms2.setNetcdfShuffleFlag(0)
        cdms2.setNetcdfDeflateFlag(0)
        cdms2.setNetcdfDeflateLevelFlag(0)

        f = self.getTempFile("nothing.nc", 'w')
        f.write(a)

    def testJustShuffle(self):
        a = cdms2.MV2.zeros((1000, 2100), 'd')
        cdms2.setNetcdfShuffleFlag(1)
        cdms2.setNetcdfDeflateFlag(0)
        cdms2.setNetcdfDeflateLevelFlag(0)

        f = self.getTempFile("justshuffle.nc", 'w')
        f.write(a)

    def testJustDeflate6(self):
        a = cdms2.MV2.zeros((1000, 2100), 'd')
        cdms2.setNetcdfShuffleFlag(0)
        cdms2.setNetcdfDeflateFlag(1)
        cdms2.setNetcdfDeflateLevelFlag(6)

        f = self.getTempFile("justdeflate6.nc", 'w')
        f.write(a)

    def testJustDeflate9(self):
        a = cdms2.MV2.zeros((1000, 2100), 'd')
        cdms2.setNetcdfDeflateLevelFlag(9)

        f = self.getTempFile("crap_justdeflate9.nc",'w')
        f.write(a)

if __name__ == "__main__":
    basetest.run()
