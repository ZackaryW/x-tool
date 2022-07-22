import os
import inspect
from xtool.exception import XToolNotImplementedException
from xtool.ext import XToolExtension

def getAllFiles(path :str, exclude_prefixes : list = ["_"], exclude_suffixes : list = [".pyc"]):
    """
    returns a list of all files in a directory

    Args:
        path (str): the path to the directory
        exclude_prefixes (list, optional): a list of prefixes to exclude. Defaults to ["_"].
        exclude_suffixes (list, optional): a list of suffixes to exclude. Defaults to [".pyc"].
    Returns:
        _type_: _description_
    """

    allFilesInPath = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if any(file.startswith(prefix) for prefix in exclude_prefixes):
                continue

            if any(file.endswith(suffix) for suffix in exclude_suffixes):
                continue

            allFilesInPath.append(os.path.join(root, file))
        
        for dir in dirs:
            allFilesInPath += getAllFiles(os.path.join(root, dir))

    return allFilesInPath

def callExtensions(**kwargs):
    """
    this is a method that originally belongs to a method of XToolExtension 
    
    currently, it is used as a boilerplate solution to avoid self being passed into the extension twice
    """ 

    # method name
    callerMethodName = inspect.stack()[1].function

    for ext in kwargs.get('self').extensions.keys():
        ext : XToolExtension
        if callerMethodName in ext._METHODS_NOT_AVAILABLE:
            continue
        try:
            ext.callMethod(callerMethodName, **{k : v for k, v in kwargs.items() if k != 'self'})
        except XToolNotImplementedException:
            ext._METHODS_NOT_AVAILABLE.append(callerMethodName)
            continue
        except:
            raise