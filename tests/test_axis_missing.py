import unittest
import numpy
import cdms2
import MV2

class CDMSTestAxisMissing(unittest.TestCase):
    def testAxismissing(self):
        data = """
        -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999.
        0.059503571833625334
        0.059503571833625334 0.05664014775641405 0.05193557222118004
        0.04777129850801233 0.0407139313814465 0.029382624830271705
        0.018469399844287374 0.0162382275289592 0.02646680241827459
        0.04792041732949079 0.0689138797030203 0.08167038620212037
        0.09273558459066569 0.11266293431057901 0.13663018925347364
        0.15229174546388072 0.15284435880966177 0.13423845476113883
        0.09945904378274077 0.07032267160267985 0.05551039827020481
        0.045537187647785464 0.040532491867244946 0.03577527125478327
        -999. -999. -999.
        -0.058062458673116 -0.08764922509099882 -0.11697036914487152
        -0.14836133615864944 -0.17956528904564023 -0.21109198032585794
        -0.23846429237248942 -0.2598536549218765 -0.27795672866320387
        -0.2939939095159731 -0.30541031366330024 -0.307643559333884
        -0.30078421139811795 -0.2841339526883441 -0.26485737397202497
        -0.24287299694779327 -0.22379014890999907 -0.20121548204699846
        -0.1746486732156772 -0.14585019344118372 -0.12070675757803526
        -0.0997891159111037 -0.08229393660994214 -0.06779720501287469
        -0.057213385470859794 -0.04875768191096844 -0.0402377347189964
        -0.030169328367807245 -0.017560662894847895 -0.006968922654137132
        0.0009773980274431048 0.007054306637034288 0.010472286514133042
        0.010702384151997032 0.009231553701801242 0.007544033101056543
        0.004639797857203645 -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999.
        -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999. -999.
        -999. -999. -999.
        """.split()
        data = numpy.array(data, dtype=numpy.float)
        data = MV2.masked_less(data, -900)
        d2 = cdms2.createAxis(data)
        self.assertTrue(numpy.ma.allclose(data.data,d2[:]))
        d2 = cdms2.createAxis(data,copy=1)
        self.assertTrue(numpy.ma.allclose(data.filled(),d2[:]))
