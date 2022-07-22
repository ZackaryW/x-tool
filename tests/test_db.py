import shutil
import unittest
from xtool import XToolDB,XToolExtension
import os
from xtool.ctx import XToolContext

from xtool_ext.shortcuts import XToolShortcuts 

class TestXToolDB(XToolDB):
    def test(self, key : str):
        xlist = [1,2,3]
        self._callExtensions(**{k: v for k, v in locals().items() if k != "self"})
        return xlist

    def test1(self, key : str):
        self._callExtensions(**{k: v for k, v in locals().items() if k != "self"})
        return 1

class TestXToolExtension(XToolExtension):
    def test(self, key : str):
        print(key)
        ctx = self.extensionContext
        ctx.xlist.append(4)
        self.globalContext.xxx = "yyy"
        pass

class t_db_init(unittest.TestCase):
    def test_db_init(self):
        db = TestXToolDB("./tests/deploy/",)
        db._addExtension(TestXToolExtension)
        xlist = db.test("test")
        self.assertEqual(xlist, [1,2,3,4])
        self.assertEqual(db.globalContext.xxx, "yyy")

        # 
        db.test1("test1")
        self.assertIsInstance(db.extensions[TestXToolExtension(db)], XToolContext)


class t_db(unittest.TestCase):
    def setUp(self) -> None:
        shutil.rmtree("./tests/deploy/", ignore_errors=True)
        os.makedirs("./tests/deploy/", exist_ok=True)
        self.db = XToolDB("./tests/deploy/", debug=True)
        self.db._addExtension(XToolShortcuts)
        self.db._createAllTables()

    def test_parseSource(self):
        self.db.parseSource("./tests/source/trid")

    def test_Package_Operations(self):
        self.test_parseSource()
        self.db.installPackage("trid")

        pass