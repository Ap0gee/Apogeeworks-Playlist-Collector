__author__ = 'Apogee'

import sys
import os

if hasattr(sys, 'frozen'):
    DIR_BASE = os.path.abspath(os.path.dirname(sys.executable))
else:
    DIR_BASE = os.path.abspath(os.path.dirname(__file__))

DIR_ASSETS = os.path.join(DIR_BASE, 'assets')
DIR_IMAGES = os.path.join(DIR_ASSETS, 'images')
DIR_CURSORS = os.path.join(DIR_ASSETS, 'cursors')
DIR_LOGS = os.path.join(DIR_BASE, 'logs')
FILE_LOG_NAME = 'apc.log'