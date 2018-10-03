from __future__ import print_function
import unittest
import os
from subprocess import Popen, PIPE
import shlex
import MV2, cdms2
import cdat_info


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


    def testCloneUnits(self):

        f= cdms2.open(cdat_info.get_sampledata_path()+"/clt.nc")
        s = f("clt", **{})
        #s.info()

        s = s(
            latitude=(
                20, 20, "cob"), longitude=(
                112, 112, "cob"), squeeze=1)
        s2 = MV2.sin(s)

        ax = s2.getTime()
        ax2 = ax.clone()
        ax2[0]=4
        ax2.toRelativeTime("days since 30000")
        self.assertNotEqual(ax[0], ax2[0])
        self.assertNotEqual(ax.__dict__['_data_'].ctypes.data, ax2.__dict__['_data_'].ctypes.data)


