import unittest
import tempfile

from staroid import Staroid

class TestStaroid(unittest.TestCase):
    def test_initialize(self):
        s = Staroid()

    def test_read_config(self):
        # given
        fp = tempfile.NamedTemporaryFile()
        fp.write(b"access_token: abc\ndefault_org: GITHUB/user1")
        fp.flush()

        # when
        s = Staroid(config_path=fp.name)

        # then
        self.assertEqual("abc", s.get_access_token())
        self.assertEqual("GITHUB/user1", s.get_org())
