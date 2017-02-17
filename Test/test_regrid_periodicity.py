import urllib
import cdms2
import os
import sys
import cdat_info
import basetest
import numpy as np
import basetest
import pdb

modFile="model_ANN_climo.nc"
obsFile="GPCP_ANN_climo.nc"
class TestRegrid(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestRegrid, self).setUp()
        myurl = "http://uvcdat.llnl.gov/cdat/sample_data/"+obsFile
#        urllib.urlretrieve(myurl, obsFile)
        myurl = "http://uvcdat.llnl.gov/cdat/sample_data/"+modFile
#        urllib.urlretrieve(myurl, modFile)

    def tearDown(self):
        super(TestRegrid, self).tearDown()
        #os.remove(obsFile)
        #os.remove(modFile)

    def testPeriodicity(self):
        reference_data_set = obsFile
        test_data_set = modFile

        f_obs = cdms2.open(reference_data_set)
        f_mod = cdms2.open(test_data_set)

        obs= f_obs('PRECT')

        mod = (f_mod('PRECC') + f_mod('PRECL'))*3600.0*24.0*1000.0
        mod.units = 'mm/day'

        self.assertEqual([obs.getLongitude()[0],obs.getLongitude()[-1]], [1.25, 358.75])
        self.assertEqual([mod.getLongitude()[0],mod.getLongitude()[-1]], [0., 358.59375])

        obs_grid = obs.getGrid()

        # Regrid model to obs grid using 'linear'
        mod_reg = mod.regrid(obs_grid, regridTool='esmf', regridMethod='linear',
                             periodicity=1)
        self.assertListEqual(mod_reg[0,:,-1].tolist(), 
               [0.18226054310798645, 0.170532688498497,   0.19422821700572968, 0.2062055915594101, 
                0.25475791096687317, 0.26943284273147583, 0.7159037590026855,  1.3457400798797607, 
                1.4986687898635864,  1.5531318187713623,  1.6910326480865479,  1.8841710090637207, 
                2.1220641136169434,  2.4442174434661865,  2.8163115978240967,  3.2974066734313965, 
                3.6789047718048096,  3.8148319721221924,  3.8304808139801025,  3.52917218208313, 
                3.008916139602661,   2.4214160442352295,  1.8726664781570435,  1.384545087814331, 
                0.9055019617080688,  0.6338639259338379,  0.49946314096450806, 0.3987405598163605, 
                0.36161595582962036, 0.3593190312385559,  0.3188425898551941,  0.22578200697898865, 
                0.28796881437301636, 0.632653534412384,   1.4626545906066895,  2.7277863025665283, 
                4.371249198913574,   5.769023418426514,   4.440964698791504,   4.568368434906006, 
                4.426982402801514,   3.134274959564209,   1.7195935249328613,  0.8663696646690369, 
                0.5404248237609863,  0.39392685890197754, 0.3023046851158142,  0.3181740343570709, 
                0.6334905028343201,  1.7460370063781738,  2.0546133518218994,  1.6389271020889282, 
                2.389214515686035,   3.570681571960449,   3.1908936500549316,  2.6651766300201416, 
                2.6674928665161133,  2.6791656017303467,  2.3955864906311035,  2.8772478103637695, 
                3.4023020267486572,  2.454601526260376,   1.7791508436203003,  1.5786277055740356, 
                1.4153118133544922,  1.2250137329101562,  1.0269666910171509,  0.8788142800331116, 
                0.7694535255432129,  0.6727534532546997,  0.6191786527633667,  0.6121304631233215])
   
        self.assertEqual([mod_reg.getLongitude()[0],mod_reg.getLongitude()[-1]],[1.25, 358.75])  
        # Regrid model to obs grid using 'conservative'
        mod_reg = mod.regrid(obs_grid, regridTool='esmf', regridMethod='conservative',
                             periodicity=1)

        self.assertEqual([mod_reg.getLongitude()[0],mod_reg.getLongitude()[-1]], [1.25, 358.75]) 
        self.assertEqual(mod_reg[0,:,-1].tolist(),
            [0.17758481204509735, 0.17194212973117828, 0.19889207184314728, 0.21295012533664703, 
             0.2486753761768341,  0.28324195742607117, 0.6944049596786499,  1.3283072710037231, 
             1.505228877067566,   1.5689724683761597,  1.688291072845459,   1.886228084564209, 
             2.131767749786377,   2.453376054763794,   2.815683126449585,   3.285163640975952, 
             3.6825342178344727,  3.813880205154419,   3.816941976547241,   3.5387678146362305, 
             2.9939534664154053,  2.4087331295013428,  1.8745570182800293,  1.3876465559005737, 
             0.9089673161506653,  0.6322836875915527,  0.49888309836387634, 0.4027368426322937, 
             0.36167609691619873, 0.35790666937828064, 0.3146344721317291,  0.23865386843681335, 
             0.29177573323249817, 0.6238294243812561,  1.5048209428787231,  2.7824716567993164, 
             4.394487380981445,   5.745364665985107,   4.552212238311768,   4.643233776092529, 
             4.387013912200928,   3.174139976501465,   1.7406494617462158,  0.8630349040031433, 
             0.5483991503715515,  0.40030503273010254, 0.311230331659317,   0.32339751720428467, 
             0.661510705947876,   1.6944501399993896,  2.08923602104187,    1.6634186506271362, 
             2.4267399311065674,  3.4352316856384277,  3.219423770904541,   2.689303398132324, 
             2.6867551803588867,  2.684333086013794,   2.5946686267852783,  2.9540343284606934, 
             3.430427074432373,   2.471134662628174,   1.810300588607788,   1.5775492191314697, 
             1.4183881282806396,  1.225182294845581,   1.0341688394546509,  0.8872455954551697, 
             0.7730062007904053,  0.6754071116447449,  0.6200597286224365,  0.6105775833129883])


if __name__ == "__main__":
    basetest.run()
