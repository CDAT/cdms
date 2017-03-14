import urllib
import cdms2
import os
import sys
import cdat_info
import basetest
import numpy as np
import basetest
import ssl

modFile="model_ANN_climo.nc"
obsFile="GPCP_ANN_climo.nc"
class TestRegrid(basetest.CDMSBaseTest):
    def setUp(self):
        super(TestRegrid, self).setUp()
        context = ssl._create_unverified_context()
        myurl = "http://uvcdat.llnl.gov/cdat/sample_data/"+obsFile
        urllib.urlretrieve(myurl, obsFile, context=context)
        myurl = "http://uvcdat.llnl.gov/cdat/sample_data/"+modFile
        urllib.urlretrieve(myurl, modFile, context=context)

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
        mod_reg = mod.regrid(obs_grid, regridTool='esmf', regridMethod='linear', periodicity=1, ignoreDegenerate=True)
#        self.assertEqual(np.array_str(mod_reg[-1,-1,:], precision=2), '[ 0.61  0.61  0.61  0.62  0.62  0.62  0.62  0.62  0.62  0.62  0.62  0.62\n  0.62  0.62  0.63  0.63  0.63  0.63  0.63  0.63  0.63  0.63  0.64  0.64\n  0.64  0.64  0.64  0.64  0.64  0.64  0.64  0.64  0.65  0.65  0.65  0.65\n  0.65  0.65  0.65  0.65  0.65  0.64  0.64  0.64  0.64  0.64  0.64  0.64\n  0.64  0.64  0.64  0.64  0.64  0.63  0.63  0.63  0.63  0.63  0.63  0.64\n  0.64  0.64  0.64  0.64  0.64  0.64  0.64  0.63  0.63  0.63  0.63  0.63\n  0.63  0.63  0.63  0.62  0.62  0.62  0.62  0.62  0.61  0.61  0.61  0.61\n  0.61  0.61  0.61  0.61  0.61  0.61  0.61  0.61  0.61  0.61  0.6   0.6\n  0.6   0.6   0.6   0.6   0.6   0.6   0.6   0.6   0.6   0.59  0.59  0.59\n  0.59  0.59  0.59  0.59  0.59  0.58  0.58  0.58  0.58  0.58  0.58  0.58\n  0.59  0.59  0.59  0.59  0.59  0.59  0.59  0.59  0.59  0.59  0.59  0.59\n  0.59  0.59  0.59  0.59  0.59  0.59  0.59  0.6    0.6  0.61  0.61  0.41]')
#        self.assertEqual(np.array_str(mod_reg[0,0,:], precision=2), '[ 0.19  0.19  0.18  0.17  0.18  0.18  0.17  0.17  0.16  0.18  0.17  0.17\n  0.17  0.18  0.17  0.17  0.17  0.17  0.18  0.17  0.17  0.16  0.17  0.17\n  0.17  0.16  0.16  0.17  0.17  0.16  0.16  0.18  0.18  0.18  0.18  0.17\n  0.19  0.18  0.18  0.18  0.19  0.19  0.19  0.19  0.19  0.2   0.2   0.2\n  0.2   0.21  0.21  0.21  0.21  0.21  0.22  0.22  0.22  0.22  0.22  0.23\n  0.23  0.23  0.23  0.24  0.24  0.24  0.24  0.25  0.26  0.29  0.3   0.3\n  0.28  0.29  0.3   0.35  0.32  0.33  0.35  0.36  0.37  0.33  0.34  0.34\n  0.35  0.32  0.32  0.32  0.31  0.3   0.29  0.3   0.31  0.32  0.31  0.32\n  0.33  0.34  0.35  0.31  0.32  0.33  0.34  0.3   0.3   0.29  0.29  0.3\n  0.28  0.28  0.29  0.28  0.26  0.26  0.26  0.26  0.25  0.25  0.25  0.24\n  0.24  0.24  0.23  0.23  0.23  0.22  0.22  0.22  0.21  0.21  0.21  0.21\n  0.21  0.21  0.21  0.2   0.2   0.2   0.2   0.2   0.19  0.19  0.18  0.18]')
   
        self.assertEqual([mod_reg.getLongitude()[0],mod_reg.getLongitude()[-1]],[1.25, 358.75])  
        # Regrid model to obs grid using 'conservative'
        mod_reg = mod.regrid(obs_grid, regridTool='esmf', regridMethod='conservative',
                             periodicity=1)

#        self.assertEqual(np.array_str(mod_reg[0,0,:], precision=2),'[ 0.18  0.18  0.17  0.16  0.16  0.16  0.16  0.16  0.16  0.16  0.16  0.16\n  0.15  0.15  0.15  0.15  0.15  0.16  0.16  0.15  0.15  0.15  0.15  0.15\n  0.15  0.15  0.15  0.15  0.14  0.14  0.15  0.15  0.15  0.16  0.16  0.16\n  0.16  0.16  0.16  0.17  0.17  0.17  0.18  0.18  0.18  0.18  0.18  0.18\n  0.19  0.19  0.19  0.19  0.2   0.2   0.2   0.21  0.21  0.21  0.22  0.22\n  0.23  0.24  0.24  0.25  0.25  0.26  0.26  0.27  0.28  0.31  0.36  0.37\n  0.37  0.38  0.43  0.47  0.48  0.48  0.47  0.46  0.45  0.45  0.44  0.45\n  0.45  0.45  0.45  0.44  0.43  0.43  0.43  0.43  0.43  0.43  0.43  0.43\n  0.42  0.39  0.38  0.38  0.39  0.39  0.39  0.39  0.38  0.35  0.32  0.31\n  0.31  0.31  0.3   0.29  0.28  0.28  0.27  0.27  0.27  0.27  0.26  0.26\n  0.25  0.25  0.25  0.24  0.24  0.23  0.23  0.22  0.22  0.22  0.22  0.21\n  0.21  0.2   0.2   0.2   0.2   0.2   0.2   0.19  0.19  0.18  0.18  0.18]')
#        self.assertEqual(np.array_str(mod_reg[-1,-1,:], precision=2), '[ 0.61  0.61  0.61  0.62  0.62  0.62  0.62  0.62  0.62  0.62  0.62  0.63\n  0.63  0.63  0.63  0.63  0.63  0.63  0.63  0.64  0.64  0.64  0.64  0.64\n  0.65  0.65  0.65  0.65  0.65  0.65  0.65  0.65  0.66  0.66  0.66  0.66\n  0.66  0.66  0.66  0.65  0.65  0.65  0.65  0.65  0.65  0.65  0.65  0.65\n  0.65  0.65  0.64  0.64  0.64  0.64  0.64  0.64  0.64  0.64  0.64  0.64\n  0.64  0.64  0.64  0.64  0.64  0.64  0.64  0.64  0.64  0.63  0.63  0.63\n  0.63  0.63  0.63  0.62  0.62  0.62  0.62  0.62  0.62  0.62  0.62  0.61\n  0.61  0.61  0.61  0.61  0.61  0.61  0.61  0.61  0.6   0.6   0.6   0.6\n  0.6   0.6   0.6   0.6   0.6   0.6   0.6   0.59  0.59  0.59  0.59  0.59\n  0.59  0.59  0.59  0.58  0.58  0.58  0.58  0.58  0.58  0.58  0.58  0.58\n  0.58  0.58  0.58  0.58  0.58  0.58  0.58  0.58  0.58  0.58  0.58  0.58\n  0.59  0.59  0.59  0.59  0.59  0.59  0.59  0.59  0.6   0.6   0.61  0.61]')

        self.assertEqual([mod_reg.getLongitude()[0],mod_reg.getLongitude()[-1]], [1.25, 358.75]) 


if __name__ == "__main__":
    basetest.run()
#
