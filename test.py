import os


def get_file_info(directory="."):
    res = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            res.append(os.path.join(root, name))
        for name in dirs:
            res.append(os.path.join(root, name))
    return res