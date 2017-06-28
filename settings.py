__author__ = 'Apogee'

import sys
import os
import utils

if hasattr(sys, 'frozen'):
    DIR_BASE = os.path.abspath(os.path.dirname(sys.executable))
else:
    DIR_BASE = os.path.abspath(os.path.dirname(__file__))

DIR_ASSETS = os.path.join(DIR_BASE, 'assets')
DIR_IMAGES = os.path.join(DIR_ASSETS, 'images')
DIR_CURSORS = os.path.join(DIR_ASSETS, 'cursors')
DIR_LOGS = os.path.join(DIR_BASE, 'logs')
DIR_CONFIG = os.path.join(DIR_BASE, 'config')

DIR_USER = os.path.expanduser('~')
DIR_USER_MUSIC = os.path.join(DIR_USER, 'Music')
DIR_USER_PLAYLISTS = os.path.join(DIR_USER_MUSIC, 'Playlists')

DIR_WMP_DEFAULT_x86 = 'C:\\Program Files (x86)\\Windows Media Player'
DIR_WMP_DEFAULT = 'C:\\Program Files\\Windows Media Player'
DIR_WMP_USER = utils.get_user_wmp_path()

DIR_WMP_DEFAULT_PLAYLISTS_x86 = os.path.join(DIR_WMP_DEFAULT_x86, 'Playlists')
DIR_WMP_DEFAULT_PLAYLISTS = os.path.join(DIR_WMP_DEFAULT, 'Playlists')
DIR_WMP_USER_PLAYLISTS = os.path.join(DIR_WMP_USER, 'Playlists')

FILE_LOG_NAME = 'apc.log'
FILE_CONFIG_NAME = 'apc.ini'