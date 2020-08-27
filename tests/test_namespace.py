import unittest
import tempfile
import os, time

from staroid import Staroid

def integration_test_ready():
    return "STAROID_ACCESS_TOKEN" in os.environ and "STAROID_ACCOUNT" in os.environ

def wait_for_phase(ns_api, ns, phase):
    max_wait = 300
    while ns.phase() != phase:
        time.sleep(1)
        ns = ns_api.get_by_id(ns.id())
        max_wait -= 1
        if max_wait == 0:
            break

class TestCluster(unittest.TestCase):
    @unittest.skipUnless(integration_test_ready(), "Integration test environment is not configured")
    def test_crud_namespace(self):
        # given
        s = Staroid(access_token=os.environ["STAROID_ACCESS_TOKEN"], org=os.environ["STAROID_ACCOUNT"])
        all_orgs = s.get_all_orgs()
        c = s.cluster().create("staroid-python it-test-namespace")

        # when create a namespace
        ns_api = s.namespace(c)
        ns = ns_api.create("instance1", "GITHUB/staroids/namespace:master")

        # then namespace becomes RUNNING
        wait_for_phase(ns_api, ns, "RUNNING")
        self.assertEqual("RUNNING", ns_api.get_by_id(ns.id()).phase())

        # when stop a namespace
        ns = ns_api.delete("instance1")

        # then namespace becomes REMOVED
        wait_for_phase(ns_api, ns, "REMOVED")
        self.assertEqual("REMOVED", ns_api.get_by_id(ns.id()).phase())

        # when delete
        s.cluster().delete("staroid-python it-test-namespace")