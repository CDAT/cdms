import sys

import unittest

def revert_modules(func):
    def wrapper():
        before = set(sys.modules)

        func()

        after = set(sys.modules)

        for x in after-before:
            del sys.modules[x]

    return wrapper

class TestMPI(unittest.TestCase):
    # @revert_modules
    def test_default_mpi(self):
        from cdms2 import dataset

        assert hasattr(dataset, "MPI")

    # @revert_modules
    def test_disable_mpi(self):
        import os
        os.environ["CDMS_NO_MPI"] = "true"

        from cdms2 import dataset

        assert not hasattr(dataset, "MPI")
