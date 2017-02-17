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
        urllib.urlretrieve(myurl, obsFile)
        myurl = "http://uvcdat.llnl.gov/cdat/sample_data/"+modFile
        urllib.urlretrieve(myurl, modFile)

    def tearDown(self):
        super(TestRegrid, self).tearDown()
        os.remove(obsFile)
        os.remove(modFile)

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
        self.assertEqual(np.array_str(mod_reg, precision=2),'[[[ 0.19  0.19  0.18 ...,  0.19  0.18  0.18]\n  [ 0.17  0.16  0.14 ...,  0.2   0.18  0.17]\n  [ 0.19  0.16  0.16 ...,  0.23  0.22  0.19]\n  ..., \n  [ 0.67  0.67  0.67 ...,  0.66  0.66  0.67]\n  [ 0.62  0.63  0.63 ...,  0.6   0.61  0.62]\n  [ 0.61  0.61  0.61 ...,  0.61  0.61  0.61]]]')
   
        self.assertEqual([mod_reg.getLongitude()[0],mod_reg.getLongitude()[-1]],[1.25, 358.75])  
        # Regrid model to obs grid using 'conservative'
        mod_reg = mod.regrid(obs_grid, regridTool='esmf', regridMethod='conservative',
                             periodicity=1)

        self.assertEqual([mod_reg.getLongitude()[0],mod_reg.getLongitude()[-1]], [1.25, 358.75]) 
        self.assertEqual(np.array_str(mod_reg, precision=2),'[[[ 0.18  0.18  0.17 ...,  0.18  0.18  0.18]\n  [ 0.17  0.16  0.14 ...,  0.2   0.19  0.17]\n  [ 0.19  0.16  0.16 ...,  0.23  0.22  0.2 ]\n  ..., \n  [ 0.68  0.68  0.68 ...,  0.67  0.67  0.68]\n  [ 0.62  0.63  0.64 ...,  0.6   0.61  0.62]\n  [ 0.61  0.61  0.61 ...,  0.6   0.61  0.61]]]')

if __name__ == "__main__":
    basetest.run()
#
