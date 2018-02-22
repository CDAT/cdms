import unittest
import cdat_info
import os
import cdms2

class CDMSInfo(unittest.TestCase):
    def testInfo(self):
        f = cdms2.open(os.path.join(cdat_info.get_sampledata_path(),"clt.nc"))
        s=f("clt")
        s.info()
    def testAxis(self):
        axis = cdms2.createAxis(cdms2.createVariable([10.], id='height', missing=1e20))
        print(axis)

