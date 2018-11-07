import cdms2
import os
import sys
import cdat_info
import basetest
import platform
from shutil import copyfile
import MV2
import cdms2
from cdms2 import serialize, deserialize
import dask.array.ma as dam
from distributed.utils_test import gen_cluster


import dask.array as da

@gen_cluster(client=True)
def testDaskArrayFV(c, s, a, b):
    f = cdms2.open(cdat_info.get_sampledata_path()+"/clt.nc")
    dataFV=f["clt"]
    myDaskArray= da.from_array(dataFV, chunks=(1,46,72)) 
    x=c.compute(myDaskArray)
    myResult = yield x
    assert MV2.allclose(myResult, dataFV)==True
    f.close()
@gen_cluster(client=True)

def testDaskArrayTV(c, s, a, b):
    f = cdms2.open(cdat_info.get_sampledata_path()+"/clt.nc")
    dataTV=f("clt")
    myDaskArray= da.from_array(dataTV, chunks=(1,46,72)) 
    y=c.compute(myDaskArray)
    myTVResult = yield y
    assert MV2.allclose(myTVResult, dataTV)==True
    f.close()

class TestDask(basetest.CDMSBaseTest):

    def setUp(self):
        super(TestDask,self ).setUp()
        self.f = cdms2.open(cdat_info.get_sampledata_path()+"/clt.nc")
        self.dataTV=self.f("clt")
        self.dataFV=self.f["clt"]                                                                                                                                                                                     

    def testSerializeDeserialize(self):
        result = deserialize(*serialize(self.dataFV))
        self.assertTrue(MV2.allclose(result, self.dataFV))
        result = deserialize(*serialize(self.dataTV))
        self.assertTrue(MV2.allclose(result, self.dataTV))

        
    def tearDown(self):
        self.f.close()

if __name__ == "__main__":
    basetest.run()

