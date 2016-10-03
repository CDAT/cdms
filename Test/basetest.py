import unittest
import shutil
import numpy
import tempfile


class CDMSBaseTest(unittest.TestCase):
    def setUp(self):
        self.NTIME = 3
        self.NLAT = 16
        self.NLON = 32
        self.test_arr = numpy.ma.arange(float(2 * self.NTIME * self.NLAT * self.NLON))
        self.test_arr.shape = (2, self.NTIME, self.NLAT, self.NLON)
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)
