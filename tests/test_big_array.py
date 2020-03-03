import os
import unittest
import cdat_info
import cdms2
import numpy as np
import sys
from testsrunner import Util
from nose.plugins.attrib import attr

class TestBigData(unittest.TestCase):

    def setUp(self):
        workdir = os.environ.get("WORKDIR")
        if workdir is None:
            prefix = sys.prefix
        else:
            prefix = os.path.join(workdir, "cdms")
        md5_files = os.path.join(prefix, "share/test_big_data_files.txt")
        test_file = "so_Omon_CESM2_historical_r1i1p1f1_gn_185001-201412.nc"
        path = Util.get_sampledata_path()
        Util.download_sample_data_files(md5_files, path)

        self.f = cdms2.open(os.path.join(path, test_file))

    def _get_var_info_for_time_frame(self, start, end):
        print("times: {start} - {end}".format(start=start,
                                              end=end))
        var = self.f('so', time=(str(start),str(end)))
        print("var size: %d Mb" % ( (var.size * var.itemsize) / (1024*1024) ) )
        min_val = var.min()
        max_val = var.max()
        mean_val = np.ma.mean(var.data)

        print('var.min():'.ljust(21), min_val)
        print('var.max():'.ljust(21), max_val)
        print('np.ma.mean(var.data):', mean_val)
        self.assertIsNot(min_val, 0)
        self.assertIsNot(max_val, 0)
        self.assertIsNot(mean_val, 0)

    @attr("big_data")
    def test_read_large_slice(self):
        start = 1990
        end = 2014
        self._get_var_info_for_time_frame(start, end)

        start = 1989
        self._get_var_info_for_time_frame(start, end)

