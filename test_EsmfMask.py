import unittest
import cdms2
import ESMF
import vcs

class TestESMFMask(unittest.TestCase):
    def setUp(self):

        self.f=cdms2.open(vcs.sample_data+"/clt.nc")
        self.s=self.f('clt',slice(0,12)).astype("float64")
        self.u=self.f('u').astype("float64")

    def tearDown(self):
        self.f.close()

    def testMask(self):
        s2=cdms2.MV2.masked_greater(self.s,67)
        s3=s2.regrid(self.u.getGrid(), regridTool='esmf', regridMethod='conserve')
        self.assertAlmostEqual(s3.min(), 27.87, places=2)
        self.assertAlmostEqual(s3.max(), 126.64, places=2)
        self.assertEqual(s3.mask.sum(), 76046)
        s4=self.s.regrid(self.u.getGrid(), regridTool='esmf', regridMethod='conserve')
        self.assertAlmostEqual(s4.min(), 27.87, places=2)
        self.assertAlmostEqual(s4.max(), 133486.21, places=2)
        s3=s2.regrid(self.u.getGrid(), regridTool='esmf', regridMethod='linear')
        self.assertEqual(s3.min(), -1.58054790449e-13)
        self.assertEqual(s3.max(), 66.9125536521)
        self.assertEqual(s3.mask.sum(), 53370)
        s4=self.s.regrid(self.u.getGrid(), regridTool='esmf', regridMethod='linear')
        self.assertEqual(s4.min(), -8.08732061894e-15)

if __name__ == "__main__":
    ESMF.Manager()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestESMFMask)
    unittest.TextTestRunner(verbosity = 2).run(suite)


