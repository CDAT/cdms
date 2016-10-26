import unittest
import glob
import importlib
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Test"))
if len(sys.argv)==1:
    names = glob.glob("Test/test_*.py")
else:
    names = sys.argv[1:]

for i,nm in enumerate(names):
    nm = nm.split("/")[-1].split(".py")[0]
    names[i]=nm

if "test_cdscan" in names:
    names.remove("test_cdscan")
    names.insert(0,"test_cdscan")

suite = unittest.defaultTestLoader.loadTestsFromNames(names)
runner = unittest.TextTestRunner(verbosity=2).run(suite)


if runner.wasSuccessful():
    sys.exit()
else:
    sys.exit(1)
