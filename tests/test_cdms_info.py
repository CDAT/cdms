import unittest
import cdat_info
import os
import cdms2

class CDMSInfo(unittest.TestCase):
    def testInfo(self):
        f = cdms2.open(os.path.join(cdat_info.get_sampledata_path(),"clt.nc"))
        s=f("clt")
        s.info()

    def testUnicode(self):
        
        f = cdms2.open(cdat_info.get_sampledata_path()+"/clt.nc")
        kargs = {u"latitude":(-20,20)}
        s=f("clt")
        s2 =s.subRegion(**kargs)
