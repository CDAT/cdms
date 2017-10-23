import unittest
import cdms2
import numpy
import subprocess
import tempfile
import os

class CDMSNc3(unittest.TestCase):
    def testOutputNC3(self):
        tempdir = tempfile.mkdtemp()
        data = numpy.random.random((12,10))
        cdms2.useNetcdf3()
        fnm = os.path.join(tempdir,"temp_cdms2file.nc")
        with cdms2.open(fnm,"w") as f:
            f.write(data,id="data")
            f.close()
            cmd = "ncdump -hs {0}".format(fnm)
            cmd = cmd.split()
            p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            o, e = p.communicate()
            self.assertEqual(o.find("_IsNetcdf4"),-1)
