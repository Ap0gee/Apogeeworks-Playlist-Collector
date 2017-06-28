__author__ = 'Apogee'

import tkinter.constants as tkc
import constants as c
import winreg
import sys
import os

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

def winreg_get_sub_key(key, sub_key_name):
    i = 0
    while True:
        try:
            sub_key = winreg.EnumKey(key, i)
            if sub_key == sub_key_name:
                return winreg.OpenKey(key, sub_key_name)
            i += 1
        except WindowsError:
            return False

def get_user_wmp_path():
    reg_conn = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    key_app_paths = winreg.OpenKey(reg_conn, c.HKEY_LM_APP_PATHS)

    sub_key = winreg_get_sub_key(key_app_paths, c.SUB_KEY_WMP)
    sub_key_val, sub_key_val_id = winreg.QueryValueEx(sub_key, c.SUB_KEY_WMP_TARGET_VAL)
    real_path = winreg.ExpandEnvironmentStrings(sub_key_val)

    return real_path