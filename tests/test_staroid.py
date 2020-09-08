import unittest
import tempfile
import os
import pathlib
import shutil

from staroid import Staroid

def integration_test_ready():
    return "STAROID_ACCESS_TOKEN" in os.environ and "STAROID_ACCOUNT" in os.environ

class TestStaroid(unittest.TestCase):
    def test_initialize(self):
        s = Staroid()

    def test_read_config(self):
        # unset env
        at = None
        ac = None
        if "STAROID_ACCESS_TOKEN" in os.environ:
            at = os.environ["STAROID_ACCESS_TOKEN"]  
            del os.environ["STAROID_ACCESS_TOKEN"]  
        if "STAROID_ACCOUNT" in os.environ:
            ac = os.environ["STAROID_ACCOUNT"]
            del os.environ["STAROID_ACCOUNT"]

        # given
        fp = tempfile.NamedTemporaryFile()
        fp.write(b"access_token: abc\naccount: GITHUB/user1")
        fp.flush()

        # when
        s = Staroid(config_path=fp.name)

        # then
        self.assertEqual("abc", s.get_access_token())
        self.assertEqual("GITHUB/user1", s.get_account())

        # restore env
        if at != None:
            os.environ["STAROID_ACCESS_TOKEN"] = at
        if ac != None:
            os.environ["STAROID_ACCOUNT"] = ac

    def test_download_chisel(self):
        # given
        tmp_dir = tempfile.mkdtemp()
        s = Staroid(cache_dir=tmp_dir)

        # when
        chisel_path = s.get_chisel_path()

        # then
        self.assertIsNotNone(chisel_path)
        self.assertTrue(os.path.isfile(chisel_path))
        
        # clean up
        shutil.rmtree(pathlib.Path(tmp_dir))


    @unittest.skipUnless(integration_test_ready(), "Integration test environment is not configured")
    def test_read_default_account(self):
        # given access_token is set but account is not set
        ac = None
        if "STAROID_ACCOUNT" in os.environ:
            ac = os.environ["STAROID_ACCOUNT"]
            del os.environ["STAROID_ACCOUNT"]

        # when
        s = Staroid()

        # then
        self.assertNotEqual(None, s.get_account())

        # restore env
        if ac != None:
            os.environ["STAROID_ACCOUNT"] = ac
