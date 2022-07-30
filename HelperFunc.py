import os
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, 'src\\', relative_path)


def readLocalFile(filename):
    f = open(filename, 'r')
    txt = f.read()
    f.close()

    return txt


def writeLocalFile(filename, txt):
    f = open(filename, mode='w', newline='')
    f.write(txt)
    f.close()
