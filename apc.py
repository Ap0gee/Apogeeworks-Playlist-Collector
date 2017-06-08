# -*- coding: utf-8 -*-

__author__ = 'Apogee'

import tkmodels
import utils

VERSION = (0, 1, 0)

__version__ = utils.get_version(VERSION)

def main():
    root = tkmodels.RootFrame(None)
    root.mainloop()

if __name__ == '__main__':
    main()