from __future__ import print_function
import unittest
import os
from subprocess import Popen, PIPE
import shlex


class TestFlake8(unittest.TestCase):

    def testFlake8(self):
        pth = os.path.dirname(__file__)
        pth = os.path.join(pth, "..")
        pth = os.path.abspath(pth)
        # pth = os.path.join(pth, "Lib regrid2/Lib")
        pth = os.path.join(pth, "Lib")
        print()
        print()
        print()
        print()
        print("---------------------------------------------------")
        print("RUNNING: flake8 on directory %s" % pth)
        print("---------------------------------------------------")
        print()
        print()
        print()
        print()
        print(pth)
        P = Popen(shlex.split("flake8 --show-source --statistics --ignore=F999,F405,E121,E123,E126,E226,E24,E704 --max-line-length=120 %s" % pth),
                             stdin=PIPE,
                             stdout=PIPE,
                             stderr=PIPE, close_fds=True)
        out, errs = P.communicate()
        out=out.decode('utf8')
        if out != "":
            print(out)
        self.assertEqual(out, "")
