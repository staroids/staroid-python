import unittest
import tempfile

from staroid import Commit

class TestCommit(unittest.TestCase):
    def test_commit(self):
        test_data = [
            ["GITHUB/staroid/app:master#commit1", ["GITHUB", "staroid", "app", "master", "commit1", "false"]],
	        ["GITHUB/staroid/app:master", ["GITHUB", "staroid", "app", "master", "", "false"]],
	        ["GITHUB/staroid/app", ["", "", "", "", "", "true"]],
	        ["GITHUB/staroid/app:", ["", "", "", "", "", "true"]],
	        ["GITHUB/staroid:master", ["", "", "", "", "", "true"]]
        ]

        for data in test_data:
            
            try:
                c = Commit(data[0])
                self.assertEqual(data[1][0], c.provider())
                self.assertEqual(data[1][1], c.owner())
                self.assertEqual(data[1][2], c.repo())
                self.assertEqual(data[1][3], c.branch())
                self.assertEqual(data[1][4], c.commit())
            except:
                self.assertEqual(data[1][5], "true")
