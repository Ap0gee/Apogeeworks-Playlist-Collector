# -*- coding: utf-8 -*-

__author__ = 'Apogee'

from tkmodels import RootFrame
from utils import get_version

VERSION = (0, 1, 0)

__version__ = get_version(VERSION)

def main():
    root = RootFrame(None)
    root.mainloop()

if __name__ == '__main__':
    main()