import os
import contextlib

import unittest
from unittest.mock import patch

from cdms2 import util
from cdms2 import CDMSError

class TestUtil(unittest.TestCase):
    def test_getenv_bool(self):
        with self.assertRaises(CDMSError):
            util.getenv_bool("TEST")

        tests = {
            "true": True,
            "True": True,
            "false": False,
            "False": False
        }

        for x, y in tests.items():
            with patch.dict(os.environ, {"TEST": x}):
                value = util.getenv_bool("TEST")

                assert value == y

        assert util.getenv_bool("NOEXIST", "false") == False

    def test_getenv_bool_invalid(self):
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, {"TEST": "1"}))
            stack.enter_context(self.assertRaises(CDMSError))

            util.getenv_bool("TEST")
