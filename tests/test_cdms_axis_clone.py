from __future__ import print_function
import unittest
import os
from subprocess import Popen, PIPE
import shlex
import MV2, cdms2


class TestAxis(unittest.TestCase):

    def testCloneUnits(self):

        tmp = MV2.ones(3, id='tmp')
        ax = tmp.getAxis(0)
        ax.standard_name = "time"
        ax.id = 'time'
        ax.units = "seconds since 1900-01-01T00:00:00Z"
        ax.long_name = "time in seconds (UT)"
        ax.time_origin = "01-JAN-1900 00:00:00"
        ax.designateTime()

        f = cdms2.open('tmp.nc', 'w')
        f.write(tmp)
        f.close()

        f = cdms2.open('tmp.nc') 
        assert f['time'].clone().units == f['time'].units
        f.close()
