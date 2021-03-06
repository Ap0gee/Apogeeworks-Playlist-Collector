__author__ = 'Apogee'

import tkinter
from tkinter import ttk
from tkinter import Tk
from tkinter import filedialog
import constants as c
import tkinter.constants as tkc
import utils
import os
import sys


if hasattr(sys, 'frozen'):
    DIR_BASE = os.path.abspath(os.path.dirname(sys.executable))
else:
    DIR_BASE = os.path.abspath(os.path.dirname(__file__))

DIR_ASSETS = os.path.join(DIR_BASE, 'assets')
DIR_IMAGES = os.path.join(DIR_ASSETS, 'images')
DIR_CURSORS = os.path.join(DIR_ASSETS, 'cursors')


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

    def init_ui(self):
        pass


class RootFrame(Tk):
    def __init__(self, parent, **kwargs):
        Tk.__init__(self, **kwargs)

        self.overrideredirect(True)
        self.resizable(False, False)
        self.propagate(False)

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.attributes('-topmost', False)

        self.busy = False
        self.in_menu = False
        self.btn_hover = False

        self.config_data = {}
        self.map_var_config = {}

        self.config_type_map = {
            'b': lambda x: int(x),
            'i': lambda x: int(x),
            'f': lambda x: float(x),
            's': lambda x: str(x).strip(),
        }

        self.w, self.h = 425, 350

        self.parent = parent
        self.init_ui()

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
        self.update()

        #self.splash = RootSplashFrame(self)
        self.main_frame = RootMainFrame(self)
        self.tool_frame = RootToolFrame(self)
        self.menu_frame = RootMenuFrame(self)
        #self.footer_frame = RootFooterFrame(self)
        #self.control_frame = RootViewControlFrame(self)

        self.bind(
            "<Map>", self.bind_redirect
        )

        #self.bind_all("<Key>", self.track_keys)
        self.bind_all("<Control-l>", self.track_keys)
        self.bind_all("<Control-e>", self.track_keys)
        self.bind_all("<Control-k>", self.track_keys)
        self.bind_all("<Control-d>", self.track_keys)
        self.bind_all("<Control-m>", self.track_keys)
        self.bind_all("<Control-n>", self.track_keys)
        self.bind_all("<Control-s>", self.track_keys)
        self.bind_all("<Alt-i>", self.track_keys)
        self.bind_all("<Alt-x>", self.track_keys)
        self.bind_all("<Alt-q>", self.track_keys)

        self.key_map = {
        #     76: self.menu_frame.viewLoadGroup, #"<Control-l>"
        #     75: self.menu_frame.askClearGroup, #"<Control-k>"
        #     69: self.menu_frame.viewEditGroup, #"<Control-e>"
        #     68: self.menu_frame.askDeleteGroup, #"<Control-d>"
        #     78: self.menu_frame.viewNewGroup, #"<Control-n>"
        #     77: self.menu_frame.viewDeleteMultipleGroup, #"<Control-m>"
        #     83: self.summoned, #"<Control-s>"
        #     73: self.destroy, #"<Alt-i>"
        #     88: self.destroy, #"<Alt-x>"
            81: self.destroy, #"<Alt-q>"
        }

        self.update()

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

    def kill_splash(self):
        self.update()
        self.update_idletasks()
        self.splash.destroy()

    def track_cursor(self):
        if not self.busy:
            cursor_x, cursor_y = self.winfo_pointerxy()

    def track_keys(self, event):
        if not self.busy:
            self.key_map[event.keycode]()

    def track_events(self):
        self.after(50, self.track_events)


class RootToolFrame(StyledFrame):
    def __init__(self, parent, **kwargs):
        StyledFrame.__init__(self, parent, **kwargs)

        self.dragging_parent = False
        self.init_ui()

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
            command=self.parent.minimize
        )
        self.btn_close = tkinter.Button(
            self,
            text=c.UNICODE_BTN_CLOSE,
            font=utils.tk_font(size=20),
            background=c.COLOR_RED,
            fg=c.COLOR_WHITE,
            width=2,
            relief=tkc.FLAT,
            command=self.parent.destroy
        )

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

        self.parent.geometry("+%s+%s" % (new_x, new_y))


class RootMenuFrame(StyledFrame):
    def __init__(self, parent, **kwargs):
       StyledFrame.__init__(self, parent, **kwargs)
       self.init_ui()

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
        file_menu = tkinter.Menu(
            self.menu_file,
            tearoff=0
        )
        self.menu_file['menu'] = file_menu

        options_menu = tkinter.Menu(
            self.menu_options,
            tearoff=0
        )
        self.menu_options['menu'] = options_menu

        file_menu.add_command(
            label="{0}{1}{2}".format("Quit", " "*8, "(Alt + Q)"),
            command=self.parent.destroy
        )
        options_menu.add_command(
            label="Configure...",
            command=self.view_menu_config()
        )
        options_menu.add_separator()
        options_menu.add_command(
            label="View Tutorial...",
            command=self.view_menu_tutorial()
        )
        file_menu.bind("<<MenuSelect>>", self.menu_select_callback)

        self.update()

    def menu_select_callback(self, event):
        pass
        #self.root.busy = True

    def view_menu_config(self):
        pass
        #RootConfigureFrame(self.root)

    def view_menu_tutorial(self):
        pass


class RootMainFrame(StyledFrame):
    def __init__(self, parent, **kwargs):
        StyledFrame.__init__(self, parent, **kwargs)

        self.init_ui()

    def init_ui(self):
        self.config(
            bg=c.COLOR_WHITE,
            width=self.root.winfo_width(),
            height=self.root.winfo_height()
        )
        self.control_panel = StyledFrame(
            self,
            width=400,
            height=263,
            relief=tkc.RAISED
        )
        self.group_playlist = tkinter.LabelFrame(
            self.control_panel,
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
        #TODO: change default path
        self.entry_collection_path.insert(0, "Path/to/default/dir/here")

        self.browser_playlist_path= tkinter.Button(
            self.group_playlist,
            text="Browse",
            width=6, height=1,
            relief=tkc.RAISED,
            command=lambda: self.open_file(self.entry_playlist_path)
        )
        self.browser_collection_path = tkinter.Button(
            self.group_collection,
            text="Change",
            width=6, height=1,
            relief=tkc.RAISED,
            command=lambda: self.open_directory(self.entry_collection_path)
        )
        self.btn_close_label = tkinter.Label(
            self.control_panel,
            text="",
            font=utils.tk_font(),
            width=10, height=1,
            bg=c.COLOR_LIGHT_GREY,
            relief=tkc.FLAT,
        )
        self.btn_close = tkinter.Button(
            self.control_panel,
            text="START",
            font=utils.tk_font(),
            width=6, height=1,
            bg=c.COLOR_GREEN,
            fg=c.COLOR_WHITE,
            relief=tkc.FLAT,
            command=None
        )
        self.pack(
            pady=(25, 0)
        )
        self.control_panel.pack(
            pady=(11, 0)
        )

        self.group_playlist.pack(fill=tkc.X)
        self.label_playlist_path_entry.grid(row=0, column=0)
        self.entry_playlist_path.grid(row=0, column=1, padx=(37, 0), pady=(0, 5))
        self.browser_playlist_path.grid(row=0, column=2, padx=(0, 0), pady=(0, 5))

        self.group_collection.pack(fill=tkc.X)
        self.label_collection_path_entry.grid(row=0, column=0)
        self.entry_collection_path.grid(row=0, column=1, padx=(7, 0), pady=(0, 5))
        self.browser_collection_path.grid(row=0, column=2, padx=(0, 0), pady=(0, 5))

        self.btn_close.place(
            x=335, y=231
        )
        self.btn_close_label.place(
            x=240, y=235
        )
        self.grid(
            column=0, row=1,
            pady=27
        )

        self.track_path_entries()
        self.update()

    def open_file(self, tk_entry):
        path = filedialog.askopenfilename()

        if not path is "":
            tk_entry.delete(0, tkc.END)
            tk_entry.insert(0, path)

    def open_directory(self, tk_entry):
        path = filedialog.askdirectory()

        if not path is "":
            tk_entry.delete(0, tkc.END)
            tk_entry.insert(0, path)

    def verify_path_playlist(self, path):
        file_name, ext = os.path.splitext(path)
        return os.path.exists(path) and ext == '.wpl'

    def track_path_entries(self):
        map_tracked_entries = {
            'directories': [
                self.entry_collection_path
            ],
            'playlists': [
                self.entry_playlist_path
            ]
        }
        map_path_verifications = {
            'directories': lambda path: os.path.isdir(path),
            'playlists': lambda path: self.verify_path_playlist(path)
        }

        try:
            for _type, entry_list in map_tracked_entries.items():
                path_verified = map_path_verifications[_type]
                for entry in entry_list:
                    if path_verified(entry.get()):
                        entry.config(bg=c.COLOR_GREEN)
                    else:
                        entry.config(bg=c.COLOR_RED)

            self.root.after(10, self.track_path_entries)
        except Exception as e:
            print(e)
            #TODO: add error message in footer rather than close
            self.root.after_cancel(self.track_path_entries)
