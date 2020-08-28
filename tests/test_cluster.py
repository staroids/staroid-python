import unittest
import tempfile
import os

from staroid import Staroid

def integration_test_ready():
    return "STAROID_ACCESS_TOKEN" in os.environ and "STAROID_ACCOUNT" in os.environ

class TestCluster(unittest.TestCase):
    @unittest.skipUnless(integration_test_ready(), "Integration test environment is not configured")
    def test_initialize(self):
        s = Staroid(access_token=os.environ["STAROID_ACCESS_TOKEN"], account=os.environ["STAROID_ACCOUNT"])
        s.get_all_accounts()

    @unittest.skipUnless(integration_test_ready(), "Integration test environment is not configured")
    def test_crud(self):
        # given
        s = Staroid(access_token=os.environ["STAROID_ACCESS_TOKEN"], account=os.environ["STAROID_ACCOUNT"])
        all_accounts = s.get_all_accounts()
        clusters_before = s.cluster().get_all()

        # when create
        c = s.cluster().create("staroid-python it-test")

        # then
        self.assertEqual("staroid-python it-test", c.name())

        # when already exists on create
        c = s.cluster().create("staroid-python it-test")

        # then
        self.assertEqual("staroid-python it-test", c.name())

        # when list
        clusters_after = s.cluster().get_all()

        # then
        self.assertEqual(len(clusters_after), len(clusters_before) + 1)

        # when delete
        s.cluster().delete("staroid-python it-test")

        # then
        clusters_after_deleted = s.cluster().get_all()
        self.assertEqual(len(clusters_after_deleted), len(clusters_before))

