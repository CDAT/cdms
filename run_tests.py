import unittest
import glob
import importlib
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Test"))
tests = glob.glob("Test/test_*.py")
names = [t[5:-3] for t in tests]
suite = unittest.defaultTestLoader.loadTestsFromNames(names)
runner = unittest.TextTestRunner(verbosity=2).run(suite)
