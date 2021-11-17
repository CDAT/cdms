import cdms2
import cdat_info
import basetest
import MV2
import cdms2
from distributed.protocol import serialize, deserialize
from distributed.utils_test import gen_cluster
# import dask.array.ma as dam
import dask.array as da
import pickle
from nose.plugins.attrib import attr

@attr("cdms_dask")
@gen_cluster(client=True)
async def testDaskArrayFV(c, s, a, b):
    f = cdms2.open(cdat_info.get_sampledata_path()+"/clt.nc")
    dataFV=f["clt"]
    myDaskArray= da.from_array(dataFV, chunks=(1,46,72)) 
    x=c.compute(myDaskArray)
    myResult = await x
    assert MV2.allclose(myResult, dataFV)==True
    f.close()

@attr("cdms_dask")
@gen_cluster(client=True)
async def testDaskArrayTV(c, s, a, b):
    f = cdms2.open(cdat_info.get_sampledata_path()+"/clt.nc")
    dataTV=f("clt")
    myDaskArray= da.from_array(dataTV, chunks=(1,46,72)) 
    y=c.compute(myDaskArray)
    myTVResult = await y
    assert MV2.allclose(myTVResult, dataTV)==True
    f.close()

class TestDask(basetest.CDMSBaseTest):

    def setUp(self):
        super(TestDask, self).setUp()
        self.f = cdms2.open(cdat_info.get_sampledata_path()+"/clt.nc")
        self.dataTV=self.f("clt")
        self.dataFV=self.f["clt"]                                                                                                                                                                                     
    def testpickle(self):
        newvar = pickle.loads(pickle.dumps(self.dataTV))
        self.assertTrue(MV2.allclose(self.dataTV, newvar))

    def testTVdumps(self):
        TVstate = self.dataTV.dumps()
        newvar=cdms2.fromJSON(TVstate)
        self.assertTrue(MV2.allclose(self.dataTV, newvar))

    @attr("cdms_dask")
    def testTVSerializeDeserialize(self):
        #
        # make sure that JSON is uncomporessed since
        # zlib compress is called by __getstate__()
        #
        TVstate = self.dataTV.__getstate__()
        newvar=cdms2.fromJSON(TVstate)
        self.assertTrue(MV2.allclose(self.dataTV, newvar))

    @attr("cdms_dask")
    def testSerializeDeserialize(self):
        result = deserialize(*serialize(self.dataFV))
        self.assertTrue(MV2.allclose(result, self.dataFV))
        result = deserialize(*serialize(self.dataTV))
        self.assertTrue(MV2.allclose(result, self.dataTV))

        
    def tearDown(self):
        self.f.close()

if __name__ == "__main__":
    basetest.run()

