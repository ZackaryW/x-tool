from abc import abstractmethod
import abc

from xtool.exception import XToolNotImplementedException

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