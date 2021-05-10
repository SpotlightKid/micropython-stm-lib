"""Unpack an uncompressed tar archive."""

import os
from utarfile import TarFile


def exists(path):
    try:
        _ = os.stat(path)
    except:
        return False
    else:
        return True


def untar(filename, overwrite=False, verbose=False, chunksize=4096):
    with open(filename) as tar:
        for info in TarFile(fileobj=tar):
            if info.type == "dir":
                if verbose:
                    print("D %s" % info.name)

                name = info.name.rstrip("/")
                if not exists(name):
                    os.mkdir(name)
            elif info.type == "file":
                if verbose:
                    print("F %s" % info.name)

                if overwrite or not exists(info.name):
                    with open(info.name, "wb") as fp:
                        while True:
                            chunk = info.subf.read(chunksize)
                            if not chunk:
                               break
                            fp.write(chunk)
            elif verbose:
                print("? %s" % info.name)
