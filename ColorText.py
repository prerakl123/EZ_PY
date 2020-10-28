from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
import keyword
import builtins
import re
from code import InteractiveInterpreter
import json
from LineNumberCanvas import LineNumberCanvas
from HandyConsole import Console


class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert('end', string)
        self.text_space.see('end')


class ColorText(Text):
    FILETYPES = [("Python File", "*.py"), ("Text Documents", "*.txt"), ("Markdown File", "*.md"), ("All Files", "*.*")]

    def __init__(self, **kwargs):
        Text.__init__(self, **kwargs)
        self.root = self.master

        with open('./config.json') as file:
            self.config_dict = json.load(file)
        self.config(font=self.config_dict['color_text_font'], wrap=NONE)
        self.theme = self.config_dict['themes'][self.config_dict['selected_theme']].split('.')
        self.config(fg=self.theme[0], bg=self.theme[1], insertbackground=self.theme[2],
                    tabs=str(0.95*(int(self.config_dict['tab_length'])/4))+'c')

        self.PROGRAM_NAME = 'EZ_PY'
        self.file_name = None
        self.FILETYPES = [("Python File", "*.py"), ("Text Documents", "*.txt"), ("All Files", "*.*")]

        self.storeobj = {}

        self.module_list = self.__list()
        self.executing = False

        self.up_date()
        self.mechanise()
        self._set_()
        self.binding_keys()

        self.textfilter = re.compile(self.ty(), re.S)
        self.bind('<Control-Key-Tab>', self.on_ctab)
        self.bind('<Control-Shift-N>', self.new_file)
        self.bind('<Control-Shift-n>', self.new_file)
        self.bind('<Control-O>', self.open_file)
        self.bind('<Control-o>', self.open_file)
        self.bind('<Control-S>', self.save)
        self.bind('<Control-s>', self.save)
        self.bind('<Control-f>', self.find_text)
        self.bind('<Control-F>', self.find_text)
        self.bind('<Control-H>', self._replace)
        self.bind('<Control-h>', self._replace)
        self.bind('<Control-z>', self.undo_event)
        self.bind('<Control-Z>', self.undo_event)
        self.bind('<Control-r>', self.redo_event)
        self.bind('<Control-R>', self.redo_event)
        self.bind('<KeyRelease-bracketleft>', lambda a: self.autocomplete(val='['))
        self.bind('<KeyRelease-braceleft>', lambda a: self.autocomplete(val='{'))
        self.bind('<KeyRelease-parenleft>', lambda a: self.autocomplete(val='('))
        self.bind('<KeyRelease-bracketright>', lambda a: self.autocomplete(val=']'))
        self.bind('<KeyPress-bracketright>', lambda a: self.autocomplete(val=']'))
        self.bind('<KeyRelease-braceright>', lambda a: self.autocomplete(val='}'))
        self.bind('<KeyPress-braceright>', lambda a: self.autocomplete(val='}'))
        self.bind('<KeyRelease-parenright>', lambda a: self.autocomplete(val=')'))
        self.bind('<KeyPress-parenright>', lambda a: self.autocomplete(val=')'))
        self.bind('<KeyPress-quoteright>', lambda a: self.autocomplete(val="'"))
        self.bind('<KeyPress-quotedbl>', lambda a: self.autocomplete(val='"'))
        self.bind('<KeyPress-less>', lambda a: self.autocomplete(val='<'))
        self.bind('<KeyPress-greater>', lambda a: self.autocomplete(val='>'))
        self.bind('<Any-Key>', self.trigger)
        self.bind('<Control_R>', self.inst_trigger)
        self.bind('<Control_L>', self.inst_trigger)
        self.bind('<Return>', self.inst_trigger)
        self.bind('<Shift_R>', self.inst_trigger)
        self.bind('<Shift_L>', self.inst_trigger)
        self.bind('<Button-3>', self.r_click, add='')
        self.bind('<F5>', self.execute)
        # self.bind('<<Selection>>', self.on_select)

    def __list(self) -> list:
        modules = []
        import pkgutil
        for i in pkgutil.iter_modules():
            modules.append(i.name)
        in_modules = sys.modules.keys()
        modules = list(modules+list(in_modules))
        for i in modules:
            if '[' in i or ']' in i or '(' in i or ')' in i:
                modules.pop(modules.index(i))
        return modules

#        try:
#            import os
#            stream = os.popen('pip list')
#            output_str = stream.read()
#            r_o = " ".join(output_str.split())
#            list_r_o = r_o.split()
#            modules = []
#            for i in range(len(list_r_o)):
#                if i in [0, 1, 2, 3]:
#                    pass
#                else:
#                    if i % 2 == 0:
#                        if '-' in list_r_o[i]:
#                            modules.append(list_r_o[i].split('-')[0])
#                            modules.append(list_r_o[i].replace('-', '_'))
#                        else:
#                            modules.append(list_r_o[i])
#            return modules
#        except Exception or Warning:
#            pass

    def open_file(self, event=None):
        input_file_name = tkinter.filedialog.askopenfile(defaultextension=".txt", filetypes=self.FILETYPES)
        if input_file_name:
            self.file_name = input_file_name.name
            # self.root.title('{} - {}'.format(self.file_name, self.PROGRAM_NAME))
            self.delete(1.0, END)
            with open(self.file_name, encoding='utf-8') as _file:
                try:
                    self.insert(1.0, _file.read())
                except UnicodeError or UnicodeTranslateError or UnicodeDecodeError or UnicodeEncodeError or\
                        UnicodeWarning:
                    tkinter.messagebox.showerror('Can\'t open file',
                                                 'This error could be due to images in a file or some'
                                                 ' characters that the program is unable to read')
        self.inst_trigger()

    def new_file(self, event=None):
        # self.root.title("Untitled")
        self.file_name = None
        self.delete(1.0, END)
        # output.delete(1.0, END)

    def write_to_file(self, _file_name):
        try:
            content = self.get(1.0, 'end')
            with open(_file_name, 'w') as the_file:
                the_file.write(content)
        except IOError:
            tkinter.messagebox.showwarning("Save", "Could not save the file.")

    def save_as(self, event=None):
        input_file_name = tkinter.filedialog.asksaveasfile(defaultextension=".py", filetypes=self.FILETYPES)
        if input_file_name:
            self.file_name = input_file_name.name
            self.write_to_file(self.file_name)
            # self.root.title('{} - {}'.format(self.file_name, self.PROGRAM_NAME))
        return "break"

    def save(self, event=None):
        if not self.file_name:
            self.save_as()
        else:
            self.write_to_file(self.file_name)
        return "break"

    def undo_event(self, event=None):
        self.event_generate('<<Undo>>')
        self.edit_undo()

    def redo_event(self, event=None):
        self.event_generate('<<Redo>>')
        self.edit_redo()

    def on_ctab(self, event=None):
        event.widget.tk_focusNext().focus()
        return "break"

    def autocomplete(self, val):
        if val == '(':
            self.insert(INSERT, ')')
            self.mark_set(INSERT,
                          f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")
        elif val == '{':
            self.insert(INSERT, '}')
            self.mark_set(INSERT,
                          f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")
        elif val == '[':
            self.insert(INSERT, ']')
            self.mark_set(INSERT,
                          f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")
        elif val == '<':
            self.insert(INSERT, '>')
            self.mark_set(INSERT,
                          f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")
        elif val == ')':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == ')':
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
            else:
                return ')'
            return 'break'
        elif val == '}':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == '}':
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
            else:
                return '}'
            return 'break'
        elif val == ']':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == ']':
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
            else:
                return ']'
            return 'break'
        elif val == '>':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == '>':
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
            else:
                return '>'
            return 'break'
        elif val == '"':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == '"':
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
                return 'break'
            else:
                self.insert(INSERT, '"')
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")

        elif val == "'":
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == "'":
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
                return 'break'
            else:
                self.insert(INSERT, "'")
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")
            
        return

    def find_text(self, event=None):
        search_toplevel = Toplevel(self.root)
        search_toplevel.title('Find Text')
        search_toplevel.transient(self.root)

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
               command=lambda: self.search_output(search_entry_widget.get(), ignore_case_value.get(), self,
                                                  search_toplevel, search_entry_widget, regex_value.get())).grid(
            row=0, column=2, sticky=E + W, padx=2, pady=2)

        def close_search_window(_event=None):
            self.tag_remove('match', '1.0', END)
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
        replace_toplevel = Toplevel(self.root)
        replace_toplevel.title('Find and Replace Text')
        replace_toplevel.transient(self.root)
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
                                                                                           pady=2,
                                                                                           sticky=W)
        Checkbutton(replace_toplevel, text='Regular Expression', variable=regex_value).grid(row=4, column=0, padx=2,
                                                                                            pady=2,
                                                                                            sticky=E)
        Button(replace_toplevel, text='Find All',
               command=lambda: self.search_output(find_entry.get(), ignore_case_value.get(),
                                                  self, replace_toplevel, find_entry,
                                                  regex_value.get()),
               width=12).grid(row=1, column=1, padx=2, pady=2, sticky=E)
        Button(replace_toplevel, text='Replace All',
               command=lambda: self.replace_output(find_entry.get(), replace_entry.get(),
                                                   self, ignore_case_value.get(),
                                                   replace_toplevel, regex_value.get()),
               width=12).grid(row=2, column=1, padx=2, pady=2, sticky=E)

        def close_search_window(_event=None):
            replace_toplevel.destroy()
            self.tag_remove('match', '1.0', END)

        replace_toplevel.bind('<Escape>', close_search_window)
        replace_toplevel.bind('<Return>', lambda: self.replace_output(find_entry.get(), replace_entry.get(), self,
                                                                      ignore_case_value.get(), replace_toplevel,
                                                                      regex_value.get()))
        replace_toplevel.bind('<Shift-Return>', lambda a: self.search_output(find_entry.get(), ignore_case_value.get(),
                                                                             self, replace_toplevel, find_entry,
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

    def execute(self, event=None):
        output = Toplevel(self, width=200, height=200)
        output.title('Output Window')
        output_win = Console(output, locals(), output.destroy)

        if self.executing is True:
            self.save()
            code = self.get('1.0', END + '-1c')
            # stdin = sys.stdin
            stdout = sys.stdout
            stderr = sys.stderr

            sys.stdout = StdoutRedirector(output_win)
            sys.stderr = StdoutRedirector(output_win)

            interp = InteractiveInterpreter()
            interp.runcode(code)

            sys.stdout = stdout
            sys.stderr = stderr
            # sys.stdin = stdin
        else:
            self.save()

            self.executing = True
            output_win.pack(side=BOTTOM, expand=TRUE, fill=BOTH)

            code = self.get('1.0', END + '-1c')
            # stdin = sys.stdin
            stdout = sys.stdout
            stderr = sys.stderr

            #    def a():
            #        sys.stdin = StdinRedirector(output)
            #    output.bind('<Return>', lambda: a)

            sys.stdout = StdoutRedirector(output_win)
            sys.stderr = StdoutRedirector(output_win)

            interp = InteractiveInterpreter()
            interp.runcode(code)

            sys.stdout = stdout
            sys.stderr = stderr
            # sys.stdin = stdin

    def _any(self, name, alternates):
        """Return a named group pattern matching list of alternates."""
        return "(?P<%s>" % name + "|".join(alternates) + ")"

    def ty(self):
        kw = r"\b" + self._any("KEYWORD", keyword.kwlist) + r"\b"

        builtinlist = [str(name) for name in dir(builtins) if not name.startswith('_')]
        builtin = r"([^.'\"\\#]\b|^)" + self._any("BUILTIN", builtinlist) + r"\b"

        comment = self._any("COMMENT", [r"#[^\n]*"])

        stringprefix = r"(\bB|b|br|Br|bR|BR|rb|rB|Rb|RB|r|u|R|U|f|F|fr|Fr|fR|FR|rf|rF|Rf|RF)?"
        sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
        dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
        sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
        dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
        string = self._any("STRING", [sq3string, dq3string, sqstring, dqstring])

        numbers = self._any("NUMBERS", [str(i) for i in range(10)])

        speciallist = ['=', '@', '-', ':', '<', '>', r'[+]', r'[*]', r'[.]', r'[!]', r'[%]', r'[\\]']
        special = self._any("SPECIAL", speciallist)

        bracketlist = [r'[(]', r'[)]', r'[{]', r'[}]', r'[[]', r'[]]']
        bracket = self._any("BRACKET", bracketlist)

        decorators = self._any("DECORATORS", [r"@[^\n]*"])

        modules = r"([^.'\"\\#]\b|^)" + self._any('MODULES', self.module_list) + r"\b"

        dunder_list = ['__abs__', '__add__', '__and__', '__bool__', '__ceil__', '__class__', '__contains__',
                       '__delattr__', '__delitem__', '__dir__', '__divmod__', '__doc__', '__eq__', '__float__',
                       '__floor__', '__floordiv__', '__format__', '__ge__', '__getattribute__', '__getitem__',
                       '__getnewargs__', '__gt__', '__hash__', '__index__', '__iadd__', '__imul__', '__init__',
                       '__init_subclass__', '__int__', '__invert__', '__iter__', '__le__', '__len__', '__lshift__',
                       '__lt__', '__mod__', '__mul__', '__name__', '__ne__', '__neg__', '__new__', '__or__', '__pos__',
                       '__pow__', '__qualname__', '__radd__', '__rand__', '__rdivmod__', '__reduce__', '__reduce_ex__',
                       '__repr__', '__reversed__', '__rfloordiv__', '__rlshift__', '__rmod__', '__rmul__', '__ror__',
                       '__round__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__', '__rtruediv__', '__rxor__',
                       '__self__', '__setattr__', '__setitem__', '__sizeof__', '__str__', '__sub__', '__subclasshook__',
                       '__text_signature__', '__truediv__', '__trunc__', '__xor__', '__weakref__', 'self']
        dunder = self._any("DUNDER", [fr'\b{i}\b' for i in dunder_list])

        # r_link_s = r'(https?://\S+)'
        # r_link_uns = r'(http?://\S+)'
        # w_link = r'(www(.).*(.).*)'
        # URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:\'\".,<>?])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
        # link = self._any("LINK", [URL_REGEX])

        return kw + "|" + builtin + "|" + comment + "|" + string + "|" + numbers + '|' + special + '|' + decorators + \
            '|' + bracket + '|' + modules + '|' + dunder + '|' + self._any("SYNC", [r"\n"])

    def _coordinate(self, start, end, string):
        srow = string[:start].count('\n') + 1
        scolsplitlines = string[:start].split('\n')

        if len(scolsplitlines) != 0:
            scolsplitlines = scolsplitlines[len(scolsplitlines) - 1]

        scol = len(scolsplitlines)
        lrow = string[:end + 1].count('\n') + 1
        lcolsplitlines = string[:end].split('\n')

        if len(lcolsplitlines) != 0:
            lcolsplitlines = lcolsplitlines[len(lcolsplitlines) - 1]

        lcol = len(lcolsplitlines) + 1

        return '{}.{}'.format(srow, scol), '{}.{}'.format(lrow, lcol)

    def coordinate(self, pattern, string, text):
        line = string.splitlines()
        start = line.find(pattern)
        end = start + len(pattern)
        srow = string[:start].count('\n') + 1
        scolsplitlines = string[:start].split('\n')

        if len(scolsplitlines) != 0:
            scolsplitlines = scolsplitlines[len(scolsplitlines) - 1]

        scol = len(scolsplitlines)
        lrow = string[:end + 1].count('\n') + 1
        lcolsplitlines = string[:end].split('\n')

        if len(lcolsplitlines) != 0:
            lcolsplitlines = lcolsplitlines[len(lcolsplitlines) - 1]
        lcol = len(lcolsplitlines)

        return '{}.{}'.format(srow, scol), '{}.{}'.format(lrow, lcol)

    def check(self, k: dict):
        if k['COMMENT'] is not None:
            return 'comment', self.config_dict['text_color']['comment'][self.config_dict['selected_theme']]

        elif k['BUILTIN'] is not None:
            return 'builtin', self.config_dict['text_color']['builtin'][self.config_dict['selected_theme']]

        elif k['STRING'] is not None:
            return 'string', self.config_dict['text_color']['string'][self.config_dict['selected_theme']]

        elif k['KEYWORD'] is not None:
            return 'keyword', self.config_dict['text_color']['keyword'][self.config_dict['selected_theme']]

        elif k['NUMBERS'] is not None:
            return 'numbers', self.config_dict['text_color']['numbers'][self.config_dict['selected_theme']]

        elif k['SPECIAL'] is not None:
            return 'special', self.config_dict['text_color']['special'][self.config_dict['selected_theme']]

        elif k['BRACKET'] is not None:
            return 'bracket', self.config_dict['text_color']['bracket'][self.config_dict['selected_theme']]

        elif k['MODULES'] is not None:
            return 'modules', self.config_dict['text_color']['modules'][self.config_dict['selected_theme']]

        elif k['DUNDER'] is not None:
            return 'dunder', self.config_dict['text_color']['dunder'][self.config_dict['selected_theme']]

        # elif k['LINK'] is not None:
        #     return 'link', self.config_dict['text_color']['link'][self.config_dict['selected_theme']]

        else:
            return 'ss', 'NILL'

    def binding_functions_configuration(self):
        self.storeobj['ColorLight'] = self.trigger
        return

    def on_tab(self, event=None):
        self.insert(END, ' ' * int(self.config_dict['tab_length']))
        return 'break'

    def trigger(self, event=None):
        if event.keysym in ('Up', 'Down'):
            return
        
        val = self.get(INSERT + ' linestart', INSERT + ' lineend')
        # print(val, self.text.index(INSERT+' linestart'), self.text.index(INSERT+' lineend'))
        if len(val) == 1:
            return

        for i in ['comment', 'builtin', 'string', 'keyword', 'numbers', 'special', 'bracket', 'modules', 'dunder']:
            self.tag_remove(i, INSERT + ' linestart', INSERT + ' lineend')

        for i in self.textfilter.finditer(val):
            start = i.start()
            end = i.end() - 1
            tagtype, color = self.check(k=i.groupdict())
            # print(tagtype, 'start:', start, 'end:', end)
            if color != 'NILL':
                ind1, ind2 = self._coordinate(start=start, end=end, string=val)
                self.tag_add(tagtype,
                             f"{int(ColorText.index(self, INSERT).split('.')[0])}.{str(ind1).split('.')[1]}",
                             f"{int(ColorText.index(self, INSERT).split('.')[0])}.{str(ind2).split('.')[1]}")
                self.tag_config(tagtype, foreground=color)
                # print('tagtype:', tagtype, 'ind1:', ind1, 'ind2:', ind2, 'start:', start, 'end:', end, 'val:',val)

    def inst_trigger(self, event=None):
        val = self.get(1.0, END)
        if len(val) == 1:
            return

        for i in ['comment', 'builtin', 'string', 'keyword', 'numbers', 'special', 'bracket', 'modules', 'dunder']:
            self.tag_remove(1.0, END)

        for i in self.textfilter.finditer(val):
            start = i.start()
            end = i.end() - 1
            tagtype, color = self.check(k=i.groupdict())
            if color != 'NILL':
                ind1, ind2 = self._coordinate(start=start, end=end, string=val)
                self.tag_add(tagtype, ind1, ind2)
                self.tag_config(tagtype, foreground=color)
            # self.tag_bind('link', '<Control-Button-1>', self.open_link)
            # self.tag_bind('link', '<Double-1>', self.open_link)
            # self.tag_configure('link', underline=1, foreground='#0000ff')
            # self.tag_raise('link', 'string')
            # self.tag_raise('link', 'comment')

    def mechanise(self):
        self.tk.eval('''
        proc widget_interceptor {widget command args} {
            set orig_call [uplevel 1 [linsert $args 0 $command]]
            if {
                [lindex $args 0] in {insert delete replace} ||
                ([lrange $args 0 2] == {mark set insert}) || 
                ([lrange $args 0 1] == {xview moveto}) ||
                ([lrange $args 0 1] == {xview scroll}) ||
                ([lrange $args 0 1] == {yview moveto}) ||
                ([lrange $args 0 1] == {yview scroll})
            } then {
                event generate $widget <<Changed>>
            }
            #return original command
            return $orig_call
        }
        proc install_widget_interceptor {widget} {
            global unique_widget_id
            set handle ::_intercepted_widget_[incr unique_widget_id]
            rename $widget $handle
            interp alias {} ::$widget {} widget_interceptor $widget $handle
        }
        ''')
        self.tk.eval('''
        install_widget_interceptor {widget}
        '''.format(widget=str(self)))
        return

    def _set_(self):
        self.linenumbers = LineNumberCanvas(self.master, width=30)
        self.linenumbers.connect(self)
        self.linenumbers.pack(side=LEFT, fill=Y)
        return

    def changed(self, event):
        self.linenumbers.re_render()
        return

    def binding_keys(self):
        for key in ['<Down>', '<Up>', "<<Changed>>", "<Configure>", '<Home>', '<End>', '<Prior>', '<Control_L>',
                    '<Next>', '<Control_R>', '<Prior>', '<Next>']:
            self.bind(key, self.changed)
        self.linenumbers.bind('<Button-1>', self.linenumbers.get_breakpoint_number)
        return

        
    def r_click(self, event):
        """right click context menu for all Tk Entry and Text widgets"""


        try:
            def r_click_copy(event, apnd=0):
                event.widget.event_generate('<Control-c>')

            def r_click_cut(event):
                event.widget.event_generate('<Control-x>')

            def r_click_paste(event):
                event.widget.event_generate('<Control-v>')
                self.inst_trigger()

            event.widget.focus()

            nclst = [
                     (' Cut', lambda event=event: r_click_cut(event)),
                     (' Copy', lambda event=event: r_click_copy(event)),
                     (' Paste', lambda event=event: r_click_paste(event)),
            ]

            rmenu = Menu(None, tearoff=0, takefocus=0)

            for (txt, cmd) in nclst:
                rmenu.add_command(label=txt, command=cmd)

            rmenu.tk_popup(event.x_root+40, event.y_root+10, entry="0")

        except TclError:
            pass
        return "break"

    def r_click_binder(self, r):
        try:
            for b in ['Text', 'Entry', 'Listbox', 'Label']:
                r.bind_class(b, sequence='<Button-3>',
                             func=self.r_click, add='')
                r.bind_class(b, sequence='<KeyPressed-App>',
                             func=self.r_click, add='')
        except TclError:
            print(' - rClickbinder, something wrong')
            pass


    def up_date(self, event=None):
        with open('config.json') as _file:
            self.config_dict = json.load(_file)
        self.theme = self.config_dict['themes'][self.config_dict['selected_theme']].split('.')
        self.config(fg=self.theme[0], bg=self.theme[1], insertbackground=self.theme[2],
                    tabs=str(0.95*(int(self.config_dict['tab_length'])/4))+'c')
        self.after(2000, self.up_date)


if __name__ == '__main__':
    root = Tk()
    s = ColorText(master=root)
    s.pack(side=TOP, expand=TRUE, fill=BOTH)
    root.call('encoding', 'system', 'utf-8')
    root.mainloop()


