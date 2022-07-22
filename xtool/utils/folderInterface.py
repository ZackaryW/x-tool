from abc import abstractmethod, abstractproperty
from functools import cached_property
import json
import os
import typing
import zipfile
from fuzzywuzzy import process
import shutil

class FileDeliveryInterface:
    """
    this interface defines a folder or folder like structure for io operations

    it also supports hasFile_ prefixed checks
    
    for example:
        to check if x.txt is available in the folder:
        self.hasFile_x_txt


    """
    def __init__(
        self, 
        file_path : str,
        has_json_config : bool = True, 
        config_file : str = "config.json",
    ):
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise ValueError("file_path is not found")

        if not has_json_config:
            return

        try:
            self.meta = self.readJsonFile(config_file)
        except:
            self.meta = {}

    @cached_property
    def allFiles(self) -> typing.List[str]:
        """
        returns a list of all files in the medium

        Returns:
            typing.List[str]
        """

        pass

    def hasFile(self, filename : str, fuzzy : bool = True) -> bool:
        """
        checks if a file is avilable in the medium

        fuzzy matching is enabled by default

        Args:
            filename (str): the filename to check
            fuzzy (bool, optional): enable fuzzy matching. Defaults to True.

        Returns:
            bool: True if the file is available
            str: filename, None if not available
        """

        if filename in self.allFiles:
            return True, filename
        if not fuzzy:
            return False, None

        match = process.extractOne(filename, self.allFiles)
        if match is None:
            return False, None

        if  match[1] > 80 and any(match[0].endswith(ext) for ext in [".exe", ".py",".bat",".sh"]):
            return True, match[0]

        return False, None


    @abstractmethod
    def getFile(self, fileName : str):
        """
        returns a file object

        Args:
            fileName (str): the filename to get
        """

        raise NotImplementedError("getFile is not implemented")

    @abstractmethod
    def writeFile(self, fileName, data):
        """
        writes a file to the medium

        Args:
            fileName (str): the filename to write
            data (bytes): the data to write

        #TODO may need to specify byte mode
        """

        raise NotImplementedError("writeFile is not implemented")

    @abstractmethod
    def readJsonFile(self, fileName : str):
        """
        reads a json file from the medium

        Args:
            fileName (str): the filename to read

        """

        raise NotImplementedError("readJsonFile is not implemented")
    
    @abstractmethod
    def writeJsonFile(self, fileName : str, data : dict):
        """
        writes a json file to the medium

        Args:
            fileName (str): the filename to write
            data (dict): the data to write

        """

        raise NotImplementedError("writeJsonFile is not implemented")

    @abstractmethod
    def copyFile(self, fileName : str, destPath : str):
        """
        copies a file from the medium to a destination path

        Args:
            fileName (str): the filename to copy
            destPath (str): the destination path to copy to

        """
        raise NotImplementedError("copyFile is not implemented")

    @abstractmethod
    def copyTo(self, destPath : str):
        """
        copies the medium to a destination path

        Args:
            destPath (str): the destination path to copy to
        """
        raise NotImplementedError("copyTo is not implemented")

    @abstractmethod
    def zipTo(self, destPath : str):
        """
        zips the medium to a destination path

        Args:
            destPath (str): the destination path to zip to
        """
        raise NotImplementedError("zipTo is not implemented")

    @cached_property
    def pkgName(self):
        """
        returns os.path.basename(self.file_path)
        """
        return os.path.basename(self.file_path).split(".")[0]

    def __getattribute__(self, name: str):
        if (
            name.startswith("hasFile_") 
        ):
            
            name = name.split("_", 1)[1]
            # split by _
            if "_" in name:
                name, ext = name.rsplit("_",1)
                name = f"{name}.{ext}"
            
            return name in self.allFiles

        return super().__getattribute__(name)


class ZipMFD(FileDeliveryInterface):
    @cached_property
    def allFiles(self):
        with zipfile.ZipFile(self.file_path) as zf:
            return zf.namelist()

    def readJsonFile(self, fileName):
        with zipfile.ZipFile(self.file_path) as zip_file:
            with zip_file.open(fileName) as f:
                return json.load(f)

    def writeJsonFile(self, fileName, data):
        with zipfile.ZipFile(self.file_path, "a") as zip_file:
            with zip_file.open(fileName, "w") as f:
                json.dump(data, f)

    def getFile(self, fileName):
        with zipfile.ZipFile(self.file_path) as zip_file:
            with zip_file.open(fileName) as f:
                return f.read()     

    def writeFile(self, fileName, data):
        with zipfile.ZipFile(self.file_path, "a") as zip_file:
            zip_file.write(fileName, data)
   
    def unpack(self, target_path):
        with zipfile.ZipFile(self.file_path) as zip_file:
            zip_file.extractall(target_path)

    def copyFile(self, fileName, destPath):
        with zipfile.ZipFile(self.file_path) as zip_file:
            destPath = os.path.dirname(destPath)
            zip_file.extract(fileName, destPath)

    def copyTo(self, destPath):
        with zipfile.ZipFile(self.file_path) as zip_file:
            zip_file.extractall(destPath)
        return FolderMFD(destPath)

    def zipTo(self, destPath):
        shutil.copy(self.file_path, destPath)

class FolderMFD(FileDeliveryInterface):

    @cached_property
    def allFiles(self):
        return os.listdir(self.file_path)        
    
    def readJsonFile(self, fileName):
        with open(os.path.join(self.file_path, fileName), "r") as f:
            return json.load(f)
    
    def writeJsonFile(self, fileName, data):
        with open(os.path.join(self.file_path, fileName), "w") as f:
            json.dump(data, f)


    def pack(self, target_path = None, remove_source = False):
        if target_path is None:
            target_path = self.file_path

        shutil.make_archive(target_path, "zip", self.file_path)

        zmfd = ZipMFD(target_path+".zip")
        if remove_source:
            os.remove(self.file_path)
        return zmfd

    def copyFile(self, fileName, destPath):
        shutil.copyfile(os.path.join(self.file_path, fileName), destPath)

    def copyTo(self, destPath):
        shutil.copytree(self.file_path, destPath)
        return FolderMFD(destPath)

    def zipTo(self, destPath):
        shutil.make_archive(destPath, "zip", self.file_path)
        return ZipMFD(destPath+".zip")

def createMFD( path : str)-> FileDeliveryInterface:
    """
    creates a FileDeliveryInterface from a path

    it may resolve itself to either a ZipMFD or FolderMFD depending on the path

    """

    if os.path.exists(path) and os.path.isdir(path):
        return FolderMFD(path)
    elif os.path.exists(path) and zipfile.is_zipfile(path):
        return ZipMFD(path)
    elif ".zip" not in path and os.path.exists(path + ".zip"):
        return ZipMFD(path + ".zip")
    elif ".zip" in path and os.path.exists(path[:-4]) and os.path.isdir(path[:-4]):
        return FolderMFD(path[:-4])

    return None