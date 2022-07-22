import sqlalchemy
import os
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from xtool.ctx import XToolContext
from xtool.interface import XToolManageInterface
from xtool.entry import XToolEntry
from xtool.utils.folderInterface import FolderMFD, ZipMFD, createMFD, FileDeliveryInterface
from xtool.ext import XToolExtension
import inspect
import shutil
import contextlib

from xtool.utils.misc import callExtensions

class XToolDB(XToolManageInterface):
    def __init__(self, folderpath : str, sourceFolder : str = None, debug : bool = False) -> None:
        """
        this is the xtool manager that also wraps over the sqlalchemy engine

        NOTE: make sure folderPath is a valid path
        NOTE: in order for all the tables to be created, you must call _createAllTables()
        """

        if not os.path.isdir(folderpath):
            raise Exception("Folderpath is not a directory")

        if not os.path.exists(folderpath):
            os.makedirs(folderpath, exist_ok=True)

        self.engine = sqlalchemy.create_engine(f'sqlite:///{folderpath}/xtool.db', echo=debug)
        self._base = declarative_base(self.engine)

        # parse source path
        if sourceFolder is None:
            self._sourcePath = os.path.join(folderpath, "source")
            os.makedirs(self._sourcePath, exist_ok=True)
        elif not os.path.exists(sourceFolder):
            raise Exception("Source folder does not exist")
        else:
            self._sourcePath = sourceFolder

        self._sourcePath = os.path.abspath(self._sourcePath)
        
        self._targetPath = os.path.join(folderpath, "target")
        if not os.path.exists(self._targetPath):
            os.makedirs(self._targetPath, exist_ok=True)

        self._targetPath = os.path.abspath(self._targetPath)
        self._sourcePath = os.path.abspath(self._sourcePath)

        self.XToolEntry : XToolEntry = self._createTable(XToolEntry)

        self.extensions = {}
        self.globalContext = XToolContext()
        
    @contextlib.contextmanager
    def makeSession(self,
        commit : bool = False,
        expunge : bool = True,
    ) -> None:
        """
        this is a context manager that creates a session and commits/expunges it

        Args:
            commit (bool, optional): commit the session. Defaults to False.
            expunge (bool, optional): expunge the session. Defaults to True.

        Yields:
            Session: the session
        """

        session : Session = sessionmaker(bind=self.engine)()
        try:
            yield session
            if commit:
                session.commit()
        finally:
            if expunge:
                session.expunge_all()
            
            session.close()

    def _addExtension(self, extension : type) -> None:
        """
        add an extension to the manager

        this should be the only way to append extensions to the manager

        Args:
            extension (type): the extension class to add

        """

        if not issubclass(extension, XToolExtension) or extension is XToolExtension:
            raise Exception("Extension is not a subclass of XToolExtension")

        ext = extension(self)

        self.extensions[ext] = XToolContext()

    def _createAllTables(self) -> None:
        """
        create all the tables (sqlalchemy.engine)
        """

        self._base.metadata.create_all(self.engine)

    def _createTable(self, table : type, tablename : str = None) -> None:
        """
        dynamically creates a table based on a dataclass that init with sqlalchemy columns

        Args:
            table (type): the dataclass to create a table from
            tablename (str, optional): the name of the table. Defaults to None.

        Returns:
            type: the table class
        """

        if tablename is None:
            tablename = table.__name__

        new_type = type(table.__name__, (table, self._base,), {"__tablename__": tablename})
        return new_type

    @property
    def sourcePath(self) -> str:
        """
        get the source path

        Returns:
            str: the source path
        """

        return self._sourcePath
    
    @property
    def targetPath(self) -> str:
        return self._targetPath
    
    def parseSource(self, source : str) -> None:
        """
        this methods parses a not available package and adds it to the database

        Args:
            source (str): the source path to the package

        """

        if not os.path.exists(source):
            raise Exception("Source file does not exist")

        if not os.path.isdir(source):
            raise Exception("Source is not a directory")

        source = os.path.abspath(source)

        mfd : FileDeliveryInterface = createMFD(source)

        # checks if the package and the source are both ready and valid
        with self.makeSession() as session:
            session : Session
            existingPackage : XToolEntry = session.query(self.XToolEntry).filter(self.XToolEntry.pkgname == mfd.pkgName).first()
            if (
                existingPackage is not None 
                and existingPackage.isAvailable 
                and os.path.exists(os.path.join(self._targetPath, existingPackage.pkgname))
            ):
                return

        if mfd is None:
            raise Exception("Could not create MFD")

        # if source is in sourcepath
        if not source.startswith(self._sourcePath) and isinstance(mfd, FolderMFD):
            mfd = mfd.pack(os.path.join(self._sourcePath, mfd.pkgName))
        elif not source.startswith(self._sourcePath) and isinstance(mfd, ZipMFD):
            mfd = mfd.copyTo(os.path.join(self._sourcePath, mfd.pkgName))
        
        # parse config
        config = {}
        try:
            config = mfd.readJsonFile("xtool.json")
        except:
            pass

        # call extensions
        callExtensions(**locals())

        # creates the xtoolentry object
        pkgObj : XToolEntry = self.XToolEntry(
            pkgname = mfd.pkgName,
            config=config,
            isAvailable=True,
            isInstalled=False,
            filesList = mfd.allFiles,
        )        

        # add to database
        with self.makeSession() as session:
            session : Session
            session.merge(pkgObj)
            session.commit()


    def installPackage(self, package: str) -> None:
        # get package
        with self.makeSession() as session:
            pkgObj : XToolEntry = session.query(self.XToolEntry).filter(self.XToolEntry.pkgname == package).first()
        
        if pkgObj is None:
            raise Exception("Package does not exist")

        if pkgObj.isInstalled:
            raise Exception("Package is already installed")

        if pkgObj.isAvailable is False:
            raise Exception("Package is not available")

        sourceMfd : FileDeliveryInterface = createMFD(os.path.join(self._sourcePath, package))

        if sourceMfd is None:
            raise Exception("Could not create MFD")

        # copy source files to target
        sourceMfd.copyTo(os.path.join(self._targetPath, package))

        callExtensions(**locals())

        # set package as installed
        with self.makeSession() as session:
            session : Session
            pkgObj.isInstalled = True
            session.merge(pkgObj)
            session.commit()
        
    def purgeAll(self):
        # remove everything in the db
        with self.makeSession() as session:
            session : Session
            session.query(self.XToolEntry).delete()
            session.commit()

        # remove target folder
        shutil.rmtree(self._targetPath, ignore_errors=True)

        callExtensions(**locals())


        
