import os

def getAllFiles(path :str, exclude_prefixes : list = ["_"], exclude_suffixes : list = [".pyc"]):
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