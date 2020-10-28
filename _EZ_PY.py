import builtins
import keyword
from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
import sys
import re
from code import InteractiveConsole, InteractiveInterpreter
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

PROGRAM_NAME = 'EZ_PY'
file_name = None
FILETYPES = [("Python File", "*.py"), ("Text Documents", "*.txt"), ("All Files", "*.*")]
root = Tk()
root.minsize(900, 300)
root.geometry('800x500')
icon_pic = PhotoImage(file='py_icon.png')
root.iconphoto(False, icon_pic)


class History(list):
    def __getitem__(self, index):
        try:
            return list.__getitem__(self, index)
        except IndexError:
            return


class TextConsole(Text):
    def __init__(self, master, **kw):
        kw.setdefault('width', 50)
        kw.setdefault('wrap', 'word')
        kw.setdefault('prompt1', '>>> ')
        kw.setdefault('prompt2', '... ')
        banner = kw.pop('banner', 'Python %s\n' % sys.version)
        self._prompt1 = kw.pop('prompt1')
        self._prompt2 = kw.pop('prompt2')
        Text.__init__(self, master, **kw)
        # --- history
        self.history = History()
        self._hist_item = 0
        self._hist_match = ''

        # --- initialization
        self._console = InteractiveConsole()  # python console to execute commands
        self.insert('end', banner, 'banner')
        self.prompt()
        self.mark_set('input', 'insert')
        self.mark_gravity('input', 'left')

        # --- bindings
        self.bind('<Control-Return>', self.on_ctrl_return)
        self.bind('<Shift-Return>', self.on_shift_return)
        self.bind('<KeyPress>', self.on_key_press)
        self.bind('<KeyRelease>', self.on_key_release)
        self.bind('<Tab>', self.on_tab)
        self.bind('<Down>', self.on_down)
        self.bind('<Up>', self.on_up)
        self.bind('<Return>', self.on_return)
        self.bind('<BackSpace>', self.on_backspace)
        self.bind('<Control-c>', self.on_ctrl_c)
        self.bind('<<Paste>>', self.on_paste)

    def on_ctrl_c(self, event):
        """Copy selected code, removing prompts first"""
        sel = self.tag_ranges('sel')
        if sel:
            txt = self.get('sel.first', 'sel.last').splitlines()
            lines = []
            for i, line in enumerate(txt):
                if line.startswith(self._prompt1):
                    lines.append(line[len(self._prompt1):])
                elif line.startswith(self._prompt2):
                    lines.append(line[len(self._prompt2):])
                else:
                    lines.append(line)
            self.clipboard_clear()
            self.clipboard_append('\n'.join(lines))
        return 'break'

    def on_paste(self, event):
        """Paste commands"""
        if self.compare('insert', '<', 'input'):
            return "break"
        sel = self.tag_ranges('sel')
        if sel:
            self.delete('sel.first', 'sel.last')
        txt = self.clipboard_get()
        self.insert("insert", txt)
        self.insert_cmd(self.get("input", "end"))
        return 'break'

    def prompt(self, result=False):
        """Insert a prompt"""
        if result:
            self.insert('end', self._prompt2, 'prompt')
        else:
            self.insert('end', self._prompt1, 'prompt')
        self.mark_set('input', 'end-1c')

    def on_key_press(self, event):
        """Prevent text insertion in command history"""
        if self.compare('insert', '<', 'input') and event.keysym not in ['Left', 'Right']:
            self._hist_item = len(self.history)
            self.mark_set('insert', 'input lineend')
            if not event.char.isalnum():
                return 'break'

    def on_key_release(self, event):
        """Reset history scrolling"""
        if self.compare('insert', '<', 'input') and event.keysym not in ['Left', 'Right']:
            self._hist_item = len(self.history)
            return 'break'

    def on_up(self, event):
        """Handle up arrow key press"""
        if self.compare('insert', '<', 'input'):
            self.mark_set('insert', 'end')
            return 'break'
        elif self.index('input linestart') == self.index('insert linestart'):
            # navigate history
            line = self.get('input', 'insert')
            self._hist_match = line
            hist_item = self._hist_item
            self._hist_item -= 1
            item = self.history[self._hist_item]
            while self._hist_item >= 0 and not item[-1].startswith(line):
                self._hist_item -= 1
                item = self.history[self._hist_item]
            if self._hist_item >= 0:
                index = self.index('insert')
                self.insert_cmd(item)
                self.mark_set('insert', index)
            else:
                self._hist_item = hist_item
            return 'break'

    def on_down(self, event):
        """Handle down arrow key press"""
        if self.compare('insert', '<', 'input'):
            self.mark_set('insert', 'end')
            return 'break'
        elif self.compare('insert lineend', '==', 'end-1c'):
            # navigate history
            line = self._hist_match
            self._hist_item += 1
            item = self.history[self._hist_item]
            while item is not None and not item[-1].startswith(line):
                self._hist_item += 1
                item = self.history[self._hist_item]
            if item is not None:
                self.insert_cmd(item)
                self.mark_set('insert', 'input+%ic' % len(self._hist_match))
            else:
                self._hist_item = len(self.history)
                self.delete('input', 'end')
                self.insert('insert', line)
            return 'break'

    def on_tab(self, event):
        """Handle tab key press"""
        if self.compare('insert', '<', 'input'):
            self.mark_set('insert', 'input lineend')
            return "break"
        # indent code
        sel = self.tag_ranges('sel')
        if sel:
            start = str(self.index('sel.first'))
            end = str(self.index('sel.last'))
            start_line = int(start.split('.')[0])
            end_line = int(end.split('.')[0]) + 1
            for line in range(start_line, end_line):
                self.insert('%i.0' % line, '    ')
        else:
            txt = self.get('insert-1c')
            if not txt.isalnum() and txt != '.':
                self.insert('insert', '    ')
        return "break"

    def on_shift_return(self, event):
        """Handle Shift+Return key press"""
        if self.compare('insert', '<', 'input'):
            self.mark_set('insert', 'input lineend')
            return 'break'
        else:  # execute commands
            self.mark_set('insert', 'end')
            self.insert('insert', '\n')
            self.insert('insert', self._prompt2, 'prompt')
            self.eval_current(True)

    def on_return(self, event=None):
        """Handle Return key press"""
        if self.compare('insert', '<', 'input'):
            self.mark_set('insert', 'input lineend')
            return 'break'
        else:
            self.eval_current(True)
            self.see('end')
        return 'break'

    def on_ctrl_return(self, event=None):
        """Handle Ctrl+Return key press"""
        self.insert('insert', '\n' + self._prompt2, 'prompt')
        return 'break'

    def on_backspace(self, event):
        """Handle delete key press"""
        if self.compare('insert', '<=', 'input'):
            self.mark_set('insert', 'input lineend')
            return 'break'
        sel = self.tag_ranges('sel')
        if sel:
            self.delete('sel.first', 'sel.last')
        else:
            linestart = self.get('insert linestart', 'insert')
            if re.search(r' '*4 + r'$', linestart):
                self.delete('insert-4c', 'insert')
            else:
                self.delete('insert-1c')
        return 'break'

    def insert_cmd(self, cmd):
        """Insert lines of code, adding prompts"""
        input_index = self.index('input')
        self.delete('input', 'end')
        _cmd = ''
        for i in range(len(cmd)):
            c = cmd[i].__add__('\n')
            _cmd += c
        lines = _cmd.splitlines()
        if lines:
            indent = len(re.search(r'^( )*', lines[0]).group())
            self.insert('insert', lines[0][indent:])
            for line in lines[1:]:
                line = line[indent:]
                self.insert('insert', '\n')
                self.prompt(True)
                self.insert('insert', line)
                self.mark_set('input', input_index)
        self.see('end')

    def eval_current(self, auto_indent=False):
        """Evaluate code"""
        index = self.index('input')
        lines = self.get('input', 'insert lineend').splitlines()  # commands to execute
        self.mark_set('insert', 'insert lineend')
        if lines:  # there is code to execute
            # remove prompts
            lines = [lines[0].rstrip()] + [line[len(self._prompt2):].rstrip() for line in lines[1:]]
            for i, l in enumerate(lines):
                if l.endswith('?'):
                    lines[i] = 'help(%s)' % l[:-1]
            cmds = '\n'.join(lines)
            self.insert('insert', '\n')
            out = StringIO()  # command output
            err = StringIO()  # command error traceback
            with redirect_stderr(err):     # redirect error traceback to err
                with redirect_stdout(out):  # redirect command output
                    # execute commands in interactive console
                    res = self._console.push(cmds)
                    # if res is True, this is a partial command, e.g. 'def test():' and we need to wait for the rest of
                    # the code
            errors = err.getvalue()
            if errors:  # there were errors during the execution
                self.insert('end', errors)  # display the traceback
                self.mark_set('input', 'end')
                self.see('end')
                self.prompt()  # insert new prompt
            else:
                output = out.getvalue()  # get output
                if output:
                    self.insert('end', output, 'output')
                self.mark_set('input', 'end')
                self.see('end')
                if not res and self.compare('insert linestart', '>', 'insert'):
                    self.insert('insert', '\n')
                self.prompt(res)
                if auto_indent and lines:
                    # insert indentation similar to previous lines
                    indent = re.search(r'^( )*', lines[-1]).group()
                    line = lines[-1].strip()
                    if line and line[-1] == ':':
                        indent = indent + '    '
                    self.insert('insert', indent)
                self.see('end')
                if res:
                    self.mark_set('input', index)
                    self._console.resetbuffer()  # clear buffer since whole command will be retrieved from text widget
                elif lines:
                    self.history.append(lines)  # add commands to history
                    self._hist_item = len(self.history)
            out.close()
            err.close()
        else:
            self.insert('insert', '\n')
            self.prompt()


t_scroll_v = Scrollbar(root, orient=VERTICAL)
t_scroll_h = Scrollbar(root, orient=HORIZONTAL)
text = Text(root, font='Consolas 15', bg='#02002e', fg='white', insertbackground='white', yscrollcommand=t_scroll_v.set,
            relief=SUNKEN, height=5, xscrollcommand=t_scroll_h.set, undo=True)
c_scroll = Scrollbar(root)
console = TextConsole(root, wrap=WORD, height=10, width=50, font=('Consolas 12'), yscrollcommand=c_scroll.set)
o_scroll = Scrollbar(root)
output = Text(root, width=50, height=5, wrap=WORD, yscrollcommand=o_scroll.set)


class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert('end', string)
        self.text_space.see('end')


# class StdinRedirector(object):
#     def __init__(self, text_widget):
#         self.text_space = text_widget
#
#     def readline(self) -> str:
#         t = self.text_space.get(INSERT, f"{int(text.index(INSERT).split('.')[0])}"
#                                         f".{int(text.index(INSERT).split('.')[1])}")
#         return t


def execute(event=None):
    save()
    code = text.get('1.0', END+'-1c')
#    stdin = sys.stdin
    stdout = sys.stdout 
    stderr = sys.stderr

    output.delete('1.0', END)
#    def a():
#        sys.stdin = StdinRedirector(output)
#    output.bind('<Return>', lambda: a)
    
    sys.stdout = StdoutRedirector(output)
    sys.stderr = StdoutRedirector(output)
    
    interp = InteractiveInterpreter()
    interp.runcode(code)

    sys.stdout = stdout
    sys.stderr = stderr
#    sys.stdin = stdin


def on_ctab(event=None):
    event.widget.tk_focusNext().focus()
    return "break"


def autocomplete(val):
    if val == '(':
        text.insert(INSERT, ')')
        text.mark_set(INSERT, f"{int(text.index(INSERT).split('.')[0])}.{int(text.index(INSERT).split('.')[1]) - 1}")
    elif val == '{':
        text.insert(INSERT, '}')
        text.mark_set(INSERT, f"{int(text.index(INSERT).split('.')[0])}.{int(text.index(INSERT).split('.')[1]) - 1}")
    elif val == '[':
        text.insert(INSERT, ']')
        text.mark_set(INSERT, f"{int(text.index(INSERT).split('.')[0])}.{int(text.index(INSERT).split('.')[1]) - 1}")
    elif val == ')':
        if text.get(text.index(INSERT),
                    f"{int(text.index(INSERT).split('.')[0])}.{int(text.index(INSERT).split('.')[1]) + 1}") == ')':
            text.mark_set(INSERT,
                          f"{int(text.index(INSERT).split('.')[0])}.{int(text.index(INSERT).split('.')[1]) + 1}")
        else:
            return ')'
        return 'break'
    elif val == '}':
        if text.get(text.index(INSERT),
                    f"{int(text.index(INSERT).split('.')[0])}.{int(text.index(INSERT).split('.')[1]) + 1}") == '}':
            text.mark_set(INSERT,
                          f"{int(text.index(INSERT).split('.')[0])}.{int(text.index(INSERT).split('.')[1]) + 1}")
        else:
            return '}'
        return 'break'
    elif val == ']':
        if text.get(text.index(INSERT),
                    f"{int(text.index(INSERT).split('.')[0])}.{int(text.index(INSERT).split('.')[1]) + 1}") == ']':
            text.mark_set(INSERT,
                          f"{int(text.index(INSERT).split('.')[0])}.{int(text.index(INSERT).split('.')[1]) + 1}")
        else:
            return ']'
        return 'break'
    return


def __list() -> list:
    try:
        import os
        stream = os.popen('pip list')
        output_str = stream.read()
        r_o = " ".join(output_str.split())
        list_r_o = r_o.split()
        modules = []
        for i in range(len(list_r_o)):
            if i in [0, 1, 2, 3]:
                pass
            else:
                if i % 2 == 0:
                    if '-' in list_r_o[i]:
                        modules.append(list_r_o[i].split('-')[0])
                        modules.append(list_r_o[i].replace('-', '_'))
                    else:
                        modules.append(list_r_o[i])
        return modules
    except Exception or Warning:
        pass


with open('builtins') as b_file:
    builtin_mods = b_file.read().split(',')


module_list = __list() + builtin_mods


def _any(name, alternates):
    """Return a named group pattern matching list of alternates."""
    return "(?P<%s>" % name + "|".join(alternates) + ")"


def ty():
    kw = r"\b" + _any("KEYWORD", keyword.kwlist) + r"\b"
    builtinlist = [str(name) for name in dir(builtins) if not name.startswith('_')]
    builtin = r"([^.'\"\\#]\b|^)" + _any("BUILTIN", builtinlist) + r"\b"
    comment = _any("COMMENT", [r"#[^\n]*"])
    stringprefix = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR)?"
    sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
    dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
    sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
    dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
    string = _any("STRING", [sq3string, dq3string, sqstring, dqstring])
    numbers = _any("NUMBERS", [str(i) for i in range(10)])
    speciallist = ['=', '@', '-', ':', '<', '>', r'[+]', r'[*]', r'[.]', r'[!]', r'[%]', r'[\\]']
    special = _any("SPECIAL", speciallist)
    bracketlist = [r'[(]', r'[)]', r'[{]', r'[}]', r'[[]', r'[]]']
    bracket = _any("BRACKET", bracketlist)
    decorators = _any("DECORATORS", [r"@[^\n]*"])
    modules = _any("MODULES", [fr'\b{i}\b' for i in module_list])

    return kw + "|" + builtin + "|" + comment + "|" + string + "|" + numbers + '|' + special + '|' + decorators + \
        '|' + bracket + '|' + modules + '|' + _any("SYNC", [r"\n"])


def _coordinate(start, end, string):
    srow = string[:start].count('\n')+1
    scolsplitlines = string[:start].split('\n')

    if len(scolsplitlines) != 0:
        scolsplitlines = scolsplitlines[len(scolsplitlines)-1]

    scol = len(scolsplitlines)
    lrow = string[:end+1].count('\n') + 1
    lcolsplitlines = string[:end].split('\n')

    if len(lcolsplitlines) != 0:
        lcolsplitlines = lcolsplitlines[len(lcolsplitlines) - 1]

    lcol = len(lcolsplitlines) + 1

    return '{}.{}'.format(srow, scol), '{}.{}'.format(lrow, lcol)


def coordinate(pattern, string, text):
    line = string.splitlines()
    start = line.find(pattern)
    end = start+len(pattern)
    srow = string[:start].count('\n')+1
    scolsplitlines = string[:start].split('\n')

    if len(scolsplitlines) != 0:
        scolsplitlines = scolsplitlines[len(scolsplitlines) - 1]

    scol = len(scolsplitlines)
    lrow = string[:end+1].count('\n')+1
    lcolsplitlines = string[:end].split('\n')

    if len(lcolsplitlines) != 0:
        lcolsplitlines = lcolsplitlines[len(lcolsplitlines) - 1]
    lcol = len(lcolsplitlines)

    return '{}.{}'.format(srow, scol), '{}.{}'.format(lrow, lcol)


def check(k: dict):
    if k['COMMENT'] is not None:
        return 'comment', '#00faee'

    elif k['BUILTIN'] is not None:
        return 'builtin', '#ff0059'

    elif k['STRING'] is not None:
        return 'string', '#fa0089'

    elif k['KEYWORD'] is not None:
        return 'keyword', '#eeff00'

    elif k['NUMBERS'] is not None:
        return 'numbers', '#00ff11'

    elif k['SPECIAL'] is not None:
        return 'special', '#0b8525'

    elif k['BRACKET'] is not None:
        return 'bracket', '#480b85'

    elif k['MODULES'] is not None:
        return 'modules', '#ff0000'

    else:
        return 'ss', 'NILL'


textfilter = re.compile(ty(), re.S)


class ColorLight:
    def __init__(self, textbox=None):
        self.text = textbox
        self.text.bind('<Any-Key>', self.trigger)

    def binding_functions_configuration(self):
        self.text.storeobj['ColorLight'] = self.trigger
        return

    def on_tab(self, event=None):
        self.text.insert(END, ' '*8)
        return 'break'

    def on_content_changed(self, event=None) -> str:
        row, col = text.index(INSERT).split('.')
        line_num, col_num = int(row), int(col)
        return str(line_num) + '.' + str(col_num)

    def trigger(self, event=None):
        val = self.text.get(INSERT+' linestart', INSERT+' lineend')
        # print(val, self.text.index(INSERT+' linestart'), self.text.index(INSERT+' lineend'))
        if len(val) == 1:
            return

        for i in ['comment', 'builtin', 'string', 'keyword', 'numbers', 'special', 'bracket', 'modules']:
            self.text.tag_remove(i, INSERT+' linestart', INSERT+' lineend')

        for i in textfilter.finditer(val):
            start = i.start()
            end = i.end()-1
            tagtype, color = check(k=i.groupdict())
            # print(tagtype, 'start:', start, 'end:', end)
            if color != 'NILL':
                ind1, ind2 = _coordinate(start, end, val)
                self.text.tag_add(tagtype, f"{int(text.index(INSERT).split('.')[0])}.{str(ind1).split('.')[1]}",
                                  f"{int(text.index(INSERT).split('.')[0])}.{str(ind2).split('.')[1]}")
                self.text.tag_config(tagtype, foreground=color)
                # print('tagtype:', tagtype, 'ind1:', ind1, 'ind2:', ind2, 'start:', start, 'end:', end, 'val:', val)


root.bind('<F5>', execute)

text.focus_force()

t_scroll_v.pack(side=RIGHT, fill=Y)
text.pack(side=TOP, expand=YES, fill=BOTH)

t_scroll_h.pack(side=TOP, fill=X)

c_scroll.pack(side=RIGHT, fill=Y)
console.pack(side=RIGHT, expand=YES, fill=BOTH)

output.pack(side=LEFT, anchor=S, expand=YES, fill=BOTH)
o_scroll.pack(side=RIGHT, fill=Y)

t_scroll_v.config(command=text.yview)
t_scroll_h.config(command=text.xview)
c_scroll.config(command=console.yview)
o_scroll.config(command=output.yview)

text.storeobj = {}

store = ColorLight(textbox=text)


def find_text(event=None):
    search_toplevel = Toplevel(root)
    search_toplevel.title('Find Text')
    search_toplevel.transient(root)

    Label(search_toplevel, text="Find All:").grid(row=0, column=0, sticky='e')

    search_entry_widget = Entry(search_toplevel, width=35)
    search_entry_widget.grid(row=0, column=1, padx=2, pady=2, sticky='we')
    search_entry_widget.focus_set()
    ignore_case_value, regex_value = IntVar(), IntVar()
    Checkbutton(search_toplevel, text='Ignore Case', variable=ignore_case_value).grid(row=1, column=1, sticky=W, padx=1,
                                                                                      pady=2)
    Checkbutton(search_toplevel, text='Regular Expression', variable=regex_value).grid(row=1, column=1, sticky=E,
                                                                                       padx=2, pady=2)
    Button(search_toplevel, text="Find All", underline=0,
           command=lambda: search_output(search_entry_widget.get(), ignore_case_value.get(), text, search_toplevel,
                                         search_entry_widget, regex_value.get())).grid(row=0, column=2, sticky=E+W,
                                                                                       padx=2, pady=2)

    def close_search_window(_event=None):
        text.tag_remove('match', '1.0', END)
        search_toplevel.destroy()
    search_toplevel.bind('<Escape>', close_search_window)
    search_toplevel.protocol('WM_DELETE_WINDOW', close_search_window)
    return "break"


def search_output(needle, if_ignore_case, _text, search_toplevel, search_box, regex):
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


def replace(event=None):
    replace_toplevel = Toplevel(root)
    replace_toplevel.title('Find and Replace Text')
    replace_toplevel.transient(root)
    replace_toplevel.resizable(False, False)

    Label(replace_toplevel, text="Find:", font=('Consolas 9')).grid(row=0, column=0, sticky=W, padx=2, pady=2)
    find_entry = Entry(replace_toplevel, width=40, font=('Consolas 12'))
    find_entry.grid(row=1, column=0, sticky=W, padx=2, pady=2)
    find_entry.focus_set()
    Label(replace_toplevel, text='Replace:', font=('Consolas 9')).grid(row=2, column=0, sticky=W, padx=2, pady=2)
    replace_entry = Entry(replace_toplevel, width=40, font=('Consolas 12'))
    replace_entry.grid(row=3, column=0, sticky=W, padx=2, pady=2)

    ignore_case_value, regex_value = IntVar(), IntVar()
    Checkbutton(replace_toplevel, text='Ignore Case', variable=ignore_case_value).grid(row=4, column=0, padx=2, pady=2,
                                                                                       sticky=W)
    Checkbutton(replace_toplevel, text='Regular Expression', variable=regex_value).grid(row=4, column=0, padx=2, pady=2,
                                                                                        sticky=E)
    Button(replace_toplevel, text='Find All', command=lambda: search_output(find_entry.get(), ignore_case_value.get(),
                                                                            text, replace_toplevel, find_entry,
                                                                            regex_value.get()),
           width=12).grid(row=1, column=1, padx=2, pady=2, sticky=E)
    Button(replace_toplevel, text='Replace All', command=lambda: replace_output(find_entry.get(), replace_entry.get(),
                                                                                text, ignore_case_value.get(),
                                                                                replace_toplevel, regex_value.get()),
           width=12).grid(row=2, column=1, padx=2, pady=2, sticky=E)
    
    def close_search_window(_event=None):
        replace_toplevel.destroy()
        text.tag_remove('match', '1.0', END)

    replace_toplevel.bind('<Escape>', close_search_window)
    replace_toplevel.bind('<Return>', lambda: replace_output(find_entry.get(), replace_entry.get(), text,
                                                             ignore_case_value.get(), replace_toplevel,
                                                             regex_value.get()))
    replace_toplevel.bind('<Shift-Return>', lambda a: search_output(find_entry.get(), ignore_case_value.get(), text,
                                                                    replace_toplevel, find_entry, regex_value.get()))
    replace_toplevel.protocol('WM_DELETE_WINDOW', close_search_window)
    return "break"


def replace_output(_find, _replace, _text, ignore, replace_box, regex):
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


def open_file(event=None):
    input_file_name = tkinter.filedialog.askopenfile(defaultextension=".txt", filetypes=FILETYPES)
    if input_file_name:
        global file_name
        file_name = input_file_name.name
        root.title('{} - {}'.format(file_name, PROGRAM_NAME))
        text.delete(1.0, END)
        with open(file_name) as _file:
            try:
                text.insert(1.0, _file.read())
            except UnicodeError or UnicodeTranslateError or UnicodeDecodeError or UnicodeEncodeError or UnicodeWarning:
                tkinter.messagebox.showerror('Can\'t open file', 'This error could be due to images in a file or some'
                                                                 ' characters that the program is unable to read')


def new_file(event=None):
    root.title("Untitled")
    global file_name
    file_name = None
    text.delete(1.0, END)
    output.delete(1.0, END)


def write_to_file(_file_name):
    try:
        content = text.get(1.0, 'end')
        with open(_file_name, 'w') as the_file:
            the_file.write(content)
    except IOError:
        tkinter.messagebox.showwarning("Save", "Could not save the file.")


def save_as(event=None):
    input_file_name = tkinter.filedialog.asksaveasfile(defaultextension=".py", filetypes=FILETYPES)
    if input_file_name:
        global file_name
        file_name = input_file_name.name
        write_to_file(file_name)
        root.title('{} - {}'.format(file_name, PROGRAM_NAME))
    return "break"


def save(event=None):
    global file_name
    if not file_name:
        save_as()
    else:
        write_to_file(file_name)
    return "break"


def undo_event(event=None):
    text.event_generate('<<Undo>>')
    text.edit_undo()


def redo_event(event=None):
    text.event_generate('<<Redo>>')
    text.edit_redo()


def wrap_none():
    text.config(wrap=None)


def wrap_word():
    text.config(wrap=WORD)


menubar = Menu(root)
file_menu = Menu(menubar, tearoff=0)
file_menu.add_command(label='New File', accelerator='Ctrl+N', command=new_file)
file_menu.add_command(label='Open', accelerator='Ctrl+O', command=open_file)
file_menu.add_command(label='Save', accelerator='Ctrl+S', command=save)
file_menu.add_command(label='Save As', command=save_as)
file_menu.add_command(label='Exit', accelerator='Alt+F4', command=lambda: root.destroy())
menubar.add_cascade(label='File', menu=file_menu)
edit_menu = Menu(menubar, tearoff=0)
edit_menu.add_command(label='Copy', accelerator='Ctrl+C', command=lambda: menubar.event_generate("<<Copy>>"))
edit_menu.add_command(label='Cut', accelerator='Ctrl+X', command=lambda: menubar.event_generate("<<Cut>>"))
edit_menu.add_command(label='Paste', accelerator='Ctrl+V', command=lambda: menubar.event_generate("<<Paste>>"))
edit_menu.add_command(label='Undo', accelerator='Ctrl+Z', command=undo_event)
edit_menu.add_command(label='Redo', accelerator='Ctrl+R', command=redo_event)
edit_menu.add_separator()
edit_menu.add_command(label='Word Wrap', command=lambda: wrap_word())
edit_menu.add_command(label='None Wrap', command=lambda: wrap_none())
menubar.add_cascade(label='Edit', menu=edit_menu)
config_menu = Menu(menubar, tearoff=0)
config_menu.add_command(label='Run', accelerator='F5', command=execute)
config_menu.add_command(label='Find', accelerator='Ctrl+F', command=find_text)
config_menu.add_command(label='Replace', accelerator='Ctrl+H', command=replace)
menubar.add_cascade(label='Config', menu=config_menu)
root.config(menu=menubar)


text.bind('<Control-Key-Tab>', on_ctab)
text.bind('<Control-N>', new_file)
text.bind('<Control-n>', new_file)
text.bind('<Control-O>', open_file)
text.bind('<Control-o>', open_file)
text.bind('<Control-S>', save)
text.bind('<Control-s>', save)
text.bind('<Control-f>', find_text)
text.bind('<Control-F>', find_text)
text.bind('<Control-H>', replace)
text.bind('<Control-h>', replace)
text.bind('<Control-z>', undo_event)
text.bind('<Control-Z>', undo_event)
text.bind('<Control-r>', redo_event)
text.bind('<Control-R>', redo_event)
text.bind('<KeyRelease-bracketleft>', lambda a: autocomplete(val='['))
text.bind('<KeyRelease-braceleft>', lambda a: autocomplete(val='{'))
text.bind('<KeyRelease-parenleft>', lambda a: autocomplete(val='('))
text.bind('<KeyRelease-bracketright>', lambda a: autocomplete(val=']'))
text.bind('<KeyPress-bracketright>', lambda a: autocomplete(val=']'))
text.bind('<KeyRelease-braceright>', lambda a: autocomplete(val='}'))
text.bind('<KeyPress-braceright>', lambda a: autocomplete(val='}'))
text.bind('<KeyRelease-parenright>', lambda a: autocomplete(val=')'))
text.bind('<KeyPress-parenright>', lambda a: autocomplete(val=')'))
text.bind('<KeyRelease-colon>', lambda x: autocomplete(':'))
console.bind('<Control-Key-Tab>', on_ctab)


root.mainloop()
