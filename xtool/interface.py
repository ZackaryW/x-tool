from abc import abstractmethod
import sqlalchemy
from xtool.ctx import XToolContext
from xtool.exception import XToolNotImplementedException
from xtool.entry import XToolEntry
class XToolManageInterface:
    """
    this interface defines the intent for each method

    shared between XToolExtension and XToolDB
    """

    @abstractmethod
    def parseSource(self, source : str) -> None:
        """
        parse the source folder and create database entry (package)
        """
        raise XToolNotImplementedException("parseSource")

    @abstractmethod
    def installPackage(self, package : str) -> None:
        """
        install a package based on information provided in database
        """

        raise XToolNotImplementedException("installPackage")

    @abstractmethod
    def verifyPackage(self, package : str) -> None:
        """
        verify if a package is consistent to information provided in database
        """

        raise XToolNotImplementedException("verifyPackage")

    @abstractmethod
    def uninstallPackage(self, package : str) -> None:
        """
        uninstall a package
        """

        raise XToolNotImplementedException("uninstallPackage")


    @abstractmethod
    def exportPackage(self, package : str, target : str) -> None:
        """
        export a package to a target folder
        """

        raise XToolNotImplementedException("exportPackage")

    @abstractmethod
    def backupPackageUsrData(self, package : str, target : str) -> None:
        """
        backup user data of a package to a target folder
        """

        raise XToolNotImplementedException("backupPackageUsrData")

    @abstractmethod
    def purgeAll(self):
        """
        purge all data in the database
        """

        raise XToolNotImplementedException("purgeAll")

class XToolDBMockInterface(XToolManageInterface):
    """
    this is a mock interface for XToolDB
    """

    engine : sqlalchemy.engine.Engine
    _base : sqlalchemy.engine.base
    _sourcePath : str
    _targetPath : str
    XToolEntry : XToolEntry 
    extensions : dict
    globalContext : XToolContext