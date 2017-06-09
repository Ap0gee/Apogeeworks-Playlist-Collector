__author__ = 'Apogee'

import tkinter.constants as tkc
import constants as c
import _thread
import shutil
import bs4
import sys
import os


class Collector():
    def __init__(self, tk_root, file, dir_target):

        self.path_file = os.path.realpath(file)
        self.file_name_full = os.path.basename(self.path_file)
        self.file_name, self.file_ext = self.get_path_split(self.file_name_full)
        self.dir_root = os.path.dirname(self.path_file)
        self.dir_base = os.path.dirname(self.dir_root)
        self.dir_target = os.path.join(dir_target, self.file_name)

        self.media_found = list()
        self.media_lost = list()

        self.accepted_media_exts = [
            '.cda', '.ivf', '.aif', '.aifc', '.aiff' '.asf', '.asx', '.wax', '.wm',
            '.wma', '.wmd', '.wmv', '.wvx', '.wmp', '.wmx', '.avi', '.wav',
            '.mpeg', '.mpg', '.m1v', '.mp2', '.mpa', '.mpe', '.mp2v*', '.mpv2'
            '.mid', '.midi', '.rmi', '.au',  '.snd', '.mp3', '.m3u', '.vob'
        ]

        self.root = tk_root

    @property
    def raw_data(self):
        try:
            with open(self.path_file, 'r') as f:
                return f.read().replace('\n', '')
        except IOError:
            sys.exit(c.EXIT_CODE_ERROR)

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

    def get_path_split(self, path, get_filename=True, get_ext=True):
        file_name, ext = os.path.splitext(path)

        if get_filename and get_ext or not get_filename and not get_ext:
            return (file_name, ext)
        elif get_filename and not get_ext:
            return file_name
        else:
            return ext

    def get_source_file_paths(self):
        html_data = self.as_html()
        soup = bs4.BeautifulSoup(html_data, 'html.parser')
        list_src = [
            str(media['src']).encode(c.ENCODING_WPL) for media in soup.find_all('source')
        ]
        return list_src

    def __collect(self, callback=None):
        if not os.path.isdir(self.dir_target):
            try:
                os.mkdir(self.dir_target)
            except Exception:
                raise FileExistsError

        frame_main = self.root.frame_main
        list_source_files = self.get_source_file_paths()
        list_source_files_total = len(list_source_files)
        frame_main.set_progress_collection_attr(c.PB_SETTING_MAXIMUM, list_source_files_total)
        frame_main.set_result_total(c.RESULT_TOTAL, list_source_files_total)

        for index, path_source in enumerate(list_source_files):
            #TODO provide user with reason for failure
            media_name_full = os.path.basename(str(path_source.decode('utf-8')))
            media_name, media_ext = self.get_path_split(media_name_full)
            path_media_target_full = os.path.join(self.dir_target, media_name_full)

            if os.path.exists(path_source):
                if path_source not in self.media_found and media_ext in self.accepted_media_exts:
                    self.media_found.append(path_source)
                    try:
                        shutil.copyfile(path_source, path_media_target_full)
                    except shutil.Error as e:
                        print(e)
                        self.media_lost.append(path_source)
                        console_tag = c.TAG_TEXT_RED
                    else:
                        console_tag = c.TAG_TEXT_BLUE
                        msg_failure_reason = None
                else:
                    self.media_lost.append(path_source)
                    console_tag = c.TAG_TEXT_RED
                    print("bad ext")
            else:
                self.media_lost.append(path_source)
                console_tag = c.TAG_TEXT_RED
                print('bad path')

            frame_main.set_progress_collection_attr(c.PB_SETTING_VALUE, index)
            frame_main.set_result_total(c.RESULT_SUCCESS, len(self.media_found))
            frame_main.set_result_total(c.RESULT_FAILURE, len(self.media_lost))
            copy_result = c.RESULT_SUCCESS if not console_tag is c.TAG_TEXT_RED else c.RESULT_FAILURE
            self.root.console("%s: %s" % (copy_result, path_media_target_full), tag=console_tag)

        if callback:
            callback()

    def collect(self, callback=None):
        _thread.start_new_thread(self.__collect, (callback,))




