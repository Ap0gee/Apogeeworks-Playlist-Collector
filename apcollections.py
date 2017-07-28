__author__ = 'Apogee'

import tkinter.constants as tkc
import constants as c
import _thread
import multiprocessing.pool
import shutil
import bs4
import settings
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
            '.mid', '.midi', '.rmi', '.au',  '.snd', '.mp3', '.mp4', '.m3u', '.vob'
        ]

        self.root = tk_root

    def __raw_data(self):
        try:
            with open(self.path_file, 'r') as f:
                return f.read().replace('\n', '')
        except Exception:
            msg_console = "%s: %s \n=> %s" % (
                c.RESULT_FAILURE, self.path_file, self.root.get_error(c.ERROR_FILE_READ)
            )
            self.root.console(msg_console, tag=c.TAG_TEXT_RED)

    @property
    def raw_data(self):
        async_pool = multiprocessing.pool.ThreadPool(processes=1)
        async_result = async_pool.apply_async(self.__raw_data, ())
        return async_result.get()

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
        #TODO: fix issue with media not being found
        html_data = self.as_html()
        soup = bs4.BeautifulSoup(html_data, 'html.parser')
        list_src = [
            os.path.abspath(media['src']).encode(c.ENCODING_WPL) for media in soup.find_all('source')
        ]
        return list_src

    #TODO: this is not the correct solution, try again.
    def resolve_source_path(self, path):

        if not os.path.exists(path):
            possible_playlist_locations = [
                settings.DIR_USER_PLAYLISTS,
                settings.DIR_WMP_USER_PLAYLISTS,
                settings.DIR_WMP_DEFAULT_PLAYLISTS,
                settings.DIR_WMP_DEFAULT_PLAYLISTS_x86,
            ]

            for loc in possible_playlist_locations:
                try:
                    print(os.chdir(loc))
                    new_path = os.path.abspath(path)
                    os.chdir(settings.DIR_BASE)
                    if os.path.exists(new_path):
                        print('returning new')
                        return new_path
                except WindowsError:
                    pass


        return path

    def __collect(self, callback=None):
        if not os.path.exists(self.dir_target):
            try:
                os.mkdir(self.dir_target)
            except (FileNotFoundError, IOError):
                msg_console = "%s: %s \n=> %s" % (
                c.RESULT_FAILURE, self.dir_target, self.root.get_error(c.ERROR_DIRECTORY_CREATE)
                )
                self.root.console(msg_console, tag=c.TAG_TEXT_RED)

                if callback:
                    callback()

        frame_main = self.root.frame_main
        list_source_files = self.get_source_file_paths()
        list_source_files_total = len(list_source_files)
        frame_main.set_progress_collection_attr(c.PB_SETTING_MAXIMUM, list_source_files_total)
        frame_main.set_result_total(c.RESULT_TOTAL, list_source_files_total)

        for index, path_source in enumerate(list_source_files):

            if frame_main.state is c.STATE_COLLECTING:

                path_source = str(path_source, 'utf-8')

                media_name_full = os.path.basename(path_source)

                media_name, media_ext = self.get_path_split(media_name_full)
                path_media_target_full = os.path.join(self.dir_target, media_name_full)

                msg_failure_reason = None

                path_source = self.resolve_source_path(path_source)

                if os.path.exists(path_source):
                    if path_source not in self.media_found:
                        if media_ext in self.accepted_media_exts:
                            try:
                                shutil.copyfile(path_source, path_media_target_full)
                            except shutil.Error:
                                msg_failure_reason = self.root.get_error(c.ERROR_COPY_FAILED)
                        else:
                            msg_failure_reason = self.root.get_error(c.ERROR_EXT_BAD)
                    else:
                        msg_failure_reason = self.root.get_error(c.ERROR_DUPLICATE_MEDIA)
                else:
                    msg_failure_reason = self.root.get_error(c.ERROR_PATH_BAD)

                if not msg_failure_reason:
                    tag_console = c.TAG_TEXT_BLUE
                    result_copy = c.RESULT_SUCCESS
                    self.media_found.append(path_source)
                    msg_console = "%s: %s" % (result_copy, path_source)
                else:
                    tag_console = c.TAG_TEXT_RED
                    result_copy = c.RESULT_FAILURE
                    self.media_lost.append(path_source)
                    msg_console = "%s: %s \n=> %s" % (result_copy, path_source, msg_failure_reason)

                frame_main.set_progress_collection_attr(c.PB_SETTING_VALUE, index + 1)
                frame_main.set_result_total(c.RESULT_SUCCESS, len(self.media_found))
                frame_main.set_result_total(c.RESULT_FAILURE, len(self.media_lost))

                self.root.console(msg_console, tag=tag_console)

            else:
                break

        if callback:
            callback()

    def collect(self, callback=None):
        _thread.start_new_thread(self.__collect, (callback,))




