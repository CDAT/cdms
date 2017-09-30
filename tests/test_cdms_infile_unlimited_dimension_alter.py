import unittest
import cdms2
import numpy
import os
import cdat_info


class TestCDMSInFileUnlimtedDimAlter(unittest.TestCase):
    def testInFileUnlimitedDimAlter(self):

        fnm = os.path.join(cdat_info.get_sampledata_path(),"clt.nc")
        f=cdms2.open(fnm)
        s=f("clt")
        f.close()
        cdms2.setNetcdfDeflateFlag(0)
        cdms2.setNetcdfDeflateLevelFlag(0)
        cdms2.setNetcdfShuffleFlag(0)
        cdms2.setNetcdf4Flag(1)
        cdms2.setNetcdfClassicFlag(1)
        f=cdms2.open("nc4.nc","w")
        f.write(s)
        f.close()

        timesValues = s.getTime()[:]
        f=cdms2.open("nc4.nc","r+")
        t=f["time"]
        t[:]=t[:]*100.
        f.close()

        f=cdms2.open("nc4.nc")
        s=f("clt")
        t = s.getTime()
        self.assertEqual(len(t),len(timesValues))
        self.assertTrue(numpy.allclose(t[:],timesValues*100.))
        os.remove("nc4.nc")


if __name__ == '__main__':
    print("")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCDMSInFileUnlimtedDimAlter)
    unittest.TextTestRunner(verbosity=2).run(suite)

