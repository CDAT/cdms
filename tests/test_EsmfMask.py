import unittest
import cdms2
import ESMF
import cdat_info
import os


class TestESMFMask(unittest.TestCase):
    def setUp(self):

        self.f = cdms2.open(
            os.path.join(
                cdat_info.get_sampledata_path(),
                "clt.nc"))
        self.s = self.f('clt', slice(0, 12)).astype("float64")
        self.u = self.f('u').astype("float64")

    def tearDown(self):
        self.f.close()

    def testMask(self):
        s2 = cdms2.MV2.masked_greater(self.s, 67)
        s3 = s2.regrid(
            self.u.getGrid(),
            regridTool='esmf',
            regridMethod='conserve')
        self.assertAlmostEqual(s3.min(), 0.0, places=2)
        self.assertAlmostEqual(s3.max(), 66.99, places=2)
#        self.assertEqual(s3.mask.sum(), 63429)
        s4 = self.s.regrid(
            self.u.getGrid(),
            regridTool='esmf',
            regridMethod='conserve')
        self.assertAlmostEqual(s4.min(), 0, places=2)
        self.assertAlmostEqual(s4.max(), 100.0, places=2)
        s3 = s2.regrid(
            self.u.getGrid(),
            regridTool='esmf',
            regridMethod='linear')
        self.assertAlmostEqual(s3.min(), 0.0)
        self.assertAlmostEqual(s3.max(), 66.91, places=2)
#        self.assertEqual(s3.mask.sum(), 65698)
        s4 = self.s.regrid(
            self.u.getGrid(),
            regridTool='esmf',
            regridMethod='linear')
        self.assertAlmostEqual(s4.min(), 0.0)
        self.assertAlmostEqual(s4.max(), 100.0, places=1)

    def testMask2(self):
        data = cdms2.open(os.path.join(
                cdat_info.get_sampledata_path(),
                "ta.nc"))("ta")
        tmp = cdms2.open(os.path.join(
                cdat_info.get_sampledata_path(),
               "sftlf.nc"))
        sft = tmp("sftlf")
        tmp.close()

        data2 = cdms2.MV2.masked_where(cdms2.MV2.less(sft,50.),data)

        tGrid = cdms2.createUniformGrid(-88.875, 72, 2.5, 0, 144, 2.5)

        for mthd in ["conservative", "linear"]:
            print("USING REGRID METHOD:",mthd)
            data3 = data2.regrid(tGrid, regridTool="esmf", regridMethod=mthd, mask=data2.mask)



if __name__ == "__main__":
    ESMF.Manager()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestESMFMask)
    unittest.TextTestRunner(verbosity=2).run(suite)
