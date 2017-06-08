__author__ = 'Apogee'

import tkinter.constants as tkc
import constants as c
import sys

def tk_font(family="Helvetica", size=12, weight="normal"):
    return (family, size, weight)

def tk_get_root(current_frame):
    def is_root(frame):
        try:
            if frame.parent == None:
                return frame
            return is_root(frame.parent)
        except:
            return None
    return is_root(current_frame)

def get_version(version=None):
    if version is None:
        from apc import VERSION as version

    return '.'.join(str(x) for x in version)

def write_to_file(self, data, file, mode='w'):
    try:
        with open(file, mode) as f:
            f.write(data)
    except IOError:
        sys.exit(c.EXIT_CODE_ERROR)