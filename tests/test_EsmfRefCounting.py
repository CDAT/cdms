import ESMF
import numpy
import unittest

# global, keeps track of the number of times the Ctor was called
INIT_REF_COUNT = 0


class Foo:
    """
    Test class to check that reference counting of ESMP.ESMP_Initialize/
    ESMP.ESMP_Finalize is working
    """

    def __init__(self):
        global INIT_REF_COUNT
        if INIT_REF_COUNT == 0:
<<<<<<< HEAD
            print('calling ESMP.ESMP_Initialize()...')
=======
            print 'calling ESMP.ESMP_Initialize()...'
>>>>>>> master
            ESMF.Manager()
        INIT_REF_COUNT += 1

    def __del__(self):
        global INIT_REF_COUNT
        INIT_REF_COUNT -= 1
        if INIT_REF_COUNT == 0:
<<<<<<< HEAD
            print('now finalizing...')
=======
            print 'now finalizing...'
>>>>>>> master


class Test(unittest.TestCase):
    def setUp(self):
        pass

    def test_test1(self):
        f1 = Foo()
        grid = ESMF.Grid(numpy.array([3, 4], dtype=numpy.int32))
#        grid = ESMP.ESMP_GridCreateNoPeriDim(numpy.array([3, 4], dtype=numpy.int32))
        f2 = Foo()
        del f1
        f1 = Foo()

    def test_test2(self):
        ESMF.Manager()
        g = ESMF.Grid(numpy.array([3, 4], dtype=numpy.int32))
#        g = ESMP.ESMP_GridCreateNoPeriDim(numpy.array([3, 4], dtype=numpy.int32))


if __name__ == '__main__':
<<<<<<< HEAD
    print("")  # Spacer
=======
    print ""  # Spacer
>>>>>>> master
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=1).run(suite)
