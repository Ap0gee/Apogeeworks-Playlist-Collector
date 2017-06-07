__author__ = 'Apogee'

from shutil import copyfile
import constants as c
import bs4
import sys
import os

EXIT_CODE_OK = 0
EXIT_CODE_ERROR = 1

class Collector():
    def __init__(self, file, dir_target):
        self.verify_file(file)
        self.path_file = os.path.realpath(file)
        self.file_name = os.path.basename(self.path_file)
        self.dir_root = os.path.dirname(self.path_file)
        self.dir_base = os.path.dirname(self.dir_root)
        self.media_found = list()
        self.media_lost = list()
        self.dir_target = dir_target
        self.accepted_media_exts = [
            '.cda', '.ivf', '.aif', '.aifc', '.aiff' '.asf', '.asx', '.wax', '.wm',
            '.wma', '.wmd', '.wmv', '.wvx', '.wmp', '.wmx', '.avi', '.wav',
            '.mpeg', '.mpg', '.m1v', '.mp2', '.mpa', '.mpe', '.mp2v*', '.mpv2'
            '.mid', '.midi', '.rmi', '.au',  '.snd', '.mp3', '.m3u', '.vob'
        ]

    @property
    def raw_data(self):
        try:
            with open(self.path_file, 'r') as f:
                return f.read().replace('\n', '')
        except IOError:
            sys.exit(EXIT_CODE_ERROR)

    @classmethod
    def verify_file(cls, file):
        if os.path.exists(file) & os.path.isfile(file):
            return True
        raise FileNotFoundError

    def as_html(self):
        raw_data = str(self.raw_data)

        data_replacements = [
            ('<?wpl version="1.0"?>', '<!DOCTYPE HTML>'),
            ('<sml>', '<html>'), ('</sml', '</html>'),
            ('<seq>', '<li>'), ('</seq>', '</li>'),
            ('<media ', '<source ')
        ]

        for replacement in data_replacements:
            old, new = replacement
            raw_data = raw_data.replace(old, new)

        return raw_data

    def write_to_file(self, data, file):
        self.verify_file(file)
        try:
            with open(file, 'w') as f:
                f.write(data)
        except IOError:
            sys.exit(EXIT_CODE_ERROR)

    def get_source_file_paths(self):
        html_data = self.as_html()
        soup = bs4.BeautifulSoup(html_data, 'html.parser')
        list_src = [str(media['src']).encode(c.ENCODING_WPL) for media in soup.find_all('source')]
        return list_src

    def gather_media_at(self, target_dir):
        #TODO remove possibility of duplicate tracks
        _file_name_full = os.path.basename(target_dir)
        _file_name, _ext = os.path.splitext(_file_name_full)
        dir_media_target = os.path.join(target_dir, _file_name)
        if not os.path.isdir(dir_media_target):
            os.mkdir(dir_media_target)

        for path in self.get_source_file_paths():
            if os.path.exists(path):
                self.media_found.append(path)
                file_name_full = os.path.basename(str(path.decode('utf-8')))
                file_name, ext = os.path.splitext(file_name_full)

                if ext in self.accepted_media_exts:
                    path_target_full = os.path.join(target_dir, file_name_full)
                    copyfile(path, path_target_full)
                else:
                    self.media_lost.append(path)
            else:
                self.media_lost.append(path)

    def collect(self):
        print("collecting data from %s @ %s" % (self.file_name, self.dir_target))
        self.gather_media_at(self.dir_target)
        print("total media gathered: %s" % len(self.media_found))
        print("total media lost: %s" % len(self.media_lost))
        print("lost media: %s" % self.media_lost)
