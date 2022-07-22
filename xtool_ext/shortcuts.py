import logging
from xtool.entry import XToolEntry
from xtool.ext import XToolExtension
from fuzzywuzzy.fuzz import ratio
import os
from win32com.client import Dispatch
from xtool.interface import XToolDBMockInterface, XToolManageInterface

class XToolShortcuts(XToolExtension):
    @classmethod
    def initCls(cls):
        
        super().initCls()

        # initialize dispatch shell
        cls.dispatchShell = Dispatch("WScript.Shell")
        
    def __init__(self, parent: XToolManageInterface) -> None:
        super().__init__(parent)

        parent : XToolDBMockInterface = self._parent
        
        # get shortcuts folder
        self.shortcutsFolder = os.path.join(os.path.dirname(parent._targetPath), "shortcuts")

        # create shortcuts folder if it doesn't exist
        os.makedirs(self.shortcutsFolder, exist_ok=True)

    
    def _resolve_an_executable(self):
        """
        This function will try to resolve an executable file in the current folder.

        the function uses fuzzywuzzy to find the best match.
        
        current specification will ignore any case that is < 80 and will return when there is a 99% match.

        Returns:
            str: the path to the executable file, or None if no executable file was found.
        """

        potentiallyExecutable = (
            lambda name : "." not in name or any(name.endswith(ext) for ext in [".py", ".bat", ".exe", ".sh"])
        )

        closeScore = 0
        bestName = None
        allFiles =self.extensionContext.mfd.allFiles
        for name in allFiles:
            # get filename strip extension
            nameNoExt = os.path.splitext(name)[0]
            score = ratio(nameNoExt, self.extensionContext.mfd.pkgName)
            if score < 80:
                continue

            if (
                potentiallyExecutable(name)
                and (bestName is None or not potentiallyExecutable(bestName)) 
                and score >= closeScore
            ):
                closeScore = score
                bestName = name

            if closeScore >= 99:
                break

        return bestName

    def parseSource(self, source: str) -> None:
        ctx = self.extensionContext
        if ctx.config.get("shortcuts", None) is None:
            ctx.config["shortcuts"] = {}
    
        # will add a package named key to the shortcuts
        if len(ctx.config["shortcuts"]) == 0 or ctx.mfd.pkgName not in ctx.config["shortcuts"]:
            aPossibleExe = self._resolve_an_executable()
            if aPossibleExe is not None:
                ctx.config["shortcuts"][ctx.mfd.pkgName] = aPossibleExe

    def _createShortcut(self, name: str, file : str) -> None:
        """
        Creates a shortcut in the shortcuts folder.

        Args:
            name (str): the name of the shortcut
            file (str): the path to the file to create the shortcut for
        """
        shortcut = self.dispatchShell.CreateShortCut(os.path.join(self.shortcutsFolder, name + ".lnk"))
        shortcut.TargetPath = file
        shortcut.save()
        
    def installPackage(self, package: str) -> None:
        pkgObj : XToolEntry = self.extensionContext.pkgObj

        if pkgObj.config.get("shortcuts", None) is None:
            logging.error(f"{pkgObj.pkgname} has no shortcuts")
            return

        for name, file in pkgObj.config["shortcuts"].items():
            self._createShortcut(name, os.path.join(self._parent._targetPath, package, file))