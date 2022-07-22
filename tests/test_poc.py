import unittest
from xtool.utils import getAllFiles

class t_poc(unittest.TestCase):
    def test_poc_getAllFiles_Working(self):
        allFiles = getAllFiles("tests")
        pass