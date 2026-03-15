import sys
import os


def resource_path(filename):
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)


def data_dir():
    path = r"C:\thesecret"
    os.makedirs(path, exist_ok=True)
    return path
