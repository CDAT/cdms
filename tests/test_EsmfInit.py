#!/usr/bin/env python

import ESMF
import unittest

class Test(unittest.TestCase):
    def setUp(self):
        pass

    def test1_pairedInitializeFinalize(self):
        ESMF.Manager()

    def test2_multipleInitializeFinalize(self):
        ESMF.Manager()
        ESMF.Manager()


if __name__ == '__main__': 
    print "" # Spacer
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity = 1).run(suite)
    




    
