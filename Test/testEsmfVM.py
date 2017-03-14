"""
$Id: testEsmfVM.py 2354 2012-07-11 15:28:14Z pletzer $

Unit MPI

"""

import ESMF
from mpi4py import MPI
import unittest

class Test(unittest.TestCase):
    def setUp(self):
        pass

    def test1(self):
        comm = MPI.COMM_WORLD
        pe1 = comm.Get_rank()
        nprocs1 = comm.Get_size()
        pe2 = ESMF.local_pet()
        nprocs2 = ESMF.pet_count()
        print "Hello ESMPy World from PET (processor) {0}!".format(ESMF.local_pet())
        self.assertEqual(pe1, pe2)
        self.assertEqual(nprocs1, nprocs2)
        
        
if __name__ == '__main__':
    ESMF.Manager()
    print ""
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity = 1).run(suite)


