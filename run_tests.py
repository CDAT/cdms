import unittest
import glob
import importlib
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Test"))
if len(sys.argv)==1:
    tests = glob.glob("Test/test_*.py")
    names = [t[5:-3] for t in tests]
    names.remove("test_cdscan")
    names.insert(0,"test_cdscan")
else:
    names = sys.argv[1:]

suite = unittest.defaultTestLoader.loadTestsFromNames(names)
runner = unittest.TextTestRunner(verbosity=2).run(suite)


if runner.wasSuccessful():
    sys.exit()
else:
    sys.exit(1)
