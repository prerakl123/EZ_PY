# importing modules
from tkinter import *
import tkinter.ttk as ttk
import json
import tkinter.messagebox as tk_mb
import tkinter.filedialog as tk_fd
# importing console, theme window, *.md reader, and Python Editor
from MDText import MDText
from HandyConsole import Console as TextConsole
from ColorText import ColorText
from ThemeSelection import ThemeWin
from Tooltip import ToolTip
from idlelib.parenmatch import *
from ttkthemes import ThemedTk


# json configuration file
with open('config.json') as file:
    config_dict = json.load(file)


class CustomNotebook(ttk.Notebook):
    """Customized tkinter.ttk.Notebook"""
    __initialized = False

    def __init__(self, *args, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__inititialized = True

        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None
        self.tab_frame = None
        self.py_files = []      # list for python files (or any file) opened using ColorText
        self.consoles = []      # list for differnet consoles opened
        self.files = []         # list for files opened as normal text
        self.md_files = []      # list for files opened as MarkDown file

        # with open('importable_modules', 'w') as imp_mods:
        #     for i in ColorText.module_list:
        #         imp_mods.write(i+'\n')

        # binding key events

        self.enable_traversal()
        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)
        self.bind('<Control-O>', self.open_file)
        self.bind('<Control-o>', self.open_file)
        self.bind('<Control-F4>', lambda event: [self.on_close_press(event), self.on_close_release(event)])
        self.bind('<Control-W>', self.on_cw_close)
        self.bind('<Control-w>', self.on_cw_close)

    def on_cw_close(self, event):
        self.event_generate('<<NotebookTabClosed>>')

    def close(self, event):
        """Closes the notebook tab on position (x, y) of
        CustomNotebook widget"""
        element = self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))
        self.forget(index)
        self.event_generate("<<NotebookTabClosed>>")

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index

    def on_close_release(self, event):
        """Called when the button is released over the close button"""
        if not self.instate(['pressed']):
            return

        element = self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))

        if "close" in element and self._active == index:
            self.forget(index)
            self.event_generate("<<NotebookTabClosed>>")

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self):
        """Function for creating the close button"""
        style = ttk.Style()
        self.images = (
            PhotoImage("img_close", data='''
            R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
            d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
            5kEJADs=
            '''),
            PhotoImage("img_closeactive", data='''
            R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
            AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
            '''),
            PhotoImage("img_closepressed", data='''
            R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
            d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
            5kEJADs=
        '''))

        style.element_create("close", "image", "img_close",
                             ("active", "pressed", "!disabled", "img_closepressed"),
                             ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [("CustomNotebook.tab", {"sticky": "nswe", "children": [
            ("CustomNotebook.padding", {"side": "top", "sticky": "nswe", "children": [("CustomNotebook.focus", {
                "side": "top",
                "sticky": "nswe",
                "children": [("CustomNotebook.label", {"side": "left", "sticky": ''}),
                             ("CustomNotebook.close", {"side": "left", "sticky": ''})
                             ]
            })
                                                                                      ]
                                        }
             )]})]
                     )

    def add_py_tab(self, event=None, _file=None, _file_name=None):
        """Adds a ColorTextTab Frame to CustomNotebook.
        '_file' and '_file_name' are for content of file and name of file
        if opened from openfiledialog"""
        
        ctt = ColorTextTab(master=self, bd=1, highlightthickness=1, highlightbackground='black')

        if _file is not None:
            fn = _file_name.rsplit('/')[-1]

            ctt.pack(side=TOP, fill=BOTH, expand=YES)
            ctt.colortext.insert(END, _file)
            ctt.colortext.inst_trigger()

            PyMenuBar(self, ctt.colortext)
            
            self.py_files.append(1)
            self.add(ctt, text=fn)
        else:
            def dragwin(evt):
                x = new_win.winfo_pointerx() - _offsetx
                y = new_win.winfo_pointery() - _offsety
                new_win.geometry('+{x}+{y}'.format(x=x, y=y))

            def clickwin(evt):
                nonlocal _offsetx, _offsety
                _offsetx = evt.x + evt.widget.winfo_rootx() - new_win.winfo_rootx()
                _offsety = evt.y + evt.widget.winfo_rooty() - new_win.winfo_rooty()

            def ok():
                fn2 = name_entry.get()
                ctt.pack(side=TOP, fill=BOTH, expand=YES)
                PyMenuBar(self, ctt.colortext)
                self.py_files.append(1)
                self.create_file(fn2)
                self.add(ctt, text=fn2)
                new_win.destroy()

            def cancel(evt=None):
                new_win.destroy()
                self.select_new_tab()

            new_win = Toplevel(self.master, bg='gray84')
            new_win.geometry(f'200x110+{int(new_win.winfo_screenheight()*0.25)}+'
                             f'{int(new_win.winfo_screenwidth()*0.16)}')
            new_win.overrideredirect(True)

            _offsetx = 0
            _offsety = 0

            new_win.bind('<Button-1>', clickwin)
            new_win.bind('<B1-Motion>', dragwin)
            new_win.bind('<Escape>', cancel)

            name_entry = Entry(new_win, font='Consolas 12')
            name_entry.pack(side=TOP, fill=X, ipady=5)
            name_entry.bind('<FocusIn>', lambda _: ToolTip(name_entry, 'Consolas 13', 'File name with extension.',
                                                           follow=False))

            ok_btn = Button(new_win, font='Consolas 10', text='OK', bd=0, width=10, command=ok)
            ok_btn.pack(side=LEFT, padx=10)

            cancel_btn = Button(new_win, font='Conoslas 10', text='Cancel', bd=0, width=10, command=cancel)
            cancel_btn.pack(side=RIGHT, padx=10)

            new_win.attributes('-topmost', True)
            new_win.mainloop()

    def add_file_tab(self, event=None, _file=None, _file_name=None):
        """Adds a FileTab Frame to CustomNotebook.
        '_file' and '_file_name' are for content of file and name of file
        if opened from openfiledialog"""
        ft = FileTab(master=self, bd=1, highlightthickness=1, highlightbackground='black')

        if _file is not None:
            fn = _file_name.rsplit('/')[-1]
            ft.file.insert(END, _file)
        
        fn = f'Text File {len(self.files)+1}'
        ft.pack(side=TOP, expand=YES, fill=BOTH)

        self.files.append(1)

        MenuBar(self, ft.file)

        self.add(ft, text=fn)

    def create_file(self, _file_name):
        try:
            with open(_file_name, 'w', encoding='utf-8') as the_file:
                the_file.write('')
                the_file.close()

        except IOError:
            tk_mb.showwarning("Save", "Could not save the file.")

    def add_console_tab(self, event=None):
        """Opens a new TextConsole tab in CustomNotebook"""

        tab_frame = Frame(self.master, highlightthickness=1, highlightbackground='black')
        self.add(tab_frame, text=f'Console {len(self.consoles)+1}')

        tab = TextConsole(tab_frame)
        tab.pack(side=TOP, expand=YES, fill=BOTH)

        self.consoles.append(1)

    def open_file(self, event=None):
        input_file_name = tk_fd.askopenfile(defaultextension="*.*", filetypes=ColorText.FILETYPES)

        if input_file_name:
            file_name = input_file_name.name

            with open(file_name, encoding='utf-8') as _file:
                try:
                    if input_file_name.name.endswith('.py'):
                        self.add_py_tab(_file=_file.read(), _file_name=file_name)
                    elif input_file_name.name.endswith('.md'):
                        self.add_md(_file=_file.read(), _file_name=file_name)
                    else:
                        self.add_file_tab(_file=_file.read(), _file_name=file_name)

                except UnicodeError or UnicodeTranslateError or UnicodeDecodeError or UnicodeEncodeError or\
                        UnicodeWarning:
                    tk_mb.showerror('Can\'t open file', 'This error could be due to images in a file or some'
                                                        ' characters that the program is unable to read')

    def add_md(self, event=None, _file=None, _file_name=None):
        """Adds a MDText Frame to CustomNotebook.
        '_file' and '_file_name' are for content of file and name of file
        if opened from openfiledialog"""

        fn = f'MD Text File {len(self.md_files)+1}'
        tab = MDText(master=self, bd=1, highlightthickness=1, highlightbackground='black')
        tab.pack(side=TOP, expand=True, fill=BOTH)

        self.md_files.append(1)

        if _file is not None:
            fn = _file_name.rsplit('/')[-1]
            tab.inputeditor.insert(END, _file)

        self.add(tab, text=fn)

    def select_new_tab(self, event=None):
        """Opens a window for selection of opening of new window"""
        self.update()

        def dragwin(evt):
            x = sf_root.winfo_pointerx() - _offsetx
            y = sf_root.winfo_pointery() - _offsety
            sf_root.geometry('+{x}+{y}'.format(x=x, y=y))

        def clickwin(evt):
            nonlocal _offsetx, _offsety
            _offsetx = evt.x + evt.widget.winfo_rootx() - sf_root.winfo_rootx()
            _offsety = evt.y + evt.widget.winfo_rooty() - sf_root.winfo_rooty()

        sf_root = Toplevel(self.master, bg='gray84')
        sf_root.geometry(f'200x130+{int(sf_root.winfo_screenheight()*0.25)}+'
                         f'{int(sf_root.winfo_screenwidth()*0.16)}')
        sf_root.overrideredirect(True)
        _offsetx = 0
        _offsety = 0
        
        sf_root_top_frame = Frame(sf_root, bg='gray75')
        sf_root_top_frame.pack(side=TOP, anchor=N, fill=X)

        sf_root_top_frame.bind('<Button-1>', clickwin)
        sf_root_top_frame.bind('<B1-Motion>', dragwin)

        sf_root_name = Label(sf_root_top_frame, text='Create File', font='Consolas 11', anchor=CENTER, bg='gray75',
                             width=11)
        sf_root_name.pack(side=LEFT, anchor=W)
        sf_root_name.bind('<Button-1>', clickwin)
        sf_root_name.bind('<B1-Motion>', dragwin)

        exit_lbl = Label(sf_root_top_frame, text='✕', font='Consolas 12', anchor=CENTER, bg='gray75', width=2)
        exit_lbl.pack(side=LEFT, expand=YES, anchor=E, ipadx=10)
        exit_lbl.bind('<ButtonRelease-1>', lambda a: sf_root.destroy())
        exit_lbl.bind('<Enter>', lambda a: exit_lbl.config(fg='white', bg='red'))
        exit_lbl.bind('<Leave>', lambda a: exit_lbl.config(fg='black', bg='gray75'))

        py_lbl = Label(sf_root, text='+ Py File', font='Consolas 13', bg='gray84', cursor='hand2',
                       width=15)
        py_lbl.pack(side=TOP)
        py_lbl.bind('<ButtonRelease-1>', lambda _=None: [self.add_py_tab(_), sf_root.destroy()])
        py_lbl.bind('<Enter>', lambda a: py_lbl.config(fg='orange', bg='light blue'))
        py_lbl.bind('<Leave>', lambda a: py_lbl.config(fg='black', bg='gray84'))

        console_lbl = Label(sf_root, text='+ New Console', font='Consolas 13', bg='gray84', cursor='hand2',
                            width=15)
        console_lbl.pack(side=TOP)
        console_lbl.bind('<ButtonRelease-1>', lambda _=None: [self.add_console_tab(), sf_root.destroy()])
        console_lbl.bind('<Enter>', lambda a: console_lbl.config(fg='orange', bg='light blue'))
        console_lbl.bind('<Leave>', lambda a: console_lbl.config(fg='black', bg='gray84'))

        txt_lbl = Label(sf_root, text='+ Text File', font=('Consolas 13'), bg='gray84', cursor='hand2',
                        width=15)
        txt_lbl.pack(side=TOP)
        txt_lbl.bind('<ButtonRelease-1>', lambda _=None: [self.add_file_tab(_), sf_root.destroy()])
        txt_lbl.bind('<Enter>', lambda a: txt_lbl.config(fg='orange', bg='light blue'))
        txt_lbl.bind('<Leave>', lambda a: txt_lbl.config(fg='black', bg='gray84'))

        md_lbl = Label(sf_root, text='+ README.md', font='Consolas 13', bg='gray84', cursor='hand2',
                       width=15)
        md_lbl.pack(side=TOP)
        md_lbl.bind('<ButtonRelease-1>', lambda _=None: [self.add_md(_), sf_root.destroy()])
        md_lbl.bind('<Enter>', lambda a: md_lbl.config(fg='orange', bg='light blue'))
        md_lbl.bind('<Leave>', lambda a: md_lbl.config(fg='black', bg='gray84'))

        sf_root.bind('<KeyPress-Escape>', lambda a: exit_lbl.config(fg='white', bg='red'))
        sf_root.bind('<KeyRelease-Escape>', lambda a: sf_root.destroy())
        sf_root.bind('<FocusOut>', lambda a=None: sf_root.destroy())
        sf_root.wm_attributes('-topmost', 1)
        sf_root.focus_force()


class ColorTextTab(Frame):
    file_name = None

    def __init__(self, **kwargs):
        Frame.__init__(self, **kwargs)
        v_scroll = Scrollbar(self, orient=VERTICAL)
        h_scroll = Scrollbar(self, orient=HORIZONTAL)
        self.colortext = ColorText(master=self, yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set,
                                   wrap=NONE, undo=True)
        v_scroll.pack(side=RIGHT, fill=Y)
        v_scroll.config(command=self.colortext.yview)
        self.colortext.pack(side=TOP, expand=YES, fill=BOTH)
        h_scroll.pack(side=BOTTOM, fill=X)
        h_scroll.config(command=self.colortext.xview)
        self.bind('<Control-o>', self.open_file)
        self.bind('<Control-O>', self.open_file)
        self.bind('<Control-S>', self.save)
        self.bind('<Control-s>', self.save)
        self.bind('<Control-Shift-S>', self.save_as)
        self.bind('<Control-Shift-s>', self.save_as)
        self.bind('<Control-R>', self.redo_event)
        self.bind('<Control-r>', self.redo_event)
        self.bind('<Control-Z>', self.undo_event)
        self.bind('<Control-z>', self.undo_event)

    def new_file(self, event=None):
        self.master.add_py_tab()

    def open_file(self, event=None):
        input_file_name = tk_fd.askopenfile(defaultextension=".py", filetypes=ColorText.FILETYPES)
        if input_file_name:
            self.file_name = input_file_name.name
            self.colortext.delete(1.0, END)
            with open(self.file_name, encoding='utf-8') as _file:
                try:
                    self.colortext.insert(1.0, _file.read())
                    self.file_name = input_file_name.name
                except UnicodeError or UnicodeTranslateError or UnicodeDecodeError or UnicodeEncodeError or\
                        UnicodeWarning:
                    tk_mb.showerror('Can\'t open file', 'This error could be due to images in a file or some'
                                                        ' characters that the program is unable to read')

    def write_to_file(self, _file_name):
        try:
            content = self.colortext.get(1.0, 'end')
            with open(_file_name, 'w') as the_file:
                the_file.write(content)
        except IOError:
            tk_mb.showwarning("Save", "Could not save the file.")


    def save_as(self, event=None):
        input_file_name = tk_fd.asksaveasfile(defaultextension=".py", filetypes=ColorText.FILETYPES)
        if input_file_name:
            self.file_name = input_file_name.name
            self.write_to_file(self.file_name)
        return "break"

    def save(self, event=None):
        if not self.file_name:
            self.save_as()
        else:
            self.write_to_file(self.file_name)
        return "break"

    def undo_event(self, event=None):
        self.colortext.event_generate('<<Undo>>')
        self.colortext.edit_undo()

    def redo_event(self, event=None):
        self.colortext.event_generate('<<Redo>>')
        self.colortext.edit_redo()


class FileTab(Frame):
    file_name = None

    def __init__(self, **kwargs):
        Frame.__init__(self, **kwargs)
        v_scroll = Scrollbar(self, orient=VERTICAL)
        self.file = Text(self, wrap=WORD, font=('Consolas', 12), yscrollcommand=v_scroll.set, undo=True)
        v_scroll.pack(side=RIGHT, fill=Y)
        v_scroll.config(command=self.file.yview)
        self.file.pack(side=TOP, expand=YES, fill=BOTH)
        self.bind('<Control-o>', self.open_file)
        self.bind('<Control-O>', self.open_file)
        self.bind('<Control-S>', self.save)
        self.bind('<Control-s>', self.save)
        self.bind('<Control-Shift-S>', self.save_as)
        self.bind('<Control-Shift-s>', self.save_as)
        self.bind('<Control-R>', self.redo_event)
        self.bind('<Control-r>', self.redo_event)
        self.bind('<Control-Z>', self.undo_event)
        self.bind('<Control-z>', self.undo_event)

    def new_file(self, event=None):
        self.master.add_file_tab()

    def open_file(self, event=None):
        input_file_name = tk_fd.askopenfile(defaultextension=".py", filetypes=ColorText.FILETYPES)
        if input_file_name:
            self.file_name = input_file_name.name
            self.file.delete(1.0, END)
            with open(self.file_name, encoding='utf-8') as _file:
                try:
                    self.file.insert(1.0, _file.read())
                    self.file_name = input_file_name.name
                except UnicodeError or UnicodeTranslateError or UnicodeDecodeError or UnicodeEncodeError or\
                        UnicodeWarning:
                    tk_mb.showerror('Can\'t open file', 'This error could be due to images in a file or some'
                                                        ' characters that the program is unable to read')

    def write_to_file(self, _file_name):
        try:
            content = self.file.get(1.0, 'end')
            with open(_file_name, 'w') as the_file:
                the_file.write(content)
        except IOError:
            tk_mb.showwarning("Save", "Could not save the file.")


    def save_as(self, event=None):
        input_file_name = tk_fd.asksaveasfile(defaultextension=".py", filetypes=ColorText.FILETYPES)
        if input_file_name:
            self.file_name = input_file_name.name
            self.write_to_file(self.file_name)
        return "break"

    def save(self, event=None):
        if not self.file_name:
            self.save_as()
        else:
            self.write_to_file(self.file_name)
        return "break"

    def find_text(self, event=None):
        search_toplevel = Toplevel(self.master)
        search_toplevel.title('Find Text')
        search_toplevel.transient(self.master)

        Label(search_toplevel, text="Find All:").grid(row=0, column=0, sticky='e')

        search_entry_widget = Entry(search_toplevel, width=35)
        search_entry_widget.grid(row=0, column=1, padx=2, pady=2, sticky='we')
        search_entry_widget.focus_set()
        ignore_case_value, regex_value = IntVar(), IntVar()
        Checkbutton(search_toplevel, text='Ignore Case', variable=ignore_case_value).grid(row=1, column=1, sticky=W,
                                                                                          padx=1,
                                                                                          pady=2)
        Checkbutton(search_toplevel, text='Regular Expression', variable=regex_value).grid(row=1, column=1, sticky=E,
                                                                                           padx=2, pady=2)
        Button(search_toplevel, text="Find All", underline=0,
               command=lambda: self.search_output(search_entry_widget.get(), ignore_case_value.get(), self.file,
                                                  search_toplevel, search_entry_widget, regex_value.get())).grid(
            row=0, column=2, sticky=E + W, padx=2, pady=2)

        def close_search_window(_event=None):
            self.file.tag_remove('match', '1.0', END)
            search_toplevel.destroy()

        search_toplevel.bind('<Escape>', close_search_window)
        search_toplevel.protocol('WM_DELETE_WINDOW', close_search_window)
        return "break"

    def search_output(self, needle, if_ignore_case, _text, search_toplevel, search_box, regex):
        _text.tag_remove('match', '1.0', END)
        matches_found = 0
        if needle:
            start_pos = '1.0'
            while True:
                start_pos = _text.search(needle, start_pos, nocase=if_ignore_case, stopindex=END, regexp=regex)
                if not start_pos:
                    break
                end_pos = '{}+{}c'.format(start_pos, len(needle))
                _text.tag_add('match', start_pos, end_pos)
                matches_found += 1
                start_pos = end_pos
            _text.tag_config('match', foreground='red', background='yellow')
        search_box.focus_set()
        search_toplevel.title('{} matches found'.format(matches_found))

    def _replace(self, event=None):
        replace_toplevel = Toplevel(self.master)
        replace_toplevel.title('Find and Replace Text')
        replace_toplevel.transient(self.master)
        replace_toplevel.resizable(False, False)

        Label(replace_toplevel, text="Find:", font=('Consolas 9')).grid(row=0, column=0, sticky=W, padx=2, pady=2)
        find_entry = Entry(replace_toplevel, width=40, font=('Consolas 12'))
        find_entry.grid(row=1, column=0, sticky=W, padx=2, pady=2)
        find_entry.focus_set()
        Label(replace_toplevel, text='Replace:', font=('Consolas 9')).grid(row=2, column=0, sticky=W, padx=2, pady=2)
        replace_entry = Entry(replace_toplevel, width=40, font=('Consolas 12'))
        replace_entry.grid(row=3, column=0, sticky=W, padx=2, pady=2)

        ignore_case_value, regex_value = IntVar(), IntVar()
        Checkbutton(replace_toplevel, text='Ignore Case', variable=ignore_case_value).grid(row=4, column=0, padx=2,
                                                                                           pady=2, sticky=W)
        Checkbutton(replace_toplevel, text='Regular Expression', variable=regex_value).grid(row=4, column=0, padx=2,
                                                                                            pady=2, sticky=E)
        Button(replace_toplevel, text='Find All',
               command=lambda: self.search_output(find_entry.get(), ignore_case_value.get(), self.file,
                                                  replace_toplevel, find_entry, regex_value.get()),
               width=12).grid(row=1, column=1, padx=2, pady=2, sticky=E)
        Button(replace_toplevel, text='Replace All',
               command=lambda: self.replace_output(find_entry.get(), replace_entry.get(), self.file,
                                                   ignore_case_value.get(), replace_toplevel, regex_value.get()),
               width=12).grid(row=2, column=1, padx=2, pady=2, sticky=E)

        def close_search_window(_event=None):
            replace_toplevel.destroy()
            self.file.tag_remove('match', '1.0', END)

        replace_toplevel.bind('<Escape>', close_search_window)
        replace_toplevel.bind('<Return>', lambda: self.replace_output(find_entry.get(), replace_entry.get(), self.file,
                                                                      ignore_case_value.get(), replace_toplevel,
                                                                      regex_value.get()))
        replace_toplevel.bind('<Shift-Return>', lambda a: self.search_output(find_entry.get(), ignore_case_value.get(),
                                                                             self.file, replace_toplevel, find_entry,
                                                                             regex_value.get()))

        replace_toplevel.protocol('WM_DELETE_WINDOW', close_search_window)
        return "break"

    def replace_output(self, _find, _replace, _text, ignore, replace_box, regex):
        _text.tag_remove('match', '1.0', END)
        matches_found = 0
        if _find:
            start_pos = 1.0
            while True:
                start_pos = _text.search(_find, start_pos, nocase=ignore, regexp=regex, stopindex=END)
                if not start_pos:
                    break
                end_pos = '{}+{}c'.format(start_pos, len(_find))
                _text.replace(start_pos, end_pos, _replace)
                _text.tag_add('match', start_pos, end_pos)
                matches_found += 1
                start_pos = end_pos
            _text.tag_config('match', foreground='red', background='yellow')
            replace_box.title(f'{matches_found} matches replaced')

    def undo_event(self, event=None):
        self.file.event_generate('<<Undo>>')
        self.file.edit_undo()

    def redo_event(self, event=None):
        self.file.event_generate('<<Redo>>')
        self.file.edit_redo()


class PyMenuBar:
    def __init__(self, master, text_widget):
        self.master = master
        menubar = Menu(self.master)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label='New File', accelerator='Ctrl+N', command=lambda: text_widget.master.new_file())
        file_menu.add_command(label='Open', accelerator='Ctrl+O', command=lambda: self.master.open_file())
        file_menu.add_command(label='Save', accelerator='Ctrl+S', command=lambda: text_widget.master.save())
        file_menu.add_command(label='Save As', accelerator='Ctrl+Shift+S', command=lambda: text_widget.master.save_as())
        file_menu.add_command(label='Exit', accelerator='Alt+F4', command=lambda: self.master.destroy())
        menubar.add_cascade(label='File', menu=file_menu)
        edit_menu = Menu(menubar, tearoff=0)
        edit_menu.add_command(label='Copy', accelerator='Ctrl+C', command=lambda: menubar.event_generate("<<Copy>>"))
        edit_menu.add_command(label='Cut', accelerator='Ctrl+X', command=lambda: menubar.event_generate("<<Cut>>"))
        edit_menu.add_command(label='Paste', accelerator='Ctrl+V', command=lambda: menubar.event_generate("<<Paste>>"))
        edit_menu.add_command(label='Undo', accelerator='Ctrl+Z', command=text_widget.undo_event)
        edit_menu.add_command(label='Redo', accelerator='Ctrl+R', command=text_widget.redo_event)
        menubar.add_cascade(label='Edit', menu=edit_menu)
        config_menu = Menu(menubar, tearoff=0)
        # config_menu.add_command(label='Run', accelerator='F5', command=text_widget.execute)
        config_menu.add_command(label='Find', accelerator='Ctrl+F', command=text_widget.find_text)
        config_menu.add_command(label='Replace', accelerator='Ctrl+H', command=text_widget.replace)
        menubar.add_cascade(label='Config', menu=config_menu)
        self.master.master.config(menu=menubar)


class MenuBar:
    def __init__(self, master, widget):
        self.master = master
        menubar = Menu(self.master)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label='New File', accelerator='Ctrl+N', command=lambda: widget.master.new_file())
        file_menu.add_command(label='Open', accelerator='Ctrl+O', command=lambda: widget.master.open_file())
        file_menu.add_command(label='Save', accelerator='Ctrl+S', command=lambda: widget.master.save())
        file_menu.add_command(label='Save As', accelerator='Ctrl+Shift+S', command=lambda: widget.master.save_as())
        file_menu.add_command(label='Exit', accelerator='Alt+F4', command=lambda: self.master.destroy())
        menubar.add_cascade(label='File', menu=file_menu)
        edit_menu = Menu(menubar, tearoff=0)
        edit_menu.add_command(label='Copy', accelerator='Ctrl+C', command=lambda: menubar.event_generate("<<Copy>>"))
        edit_menu.add_command(label='Cut', accelerator='Ctrl+X', command=lambda: menubar.event_generate("<<Cut>>"))
        edit_menu.add_command(label='Paste', accelerator='Ctrl+V', command=lambda: menubar.event_generate("<<Paste>>"))
        edit_menu.add_command(label='Undo', accelerator='Ctrl+Z', command=widget.master.undo_event)
        edit_menu.add_command(label='Redo', accelerator='Ctrl+R', command=widget.master.redo_event)
        menubar.add_cascade(label='Edit', menu=edit_menu)
        config_menu = Menu(menubar, tearoff=0)
        config_menu.add_command(label='Find', accelerator='Ctrl+F', command=widget.master.find_text)
        config_menu.add_command(label='Replace', accelerator='Ctrl+H', command=widget.master.re_place)
        menubar.add_cascade(label='Config', menu=config_menu)
        self.master.master.config(menu=menubar)


def theme_settings(event, root):
    ThemeWin(root).focus_force()


def main():
    root = ThemedTk(fonts=True, themebg=True)
    root.set_theme('arc')
    root.minsize(400, 400)
    root.geometry('700x600+40+0')
    root.title('EZ_PY')

    config_frame = Frame(root, bd=1, highlightthickness=1, highlightbackground='black')
    config_frame.pack(side=LEFT, fill=Y)
    add = Label(config_frame, text='+', fg='blue', font=('Consolas', 20), cursor='hand2')
    add.pack()
    themes = Label(config_frame, text='☰', fg='blue', font='Consolas 20', cursor='hand2')
    themes.pack()
    ez_py = CustomNotebook(root)
    ez_py.pack(side=TOP, fill=BOTH, expand=YES)

    root.bind('<Control-N>', ez_py.select_new_tab)
    root.bind('<Control-n>', ez_py.select_new_tab)
    root.bind('<Control-Shift-C>', ez_py.add_console_tab)
    root.bind('<Control-Shift-c>', ez_py.add_console_tab)
    root.bind('<Control-Shift-N>', ez_py.add_py_tab)
    root.bind('<Control-Shift-n>', ez_py.add_py_tab)
    root.bind('<Control-T>', theme_settings)
    root.bind('<Control-t>', theme_settings)
    add.bind('<Enter>', lambda a=None, b=None: [add.config(fg='orange'),
                                                ToolTip(add, 'Consolas 9', 'Create a new file', follow=False)])
    add.bind('<Leave>', lambda a=None: add.config(fg='blue'))
    add.bind('<Button-1>', ez_py.select_new_tab)
    add.bind('<Control-Shift-n>', ez_py.select_new_tab)
    add.bind('<Control-Shift-N>', ez_py.select_new_tab)
    themes.bind('<Enter>', lambda a=None, b=None: [themes.config(fg='orange'),
                                                   ToolTip(themes, 'Consolas 9', 'Theme Settings', follow=False)])
    themes.bind('<Leave>', lambda a=None: themes.config(fg='blue'))
    themes.bind('<Button-1>', lambda e: theme_settings(e, root=root))
    ez_py.focus_force()
    root.mainloop()


if __name__ == '__main__':
    main()
