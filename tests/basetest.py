import unittest
import shutil
import numpy
import tempfile
import cdms2
import os


class CDMSBaseTest(unittest.TestCase):
    def getFile(self, path, mode="r"):
        f = cdms2.open(path, mode)
        self.files.append(f)
        return f

    def getDataFilePath(self, name):
        pth = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(pth, "data", name)

    def getDataFile(self, name):
        return self.getFile(self.getDataFilePath(name))

    def getTempFile(self, path, mode="r"):
        return self.getFile(os.path.join(self.tempdir, path), mode)

    def setUp(self):
        global cdms2
        cdms2 = reload(cdms2)
        self.orig_cwd = os.getcwd()
        self.files = []
        self.NTIME = 3
        self.NLAT = 16
        self.NLON = 32
        self.test_arr = numpy.ma.arange(float(2 * self.NTIME * self.NLAT * self.NLON))
        self.test_arr.shape = (2, self.NTIME, self.NLAT, self.NLON)
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        for f in self.files:
            f.close()
        os.chdir(self.orig_cwd)
        shutil.rmtree(self.tempdir)

    def assertArraysEqual(self, arr1, arr2):
        arr1 = numpy.array(arr1)
        arr2 = numpy.array(arr2)
        if arr1.shape != arr2.shape:
            raise AssertionError("Arrays have different shape; left: %s, right %s." % (arr1.shape, arr2.shape))
        self.assertTrue(numpy.allclose(arr1, arr2), "Arrays differ.")


def run():
    unittest.main()
