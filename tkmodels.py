__author__ = 'Apogee'

import tkinter
from tkinter import ttk
from tkinter import Tk
from tkinter import filedialog
import constants as c
import tkinter.constants as tkc
from datetime import datetime
from apcollections import Collector
import subprocess
import logging
import configparser
import random
import utils
import settings
import os


class StyledFrame(tkinter.Frame):
    def __init__(self, parent, **kwargs):
        tkinter.Frame.__init__(self, parent, **kwargs)

        self.propagate(False)
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.config(
            relief=tkc.RAISED
        )
        self.parent = parent
        self.root = utils.tk_get_root(self)
        self.root.frame_register(self)

    def init_ui(self):
        pass

    def apply_config(self, config_settings):
        pass

    def on_start(self):
        pass


class StyledTopLevelFrame(tkinter.Toplevel):
    def __init__(self, parent, **kwargs):
        tkinter.Toplevel.__init__(self, parent, **kwargs)

        self.overrideredirect(True)
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.attributes('-topmost', True)
        self.is_viewing = False
        self.parent = parent
        self.root = utils.tk_get_root(self)

    def init_ui(self):
        pass

    def apply_config(self, config_settings):
        pass

    def on_start(self):
        pass


class StyledMenuFrame(StyledFrame):
    def __init__(self, parent, **kwargs):
        StyledFrame.__init__(self, parent, **kwargs)

        self.root_main_frame = self.root.frame_main
        self.frame_main_cp = self.root_main_frame.control_panel

        self.w, self.h = (
            self.root_main_frame.winfo_width(),
            self.root_main_frame.winfo_height()
        )
        self.cp_w, self.cp_h = (
            self.frame_main_cp.winfo_width(),
            self.frame_main_cp.winfo_height()
        )

    def init_ui(self):
        pass


class SizedTextBox(tkinter.Frame):
    def __init__(self, master, width=0, height=0, **kwargs):
        self.width = width
        self.height = height
        tkinter.Frame.__init__(self, master, width=self.width, height=self.height)

        self.widget = tkinter.Text(
            self,
            font=utils.tk_font(size=10),
            highlightbackground=c.COLOR_WHITE,
            highlightcolor=c.COLOR_BLUE,
            highlightthickness=0,
            width=20,
            wrap=tkc.CHAR,
            state=tkc.DISABLED,
            spacing3=5,
            cursor=c.CURSOR_ARROW
        )
        sb_y = ttk.Scrollbar(
            orient=tkc.VERTICAL,
            command=self.widget.yview
        )
        sb_y.pack(
            in_=self, side=tkc.RIGHT, fill=tkc.Y
        )
        self.widget['yscroll'] = sb_y.set

        self.widget.pack(
            expand=tkc.YES,
            fill=tkc.BOTH
        )

    def pack(self, *args, **kwargs):
        tkinter.Frame.pack(self, *args, **kwargs)
        self.pack_propagate(False)
        return self.widget

    def grid(self, *args, **kwargs):
        tkinter.Frame.grid(self, *args, **kwargs)
        self.grid_propagate(False)
        return self.widget


class RootSplashFrame(StyledTopLevelFrame):
    def __init__(self, parent, **kwargs):
        StyledTopLevelFrame.__init__(self, parent, **kwargs)

        self.init_ui()
        self.show_logo()

    def init_ui(self):
        self.config(
            bg=c.COLOR_DARK_KNIGHT
        )
        center_x, center_y = self.root.center_frame()
        #TODO: fix image size
        self.image_logo = tkinter.PhotoImage(
            file=os.path.join(settings.DIR_IMAGES, "logo_apogeeworks.gif")
        )
        self.canvas_logo = tkinter.Canvas(
            master=self,
            bg=c.COLOR_DARK_KNIGHT,
            border=None,
            width=400, height=161,
            bd=0,
            highlightthickness=0,
            relief='ridge'
        )
        self.canvas_logo.create_image(0, 0, image=self.image_logo, anchor=tkc.NW)

        self.geometry(
            '%dx%d+%d+%d' % (self.root.w, self.root.h, center_x, center_y)
        )
        self.canvas_logo.pack(
            expand=tkc.YES,
        )

    def show_logo(self, duration_seconds=2):
        self.update()
        self.after(2000, self.hide_logo)

    def hide_logo(self):
        self.after_cancel(self.hide_logo)
        self.destroy()


class RootFrame(Tk):
    def __init__(self, parent, **kwargs):
        Tk.__init__(self, **kwargs)
        self.parent = parent

        self.overrideredirect(True)
        self.resizable(False, False)
        self.propagate(False)

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.attributes('-topmost', False)

        self.w, self.h = 425, 450

        self.__menu_viewing = None

        self.__registered_frames = []

        self.init_ui()

        self.bind(
            "<Map>", self.bind_redirect
        )
        #self.bind_all("<Key>", self.track_keys)
        #self.bind_all("<Control-l>", self.track_keys)
        #self.bind_all("<Control-e>", self.track_keys)
        #self.bind_all("<Control-k>", self.track_keys)
        #self.bind_all("<Control-d>", self.track_keys)
        #self.bind_all("<Control-m>", self.track_keys)
        #self.bind_all("<Control-n>", self.track_keys)
        #self.bind_all("<Control-s>", self.track_keys)
        #self.bind_all("<Alt-i>", self.track_keys)
        #self.bind_all("<Alt-x>", self.track_keys)
        self.bind_all("<Alt-q>", self.track_keys)

        self.key_map = {
            # 76: self.menu_frame.viewLoadGroup, #"<Control-l>"
            # 75: self.menu_frame.askClearGroup, #"<Control-k>"
            # 69: self.menu_frame.viewEditGroup, #"<Control-e>"
            # 68: self.menu_frame.askDeleteGroup, #"<Control-d>"
            # 78: self.menu_frame.viewNewGroup, #"<Control-n>"
            # 77: self.menu_frame.viewDeleteMultipleGroup, #"<Control-m>"
            # 83: self.summoned, #"<Control-s>"
            # 73: self.destroy, #"<Alt-i>"
            # 88: self.destroy, #"<Alt-x>"
            81: self.kill, #"<Alt-q>"
        }

        self.tip_map = {
            c.TIP_BROWSE: 'Browse for and select your paths.',
            c.TIP_START: 'Press the "Start" button to begin!',
            c.TIP_RANDOM: [
                'You can disable these tips in "Options" > "Configure".',
                'You can exit quickly with the "Alt+Q" shortcut.',
            ],
            c.TIP_LAST: ''
        }

        self.error_map = {
            c.ERROR_PATH_BAD: "Media at this location not found.",
            c.ERROR_EXT_BAD: "Media type not supported.",
            c.ERROR_COPY_FAILED: "Unable to copy media to destination.",
            c.ERROR_DUPLICATE_MEDIA: "Media already exists in directory.",
            c.ERROR_FILE_READ: "Unable to read file.",
            c.ERROR_DIRECTORY_CREATE: "Unable to create directory."
        }

        self.log = logging.getLogger(__name__)
        self.handler_log = logging.FileHandler(
            os.path.join(settings.DIR_LOGS, settings.FILE_LOG_NAME),
            mode='w+'
        )
        self.formatter_log = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s'
        )
        self.handler_log.setFormatter(self.formatter_log)
        self.log.addHandler(self.handler_log)
        self.log.setLevel(logging.DEBUG)

        self.config_settings = self.get_config()

        self.on_start()

    def init_ui(self):
        self.title("Apogeeworks Playlist Collector")

        self.configure(
            bg=c.COLOR_WHITE,
            relief=tkc.RAISED,
            width=self.w,
            height=self.h
        )
        center_x, center_y = self.center_frame()
        self.geometry(
            '%dx%d+%d+%d' % (self.w, self.h, center_x, center_y)
        )
        #TODO: show splash
        #self.frame_splash = RootSplashFrame(self)
        self.update_idletasks()

        self.frame_main = RootMainFrame(self)
        self.frame_tool = RootToolFrame(self)
        self.frame_menu = RootMenuFrame(self)
        self.frame_footer = RootFooterFrame(self)
        #self.control_frame = RootViewControlFrame(self)

        self.update()

    @property
    def menu_viewing(self):
        return self.__menu_viewing

    @menu_viewing.setter
    def menu_viewing(self, value):
        self.__menu_viewing = value

    def browse_file(self, tk_entry):
        path = filedialog.askopenfilename()

        if not path is '':
            tk_entry.delete(0, tkc.END)
            tk_entry.insert(0, path)

    def browse_directory(self, tk_entry):
        path = filedialog.askdirectory()

        if not path is '':
            tk_entry.delete(0, tkc.END)
            tk_entry.insert(0, path)

    def on_hover(self, event):
        pass

    def exit_hover(self, event):
        pass

    def bind_redirect(self, event):
        if self.wm_state() == c.STATE_ICONIC:
            self.bind(
                "<Map>", self.un_minimize
            )

    def un_minimize(self, event):
        self.update_idletasks()
        self.overrideredirect(True)
        self.wm_deiconify()

        self.bind(
            "<Map>", self.bind_redirect
        )

    def minimize(self):
        self.update_idletasks()
        self.overrideredirect(False)
        self.wm_iconify()

    def center_frame(self):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        return screen_w/2-self.w/2, screen_h/2-self.h/2

    def cloak(self, alpha):
        if not self.is_cloaked:
            self.attributes("-alpha", alpha)
            self.is_cloaked = True

    def un_cloak(self):
        self.attributes("-alpha", 1)
        self.is_cloaked = False

    def track_cursor(self):
        if not self.busy:
            cursor_x, cursor_y = self.winfo_pointerxy()

    def track_keys(self, event):
        callback = self.key_map[event.keycode]
        callback()

    def track_events(self):
        self.after(50, self.track_events)

    def alert_action_info(self, text, **kwargs):
        fg = kwargs.get('fg', c.COLOR_WHITE)
        bg = kwargs.get('bg', c.COLOR_ORANGE)
        font = kwargs.get('font', utils.tk_font(size=12))

        self.frame_footer.label_action_info.config(
            text=text,
            fg=fg,
            bg=bg,
            font=font,
        )

    def alert_action_symbol(self, text, **kwargs):
        fg = kwargs.get('fg', c.COLOR_WHITE)
        bg = kwargs.get('bg', c.COLOR_BLUE)

        self.frame_footer.label_action_symbol.config(
            text=text,
            fg=fg,
            bg=bg,
        )

    def get_tip(self, tip, format='[Tip]: %s'):
        if not tip == c.TIP_RANDOM:
            self.tip_map.update(tip_last=self.tip_map[tip])
            return format % self.tip_map.get(c.TIP_LAST)

        list_tips = self.tip_map[tip]
        self.tip_map.update(tip_last=random.choice(list_tips))
        return format % self.tip_map.get(c.TIP_LAST)

    def get_error(self, err):
        return self.error_map[err]

    def console(self, msg, **kwargs):
        self.frame_main.console(msg, **kwargs)

    def log_info(self, msg, *args, **kwargs):
        self.log.info(msg, *args, **kwargs)

    def frame_register(self, tk_frame):
        if not tk_frame in self.__registered_frames:
            self.__registered_frames.append(tk_frame)

    def get_config(self):
        config_parser = configparser.ConfigParser()
        file_config = os.path.join(settings.DIR_CONFIG, settings.FILE_CONFIG_NAME)

        def read_settings():
            if config_parser.read(file_config):
                return config_parser
            else:
                raise FileNotFoundError

        def add_settings():
            config_parser.add_section('General')
            config_parser.set('General', 'StayOnTop', 'False')
            config_parser.set('General', 'ShowTips', 'True')
            config_parser.add_section('Visual')
            config_parser.set('Visual', 'FrameDragAlpha', '0.8')
            config_parser.add_section('Logging')
            config_parser.set('Logging', 'EnableLogging', 'True')
            config_parser.set(
                'Logging', 'LogFilePath', os.path.join(
                    settings.DIR_LOGS, settings.FILE_LOG_NAME
                )
            )
            with open(file_config, 'w') as f:
                config_parser.write(f)
        try:
           return read_settings()
        except FileNotFoundError:
            add_settings()
            return read_settings()

    def get_config_setting(self, category, setting):
        return self.config_settings.get(category, setting)

    def set_config(self, category, setting, value):
        self.config_settings.set(category, setting, value)

    def save_config(self):
        file_config = os.path.join(settings.DIR_CONFIG, settings.FILE_CONFIG_NAME)
        with open(file_config, 'w') as f:
            self.config_settings.write(f)

    def on_start(self):
        self.console('process started')
        self.alert_action_symbol('v%s' % utils.get_version())
        for frame in self.__registered_frames:
            frame.apply_config(self.config_settings)
            frame.on_start()
        self.track_events()

    def kill(self):
        self.console("process terminated")
        self.destroy()


class RootToolFrame(StyledFrame):
    def __init__(self, parent, **kwargs):
        StyledFrame.__init__(self, parent, **kwargs)

        self.init_ui()

        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.on_motion)
        self.tool_label.bind("<ButtonPress-1>", self.start_move)
        self.tool_label.bind("<ButtonRelease-1>", self.stop_move)
        self.tool_label.bind("<B1-Motion>", self.on_motion)
        self.tool_label.bind("<Enter>", self.on_hover)
        self.tool_label.bind("<Leave>", self.exit_hover)
        self.btn_close.bind("<Enter>", self.on_hover)
        self.btn_close.bind("<Leave>", self.exit_hover)
        self.btn_minimize.bind("<Enter>", self.on_hover)
        self.btn_minimize.bind("<Leave>", self.exit_hover)

    def init_ui(self):
        self.config(
            background=c.COLOR_DARK_KNIGHT,
            relief=tkc.FLAT,
            width=self.parent.winfo_width(),
            height=25
        )
        self.tool_label = tkinter.Label(
            self,
            font=utils.tk_font(),
            background=c.COLOR_DARK_KNIGHT,
            width=38,
        )
        self.btn_minimize = tkinter.Button(
            self,
            text=c.UNICODE_BTN_MINIMIZE,
            font=utils.tk_font(size=20),
            background=c.COLOR_DARK_KNIGHT,
            fg=c.COLOR_WHITE,
            width=2,
            relief=tkc.FLAT,
            command=self.root.minimize
        )
        self.btn_close = tkinter.Button(
            self,
            text=c.UNICODE_BTN_CLOSE,
            font=utils.tk_font(size=20),
            background=c.COLOR_RED,
            fg=c.COLOR_WHITE,
            width=2,
            relief=tkc.FLAT,
            command=self.root.kill
        )
        self.grid(
            column=0, row=0,
            sticky="ew"
        )
        self.btn_close.pack(
            side=tkc.RIGHT,
            padx=(10, 10)
        )
        self.btn_minimize.pack(
            side=tkc.RIGHT,
        )
        self.tool_label.pack(
            side=tkc.RIGHT,
        )

        self.update()

    def on_hover(self, event):
        if not event.widget['state'] == tkc.DISABLED:
            event.widget['cursor'] = c.CURSOR_HAND_2

    def exit_hover(self, event):
        event.widget['cursor'] = c.CURSOR_ARROW

    def start_move(self, event):
        self.parent.lift()
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        event.widget['cursor'] = c.CURSOR_HAND_2
        self.dragging_parent = False
        self.parent.un_cloak()

    def on_motion(self, event):
        self.dragging_parent = True
        #self.parent.cloak(self.parent.frame_drag_alpha_value.get())

        delta_x = event.x - self.x
        delta_y = event.y - self.y

        root_x = self.parent.winfo_x()
        root_y = self.parent.winfo_y()

        new_x = root_x + delta_x
        new_y = root_y + delta_y

        self.parent.geometry('+%s+%s' % (new_x, new_y))


class RootMenuFrame(StyledFrame):
    def __init__(self, parent, **kwargs):
       StyledFrame.__init__(self, parent, **kwargs)

       self.init_ui()

       self.file_menu.bind("<<MenuSelect>>", self.menu_select_callback)

    def init_ui(self):
        self.config(
            background=c.COLOR_GREY,
            relief=tkc.FLAT,
            width=self.parent.winfo_width(), height=22,
        )
        self.menu_file = tkinter.Menubutton(
            self, text="File",
            font=utils.tk_font(),
            background=c.COLOR_GREY
        )
        self.menu_options = tkinter.Menubutton(
            self, text="Options",
            font=utils.tk_font(),
            background=c.COLOR_GREY
        )
        self.menu_label = tkinter.Label(
            self,
            text="Apogeeworks Playlist Collector",
            relief=tkc.FLAT,
            font=utils.tk_font(),
            bg=c.COLOR_BLUE,
            fg=c.COLOR_WHITE,
            height=2, width=27,
        )
        self.grid(
            column=0, row=1,
            sticky="n",
        )
        self.menu_label.pack(
            side=tkc.RIGHT,
        )
        self.menu_file.pack(
            side=tkc.LEFT,
            padx=(0, 0)
        )
        self.menu_options.pack(
            side=tkc.LEFT,
            padx=(5, 0)
        )
        self.file_menu = tkinter.Menu(
            self.menu_file,
            tearoff=0
        )
        self.menu_file['menu'] = self.file_menu

        self.options_menu = tkinter.Menu(
            self.menu_options,
            tearoff=0
        )
        self.menu_options['menu'] = self.options_menu

        self.file_menu.add_command(
            label="{0}{1}{2}".format("Quit", " "*8, "(Alt + Q)"),
            command=self.parent.destroy
        )
        self.options_menu.add_command(
            label="Configure...",
            command=lambda: self.view_menu(RootConfigureFrame)
        )
        self.options_menu.add_separator()
        self.options_menu.add_command(
            label="View Tutorial...",
            command=lambda: self.view_menu(RootTutorialFrame)
        )

        self.update()

    def menu_select_callback(self, event):
        pass

    def view_menu(self, frame_menu):
        if self.root.menu_viewing:
            self.root.menu_viewing.destroy()
        self.root.menu_viewing = frame_menu(self.root)


class RootMainFrame(StyledFrame):
    def __init__(self, parent, **kwargs):
        StyledFrame.__init__(self, parent, **kwargs)

        self.var_console_text_size = tkinter.IntVar(value=9)
        self.var_media_success_total = tkinter.IntVar()
        self.var_media_failure_total = tkinter.IntVar()
        self.var_media_total = tkinter.IntVar()

        self.__state = None

        self.init_ui()

        self.map_tracked_entries = {
            'collection': {
                'widget': self.entry_collection_path,
                'verified': lambda path: self.verify_dir_collection(path),
                'set': False,
                'last': None,
                'browser': self.browser_collection_path
            },
            'playlist': {
                'widget': self.entry_playlist_path,
                'verified': lambda path: self.verify_path_playlist(path),
                'set': False,
                'last': None,
                'browser': self.browser_playlist_path
            }
        }
        self.textbox_console_output.bindtags(
            (self.textbox_console_output, self.textbox_console_output, "all")
        )
        self.textbox_console_output.bind_all("<MouseWheel>", self.on_mousewheel)

        self.textbox_console_output.tag_configure(
            c.TAG_TEXT_RED, foreground=c.COLOR_RED
        )
        self.textbox_console_output.tag_configure(
            c.TAG_TEXT_GREEN, foreground=c.COLOR_GREEN
        )
        self.textbox_console_output.tag_configure(
            c.TAG_TEXT_ORANGE, foreground=c.COLOR_ORANGE
        )
        self.textbox_console_output.tag_configure(
            c.TAG_TEXT_BLUE, foreground=c.COLOR_BLUE
        )

        self.label_clear_entries.bind('<Button-1>', lambda e: self.clear_entries())
        self.label_clear_console.bind('<Button-1>', lambda e: self.clear_console())
        self.label_clear_all.bind('<Button-1>', lambda e: self.clear_all())
        self.label_view_logs.bind('<Button-1>', lambda e: self.view_logs())

    def init_ui(self):
        self.config(
            bg=c.COLOR_WHITE,
            width=self.root.w,
            height=self.root.h
        )
        self.control_panel = StyledFrame(
            self,
            width=self.root.w - 25,
            height=self.root.h - 115,
            relief=tkc.RAISED
        )
        self.group_playlist = tkinter.LabelFrame(
            self.control_panel,
            font=utils.tk_font(size=10, weight=c.FONT_WEIGHT_BOLD),
            text="Media Playlist",
        )
        self.label_playlist_path_entry = tkinter.Label(
            self.group_playlist,
            text="File Path :"
        )
        self.entry_playlist_path = tkinter.Entry(
            self.group_playlist,
            width=40,
        )
        self.group_collection = tkinter.LabelFrame(
            self.control_panel,
            font=utils.tk_font(size=10, weight=c.FONT_WEIGHT_BOLD),
            text="Collection Location",
        )
        self.label_collection_path_entry = tkinter.Label(
            self.group_collection,
            text="Directory Path :"
        )
        self.entry_collection_path = tkinter.Entry(
            self.group_collection,
            width=40,
        )
        self.browser_playlist_path = tkinter.Button(
            self.group_playlist,
            text="Change",
            width=6, height=1,
            relief=tkc.RAISED,
            command=lambda: self.root.browse_file(self.entry_playlist_path)
        )
        self.browser_collection_path = tkinter.Button(
            self.group_collection,
            text="Change",
            width=6, height=1,
            relief=tkc.RAISED,
            command=lambda: self.root.browse_directory(self.entry_collection_path)
        )
        self.frame_links_top = tkinter.Frame(
            self.control_panel
        )
        self.frame_links_bottom = tkinter.Frame(
            self.control_panel,
        )
        self.label_clear_entries = tkinter.Label(
            self.frame_links_top,
            fg=c.COLOR_BLUE,
            font=utils.tk_font(size=10, weight='bold underline'),
            text="clear paths",
            cursor=c.CURSOR_HAND_2
        )
        self.label_clear_console = tkinter.Label(
            self.frame_links_bottom,
            fg=c.COLOR_BLUE,
            font=utils.tk_font(size=10, weight='bold underline'),
            text="clear console",
            cursor=c.CURSOR_HAND_2
        )
        self.label_clear_all = tkinter.Label(
            self.frame_links_bottom,
            fg=c.COLOR_BLUE,
            font=utils.tk_font(size=10, weight='bold underline'),
            text="clear all",
            cursor=c.CURSOR_HAND_2
        )
        self.label_view_logs = tkinter.Label(
            self.frame_links_bottom,
            fg=c.COLOR_ORANGE,
            font=utils.tk_font(size=10, weight='bold underline'),
            text="view logs",
            cursor=c.CURSOR_HAND_2
        )
        self.group_console = tkinter.LabelFrame(
            self.control_panel,
            font=utils.tk_font(size=10, weight=c.FONT_WEIGHT_BOLD),
            text="Console Output",
        )
        self.textbox_console_output = SizedTextBox(
            self.group_console,
            height=100,
        )
        self.frame_tools = tkinter.Frame(
            self.control_panel
        )
        self.scale_console_text = tkinter.Scale(
            self.frame_tools,
            from_=8, to=14,
            resolution=2,
            orient=tkc.HORIZONTAL,
            showvalue=False,
            highlightbackground=c.COLOR_BLUE,
            variable=self.var_console_text_size,
            command=self.set_console_text_size,
        )
        self.progress_collection = ttk.Progressbar(
            self.frame_tools,
            orient=tkc.HORIZONTAL,
            length=275,
            mode=c.MODE_DETERMINATE
        )
        self.group_totals = tkinter.LabelFrame(
            self.control_panel,
            font=utils.tk_font(size=10, weight=c.FONT_WEIGHT_BOLD),
            text="Totals",
        )
        self.frame_totals = tkinter.Frame(
            self.group_totals,
        )
        self.label_media_success = tkinter.Label(
            self.frame_totals,
            text="Success:",
            font=utils.tk_font(size=10),
            width=7, height=1,
            relief=tkc.FLAT,
            anchor=tkc.E,
        )
        self.label_value_media_success = tkinter.Label(
            self.frame_totals,
            textvariable=self.var_media_success_total,
            font=utils.tk_font(size=10),
            width=5, height=1,
            fg=c.COLOR_GREEN,
            relief=tkc.FLAT,
            anchor=tkc.W,
        )
        self.label_media_failure = tkinter.Label(
            self.frame_totals,
            text="Failure:",
            font=utils.tk_font(size=10),
            width=5, height=1,
            relief=tkc.FLAT,
            anchor=tkc.E,
        )
        self.label_value_media_failure = tkinter.Label(
            self.frame_totals,
            textvariable=self.var_media_failure_total,
            font=utils.tk_font(size=10),
            width=5, height=1,
            fg=c.COLOR_RED,
            relief=tkc.FLAT,
            anchor=tkc.W,
        )
        self.label_media_total = tkinter.Label(
            self.frame_totals,
            text="Total:",
            font=utils.tk_font(size=10),
            width=4, height=1,
            relief=tkc.FLAT,
            anchor=tkc.E,
        )
        self.label_value_media_total = tkinter.Label(
            self.frame_totals,
            textvariable=self.var_media_total,
            font=utils.tk_font(size=10),
            width=5, height=1,
            relief=tkc.FLAT,
            anchor=tkc.W,
        )
        self.btn_start = tkinter.Button(
            self.control_panel,
            text="START",
            font=utils.tk_font(),
            width=8, height=1,
            bg=c.COLOR_GREEN,
            fg=c.COLOR_WHITE,
            relief=tkc.FLAT,
            command=lambda: self.collect_media(
                self.map_tracked_entries['playlist'].get('last'),
                self.map_tracked_entries['collection'].get('last')
            )
        )
        self.btn_stop = tkinter.Button(
            self.control_panel,
            text="STOP",
            font=utils.tk_font(),
            width=8, height=1,
            bg=c.COLOR_RED,
            fg=c.COLOR_WHITE,
            relief=tkc.FLAT,
            command=lambda: self.collect_stop()
        )
        self.pack(
        )
        self.control_panel.pack(
            pady=(10, 0)
        )
        self.group_playlist.pack(
            fill=tkc.X
        )
        self.label_playlist_path_entry.grid(
            row=0, column=0,
            padx=(0, 0), pady=(0, 5)
        )
        self.entry_playlist_path.grid(
            row=0, column=1,
            padx=(37, 0), pady=(0, 3)
        )
        self.browser_playlist_path.grid(
            row=0, column=2,
            padx=(0, 0), pady=(0, 5)
        )
        self.frame_links_top.pack(
            anchor=tkc.W,
            fill=tkc.X
        )
        self.group_collection.pack(
            fill=tkc.X,
            pady=(0, 0)
        )
        self.label_collection_path_entry.grid(
            row=0, column=0,
            padx=(0, 0), pady=(0, 5)
        )
        self.entry_collection_path.grid(
            row=0, column=1,
            padx=(7, 0), pady=(0, 3)
        )
        self.browser_collection_path.grid(
            row=0, column=2,
            padx=(0, 0), pady=(0, 5)
        )
        self.frame_links_bottom.pack(
            anchor=tkc.W,
            fill=tkc.X
        )
        self.label_clear_entries.pack(
            side=tkc.LEFT,
            padx=(0, 0), pady=(0, 0)
        )
        self.label_clear_console.pack(
            side=tkc.LEFT,
            padx=(0, 0), pady=(0, 0)
        )
        self.label_clear_all.pack(
            side=tkc.LEFT,
            padx=(10, 0), pady=(0, 0)
        )
        self.label_view_logs.pack(
            side=tkc.RIGHT,
            padx=(0, 0), pady=(0, 0)
        )
        self.group_console.pack(
            fill=tkc.X,
            padx=(0, 0), pady=(0, 0)
        )
        self.textbox_console_output = self.textbox_console_output.pack(
            fill=tkc.X,
            pady=(0, 5),padx=(5, 5)
        )
        self.frame_tools.pack(
            fill=tkc.X
        )
        self.scale_console_text.pack(
            side=tkc.LEFT,
            padx=(0, 0), pady=(0, 0)
        )
        self.progress_collection.pack(
            side=tkc.LEFT,
            padx=(10, 0), pady=(0, 0)
        )
        self.group_totals.pack(
            anchor=tkc.W,
            padx=(0, 0), pady=(5, 0)
        )
        self.frame_totals.pack(
        )
        self.label_media_success.pack(
            side=tkc.LEFT
        )
        self.label_value_media_success.pack(
            side=tkc.LEFT
        )
        self.label_media_failure.pack(
            side=tkc.LEFT
        )
        self.label_value_media_failure.pack(
            side=tkc.LEFT
        )
        self.label_media_total.pack(
            side=tkc.LEFT
        )
        self.label_value_media_total.pack(
            side=tkc.LEFT
        )
        self.btn_start.place(
            x=317, y=302
        )
        self.grid(
            column=0, row=1,
            pady=25
        )
        self.update()

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, value):
        self.__state = value

    @classmethod
    def verify_path_playlist(self, path):
        file_name, ext = os.path.splitext(path)
        return os.path.exists(path) and ext == '.wpl'

    @classmethod
    def verify_dir_collection(self, path):
        map_split = {
            'p': path.split('.'),
            'fs': path.split('/'),
            'bs': path.split('\\')
        }
        for split_type, splits in map_split.items():
            if split_type == "fs":
                map_split[split_type] = True if splits.count('') <= 1 else False
            else:
                map_split[split_type] = True if '' not in splits else False

        return os.path.isdir(path) and all(map_split.values())

    def console(self, msg, **kwargs):
        prefix = kwargs.get('prefix', ' >> ')
        end = kwargs.get('end', '\n')
        tag = kwargs.get('tag', "")
        tag_start = kwargs.get('tag_start', 'insert-1c')
        tag_end = kwargs.get('tag_end', 'insert lineend+1c')
        log = kwargs.get('log', True)

        now = "[{}]".format(datetime.now().strftime("%Y/%m/%d - %H:%M:%S"))
        self.textbox_console_output.tag_add(tag, tag_start, tag_end)
        self.textbox_console_output.config(state=tkc.NORMAL)
        self.textbox_console_output.insert(tkc.END, now + prefix + msg + end)
        self.textbox_console_output.tag_remove(tag, tag_start,tag_end)
        self.textbox_console_output.config(state=tkc.DISABLED)
        self.textbox_console_output.see(tkc.END)

        self.update_idletasks()

        if log:
            self.root.log_info(msg)

    def set_collection_entry(self, path):
        self.entry_collection_path.delete(0, tkc.END)
        self.entry_collection_path.insert(0, path)

    def set_playlist_entry(self, path):
        self.entry_playlist_path.delete(0, tkc.END)
        self.entry_playlist_path.insert(0, path)

    def set_console_text_size(self, event):
        self.textbox_console_output.config(
            font=utils.tk_font(size=self.var_console_text_size.get())
        )

    def set_tracked_entries_state(self, state=tkc.NORMAL):
        for _type, entry in self.map_tracked_entries.items():
            entry.get('widget').configure(state=state)
            entry.get('browser').configure(state=state)

    def on_done_collect_media(self):
        self.console("process stopped!") if self.state is c.STATE_STOPPED else None
        self.console("done!", tag=c.TAG_TEXT_GREEN)
        self.console("logs available @ %s" % settings.DIR_LOGS, tag=c.TAG_TEXT_ORANGE, log=False)
        self.set_links_visible()
        self.set_tracked_entries_state(state=tkc.NORMAL)
        self.state = c.STATE_READY

    def on_mousewheel(self, event):
        self.textbox_console_output.yview_scroll(int(-1*(event.delta/120)), 'units')

    def collect_media(self, path_playlist, dir_target):
        self.state = c.STATE_COLLECTING
        self.root.alert_action_info(
            self.root.get_tip(c.TIP_RANDOM),
            fg=c.COLOR_DARK_KNIGHT,
            font=utils.tk_font(size=10)
        )
        media_collector = Collector(self.root, path_playlist, dir_target)
        self.console(
            "copying media from: %s to: %s" %
            (media_collector.file_name_full, media_collector.dir_target),
            tag=c.TAG_TEXT_ORANGE
        )
        self.set_links_visible(False)
        media_collector.collect(callback=self.on_done_collect_media)

    def collect_stop(self):
        self.state = c.STATE_STOPPED

    def reset_progress(self):
        self.var_media_total.set(0)
        self.var_media_success_total.set(0)
        self.var_media_failure_total.set(0)
        self.set_progress_collection_attr(c.PB_SETTING_VALUE, 0)
        self.set_progress_collection_attr(c.PB_SETTING_MAXIMUM, 0)

    def clear_entries(self):
        for entry in self.map_tracked_entries.values():
            entry.get('widget').delete(0, tkc.END)
            entry.update(set=False)
            entry.update(last=None)

    def clear_console(self):
        self.textbox_console_output.config(state=tkc.NORMAL)
        self.textbox_console_output.delete('1.0', tkc.END)
        self.console("console cleared!")
        self.textbox_console_output.config(state=tkc.DISABLED)

    def clear_all(self):
        self.reset_progress()
        self.clear_entries()
        self.clear_console()

    def set_links_visible(self, visible=True):
        avail_links = [
            self.label_clear_entries,
            self.label_clear_console, self.label_clear_all
        ]
        for link in avail_links:
            link.pack_forget() \
            if not visible else \
            link.pack(
                side=tkc.LEFT
            )

    @classmethod
    def view_logs(self):
        subprocess.call(["explorer", settings.DIR_LOGS])

    def set_action_btn_by_state(self, state):
        map_action_btn = {
            c.STATE_READY: self.btn_start,
            c.STATE_COLLECTING: self.btn_stop,
        }
        if state in map_action_btn.keys():
            for btn_state, btn in map_action_btn.items():
                btn.place_forget() \
                    if not btn_state == state else \
                btn.place(x=317, y=302)

    def set_progress_collection_attr(self, attr, value):
        self.progress_collection[attr] = value

    def set_result_total(self, result, value):
        map_result = {
            c.RESULT_FAILURE: self.var_media_failure_total,
            c.RESULT_SUCCESS: self.var_media_success_total,
            c.RESULT_TOTAL: self.var_media_total
        }
        map_result[result].set(value)

    def track_path_entries(self):
        if not self.state in [c.STATE_COLLECTING, c.STATE_STOPPED]:

            is_set_playlist = self.map_tracked_entries['playlist'].get('set')
            is_set_collection = self.map_tracked_entries['collection'].get('set')

            for _type, entry in self.map_tracked_entries.items():
                widget = entry.get('widget')
                path = widget.get().strip()
                verified = entry.get('verified')(path)
                last = entry.get('last')
                browser = entry.get('browser')
                msg_path_state = '%s path verified @ "%s"'

                if verified:
                    widget.config(bg=c.COLOR_GREEN)
                    entry.update(set=True)
                    browser.config(text='Change')

                    if _type == 'playlist':
                        path_playlist = path
                        if last != path_playlist:
                            self.console(msg_path_state % (_type, path_playlist))
                            dir_playlist = os.path.dirname(path_playlist)
                            if not is_set_collection:
                                self.set_collection_entry(dir_playlist)
                            entry.update(last=path_playlist)
                            self.reset_progress()

                    elif _type == 'collection':
                        dir_collection = path
                        if last != dir_collection:
                            self.console(msg_path_state % (_type, dir_collection))
                            entry.update(last=dir_collection)

                    widget.xview_moveto(1)

                else:
                    widget.config(bg=c.COLOR_RED)
                    entry.update(set=False)
                    browser.config(text='Browse')

            if is_set_playlist and is_set_collection:
                if self.state != c.STATE_READY:
                    self.console("ready!", tag=c.TAG_TEXT_GREEN)
                    self.state = c.STATE_READY
            else:
                if self.state != c.STATE_NOT_READY:
                    self.console('not ready', tag=c.TAG_TEXT_RED)
                    self.state = c.STATE_NOT_READY

        self.after(100, self.track_path_entries)

    def track_collection_state(self):
        if self.state == c.STATE_NOT_READY:
            self.btn_start.config(
                bg=c.COLOR_DARK_KNIGHT,
                state=tkc.DISABLED
            )
            if not self.root.menu_viewing:
               self.root.alert_action_info(self.root.get_tip(c.TIP_BROWSE, format='%s'))

        elif self.state == c.STATE_READY:
            self.btn_start.config(
                bg=c.COLOR_GREEN,
                state=tkc.NORMAL
            )
            if not self.root.menu_viewing:
                self.root.alert_action_info(self.root.get_tip(c.TIP_START, format='%s'))

        elif self.state == c.STATE_COLLECTING:
            self.set_tracked_entries_state(state=tkc.DISABLED)
            self.btn_stop.config(
                bg=c.COLOR_RED,
                state=tkc.NORMAL
            )

        elif self.state == c.STATE_STOPPED:
            self.btn_stop.config(
                bg=c.COLOR_DARK_KNIGHT,
                state=tkc.DISABLED
            )

        self.set_action_btn_by_state(self.state)

        self.root.after(50, self.track_collection_state)

    def track_console_output(self):
        pass

    def on_start(self):
        self.track_collection_state()
        self.track_path_entries()
        self.track_console_output()


class RootFooterFrame(StyledFrame):
    def __init__(self, parent, **kwargs):
       StyledFrame.__init__(self, parent, **kwargs)

       self.init_ui()

    def init_ui(self):
        self.config(
            bg=c.COLOR_RED,
            height=40,
        )
        self.label_action_info = tkinter.Label(
            self,
            width=325,
            font=utils.tk_font(),
        )
        self.label_action_symbol = tkinter.Label(
            self,
            fg=c.COLOR_WHITE,
            bg=c.COLOR_BLUE,
            font=utils.tk_font(),
            height=40, width=6,
        )
        self.pack(
            side=tkc.BOTTOM,
            fill=tkc.X
        )

        self.refresh()

    def refresh(self):
        self.label_action_symbol.pack(
            in_=self,
            side=tkc.LEFT
        )
        self.label_action_info.pack(
            in_=self,
            side=tkc.LEFT,
            fill=tkc.BOTH
        )
        self.update()


class RootConfigureFrame(StyledMenuFrame):
    def __init__(self, parent, **kwargs):
        StyledMenuFrame.__init__(self, parent, **kwargs)

        self.var_show_tips = tkinter.BooleanVar()
        self.var_frame_drag_alpha = tkinter.DoubleVar()
        self.var_enable_logging = tkinter.BooleanVar()

        self.init_ui()

        self.map_tracked_entries = {
            'log': {
                'widget': self.entry_log_path,
                'verified': lambda path: self.verify_log_path(path),
                'set': False,
                'last': None,
                'browser': self.browser_log_path
            },
        }
        self.root.alert_action_info(
            "Configure Settings"
        )

        self.on_start()

    def init_ui(self):
        self.config(
            bg=c.COLOR_WHITE,
            width=self.w,
            height=self.h,
        )
        self.control_panel = StyledFrame(
            self,
            width=self.cp_w,
            height=self.cp_h,
            relief=tkc.RAISED,
        )
        self.group_settings = tkinter.LabelFrame(
            self.control_panel,
            font=utils.tk_font(size=10, weight=c.FONT_WEIGHT_BOLD),
            text="Configuration Settings",
        )
        self.checkbox_show_tips = tkinter.Checkbutton(
            self.group_settings,
            text="Show Tips",
            variable=self.var_show_tips,
        )
        self.frame_slider = tkinter.Frame(
            self.group_settings,
        )
        self.label_slider_alpha = tkinter.Label(
            self.frame_slider,
            text="Frame Drag Alpha :",
        )
        self.label_slider_alpha_value = tkinter.Label(
            self.frame_slider,
            textvariable=self.var_frame_drag_alpha,
        )
        self.scale_alpha = tkinter.Scale(
            self.frame_slider,
            from_=.3, to=1,
            resolution=0.1,
            orient=tkc.HORIZONTAL,
            showvalue=False,
            width=20,
            variable=self.var_frame_drag_alpha,
        )
        self.checkbox_enable_logging = tkinter.Checkbutton(
            self.group_settings,
            text="Enable Logging",
            variable=self.var_enable_logging,
        )
        self.frame_log = tkinter.Frame(
            self.group_settings,
        )
        self.label_log_path_entry = tkinter.Label(
            self.frame_log,
            text="Log File Path :",
        )
        self.entry_log_path = tkinter.Entry(
            self.frame_log,
            width=40,
        )
        self.browser_log_path = tkinter.Button(
            self.frame_log,
            text="Browse",
            width=6, height=1,
            relief=tkc.RAISED,
            command=lambda: self.root.browse_file(self.entry_log_path),
        )
        self.frame_button = tkinter.Frame(
            self.control_panel,
        )
        self.label_btn_exit = tkinter.Label(
            self.frame_button,
            text="SAVE AND",
            font=utils.tk_font(),
            width=10, height=1,
            relief=tkc.FLAT,
        )
        self.btn_exit = tkinter.Button(
            self.frame_button,
            text="EXIT",
            font=utils.tk_font(),
            width=6, height=1,
            bg=c.COLOR_RED,
            fg="white",
            relief=tkc.FLAT,
            command=self.kill,
        )
        self.pack(
            padx=(0, 0), pady=(50, 0),
        )
        self.control_panel.pack(
            padx=(0, 0), pady=(10, 0),
        )
        self.group_settings.pack(
            fill=tkc.BOTH,
            padx=(0, 0), pady=(0, 0),
        )
        self.checkbox_show_tips.grid(
            row=0, column=0,
            padx=(0, 0), pady=(0, 5),
            sticky=tkc.W,
        )
        self.frame_slider.grid(
            row=1, column=0,
            padx=(0, 0), pady=(0, 5),
            sticky=tkc.W,
        )
        self.label_slider_alpha.pack(
            side=tkc.LEFT,
            padx=(0, 0), pady=(0, 0),
        )
        self.label_slider_alpha_value.pack(
            side=tkc.LEFT,
            padx=(10, 0), pady=(0, 0),
        )
        self.scale_alpha.pack(
            side=tkc.LEFT,
            padx=(0, 0), pady=(0, 0),
        )
        self.checkbox_enable_logging.grid(
            row=2, column=0,
            padx=(0, 0), pady=(0, 5),
            sticky=tkc.W,
        )
        self.frame_log.grid(
            row=3, column=0,
            padx=(0, 0), pady=(0, 5),
            sticky=tkc.W,
        )
        self.label_log_path_entry.pack(
            side=tkc.LEFT,
            padx=(0, 0), pady=(0, 0),
        )
        self.entry_log_path.pack(
            side=tkc.LEFT,
            padx=(15, 0), pady=(0, 0),
        )
        self.browser_log_path.pack(
            side=tkc.LEFT,
            padx=(0, 0), pady=(0, 0),
        )
        self.frame_button.pack(
            side=tkc.BOTTOM,
            anchor=tkc.E,
            padx=(0, 0), pady=(0, 0),
        )
        self.btn_exit.pack(
            side=tkc.RIGHT,
            padx=(0, 0), pady=(0, 0),
        )
        self.label_btn_exit.pack(
            side=tkc.RIGHT,
            padx=(0, 0), pady=(0, 0),
        )

        self.update()

    def track_path_entries(self):
        for _type, entry in self.map_tracked_entries.items():
            widget = entry.get('widget')
            path = widget.get().strip()
            verified = entry.get('verified')(path)
            last = entry.get('last')
            browser = entry.get('browser')
            msg_path_state = '%s path verified @ "%s"'

            if _type == 'log':
                if self.var_enable_logging.get():
                    log_browser_state = log_entry_state = log_label_state = tkc.NORMAL
                else:
                    log_browser_state = log_entry_state = log_label_state = tkc.DISABLED

                widget.config(
                    state=log_entry_state
                )
                browser.config(
                    state=log_browser_state
                )
                self.label_log_path_entry.config(
                    state=log_label_state
                )
            if verified:
                widget.config(bg=c.COLOR_GREEN)
                entry.update(set=True)
                browser.config(text='Change')
                if last != path:
                    self.root.log_info(msg_path_state % (_type, path))
                    entry.update(last=path)
                widget.xview_moveto(1)
            else:
                widget.config(bg=c.COLOR_RED)
                entry.update(set=False)
                browser.config(text='Browse')

        self.after(100, self.track_path_entries)

    @classmethod
    def verify_log_path(self, path):
        file_name, ext = os.path.splitext(path)
        return os.path.exists(path) and ext == '.log'

    def apply_config(self, config_settings):
        setting_show_tips = config_settings.get('General', 'ShowTips')
        setting_frame_drag_alpha = config_settings.get('Visual', 'FrameDragAlpha')
        setting_enable_logging = config_settings.get('Logging', 'EnableLogging')
        setting_logfile_path = config_settings.get('Logging', 'LogFilePath')

        self.var_show_tips.set(setting_show_tips)
        self.var_frame_drag_alpha.set(setting_frame_drag_alpha)
        self.var_enable_logging.set(setting_enable_logging)
        self.entry_log_path.insert(0, setting_logfile_path)

    def on_start(self):
        self.apply_config(self.root.config_settings)
        self.track_path_entries()

    def kill(self):
        setting_show_tips = self.var_show_tips.get()
        setting_frame_drag_alpha = self.var_frame_drag_alpha.get()
        setting_enable_logging = self.var_enable_logging.get()
        setting_logfile_path = self.map_tracked_entries.get('log').get('last')

        self.root.set_config('General', 'ShowTips', str(setting_show_tips))
        self.root.set_config('Visual', 'FrameDragAlpha', str(setting_frame_drag_alpha))
        self.root.set_config('Logging', 'EnableLogging', str(setting_enable_logging))
        self.root.set_config('Logging', 'LogFilePath', setting_logfile_path)

        self.root.save_config()

        self.root.menu_viewing=None
        self.after_cancel(self.track_path_entries)
        self.root.log_info('configure settings saved!')

        self.destroy()


class RootTutorialFrame(StyledMenuFrame):
    def __init__(self, parent, **kwargs):
        StyledMenuFrame.__init__(self, parent, **kwargs)

        self.init_ui()

    def init_ui(self):
        self.config(
            bg=c.COLOR_WHITE,
            width=self.w,
            height=self.h,
        )
        self.control_panel = StyledFrame(
            self,
            width=self.cp_w,
            height=self.cp_h,
            relief=tkc.RAISED
        )
        self.frame_button = tkinter.Frame(
            self.control_panel
        )
        self.btn_exit = tkinter.Button(
            self.frame_button,
            text="EXIT",
            font=utils.tk_font(),
            width=6, height=1,
            bg=c.COLOR_RED,
            fg="white",
            relief=tkc.FLAT,
            command=self.kill
        )
        self.pack(
            padx=(0, 0), pady=(50, 0)
        )
        self.control_panel.pack(
            padx=(0, 0), pady=(10, 0)
        )
        self.frame_button.pack(
            side=tkc.BOTTOM,
            anchor=tkc.E
        )
        self.btn_exit.pack(
            side=tkc.RIGHT
        )
        self.update()

    def kill(self):
        self.root.menu_viewing=None
        self.destroy()