from pprint import pformat
import sqlalchemy

class XToolEntry:
    """
    this is a class that represents a package in the database

    (this class is not sqlalchemy-based)
    """

    pkgname = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    config = sqlalchemy.Column(sqlalchemy.JSON, default=dict)
    isAvailable = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    isInstalled = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    filesList = sqlalchemy.Column(sqlalchemy.JSON, default=list)

    def __str__(self) -> str:
        return self.pkgname

    def __repr__(self) -> str:
        return f"{self.pkgname}\n{pformat(self.config)}\n{pformat(self.filesList)}"