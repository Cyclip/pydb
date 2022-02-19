import os
from pathlib import Path
from ..creds import createDefaultCreds

dbname = "database"

def init():
    if not os.path.isdir(dbname):
        setupDb(dbname)


def setupDb(name):
    os.makedirs(name)

    folders = ["tables", "index"]

    createDefaultCreds()