from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
import keyword
import builtins
import re
# from code import InteractiveInterpreter
import json
from ctypes import windll
from LineNumberCanvas import LineNumberCanvas


# class StdoutRedirector(object):
#     def __init__(self, text_widget):
#         self.text_space = text_widget
#
#     def write(self, string):
#         self.text_space.insert('end', string)
#         self.text_space.see('end')


class ColorText(Text):
    FILETYPES = [("Python File", "*.py"), ("Text Documents", "*.txt"), ("Markdown File", "*.md"), ("All Files", "*.*")]

    def __init__(self, master, **kwargs):
        Text.__init__(self, master, **kwargs)
        self.root = master

        with open('./config.json') as file:
            self.config_dict = json.load(file)
        self.config(font=self.config_dict['color_text_font'])
        self.theme = self.config_dict['themes'][self.config_dict['selected_theme']].split('.')
        self.config(fg=self.theme[0], bg=self.theme[1], insertbackground=self.theme[2],
                    undo=1, selectbackground=self.theme[3])
        #            tabs=str(0.95*(int(self.config_dict['tab_length'])/4))+'c')

        self.linenumbers = LineNumberCanvas(self.master, width=15)

        self.PROGRAM_NAME = 'EZ_PY'
        self.file_name = None
        self.FILETYPES = [("Python File", "*.py"), ("Text Documents", "*.txt"), ("All Files", "*.*")]

        self.storeobj = {}

        self.module_list = self.__list()
        self.executing = False

        self.mechanise()
        self._set_()
        self.binding_keys()
        self.up_date()
        self.toggle_highlight()
        self.linenum_width()

        with open('importable_modules', 'w') as imp_mods:
            for i in self.module_list:
                if ' ' not in i and '{' not in i and '}' not in i:
                    imp_mods.write(i+'\n')

        self.textfilter = re.compile(self.sort_regex(), re.S)

        # self.after(2000, self.color_code_block)

        self.bind('<Control-Shift-N>', self.new_file)
        self.bind('<Control-o>', self.open_file)
        self.bind('<Control-s>', self.save)
        self.bind('<Control-f>', self.find_text)
        self.bind('<Control-r>', self.re_place)
        self.bind('<Control-z>', self.undo_event)
        self.bind('<Control-Shift-Z>', self.redo_event)
        self.bind('<KeyPress-bracketleft>', lambda a: self.autocomplete(val='['))
        self.bind('<KeyPress-braceleft>', lambda a: self.autocomplete(val='{'))
        self.bind('<KeyPress-parenleft>', lambda a: self.autocomplete(val='('))
        self.bind('<KeyPress-bracketright>', lambda a: self.autocomplete(val=']'))
        self.bind('<KeyPress-braceright>', lambda a: self.autocomplete(val='}'))
        self.bind('<KeyPress-parenright>', lambda a: self.autocomplete(val=')'))
        self.bind('<KeyPress-quoteright>', lambda a: self.autocomplete(val="'"))
        self.bind('<KeyPress-quotedbl>', lambda a: self.autocomplete(val='"'))
        self.bind('<KeyPress-less>', lambda a: self.autocomplete(val='<'))
        self.bind('<KeyPress-greater>', lambda a: self.autocomplete(val='>'))
        self.bind('<KeyPress-colon>', lambda a: self.autocomplete(val=':'))
        self.bind('<KeyPress-BackSpace>', self.on_bkspace)
        self.bind('<KeyRelease>', self.trigger)
        self.bind('<Tab>', self.on_tab)
        # self.bind('<Control_R>', self.color_code_block)
        # self.bind('<Control_L>', self.color_code_block)
        self.bind('<Return>', self.on_return)
        # self.bind('<Shift_R>', self.color_code_block)
        # self.bind('<Shift_L>', self.color_code_block)
        self.bind('<Button-3>', self.r_click, add='')
        self.bind('<Home>', self.on_home)
        self.bind('<Control-Home>', self.on_ctrl_home)
        self.bind('<Shift-Home>', self.on_shift_home)
        self.bind('<Delete>', self.on_delete)
        # self.bind('<<NextChar>>', self.on_next_char)
        # self.bind('<<PrevChar>>', self.on_prev_char)
        # self.bind('<F5>', self.execute)
        self.bind('<<Selection>>', self.on_select)
        self.bind('<<SelectNone>>', self.on_select_remove)
        self.bind('<<Paste>>', lambda _=None: self.after(12, self.on_paste))
        # self.bind('<<NextPara>>', on_para_change)      <=
        # self.after(4000, self.color_code_block)
        self.bind('<FocusIn>', self.inst_trigger)

    def __list(self) -> list:
        modules = []
        import pkgutil
        for i in pkgutil.iter_modules():
            modules.append(i.name)
        in_modules = sys.modules.keys()
        modules = list(modules+list(in_modules))
        for i in modules:
            if '[' in i or ']' in i or '(' in i or ')' in i or '{' in i or '}' in i:
                modules.pop(modules.index(i))
        return sorted(modules)

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
        # self.edit_undo()
        self.inst_trigger()
        return 'break'

    def redo_event(self, event=None):
        self.event_generate('<<Redo>>')
        # self.edit_redo()
        self.inst_trigger()
        return 'break'

    def autocomplete(self, val):
        if val == '(':
            self.insert(INSERT, ')')
            self.mark_set(INSERT,
                          f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")
            self.current_bracket()
            
        elif val == '{':
            self.insert(INSERT, '}')
            self.mark_set(INSERT,
                          f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")
            self.current_bracket()
            
        elif val == '[':
            self.insert(INSERT, ']')
            self.mark_set(INSERT,
                          f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")
            self.current_bracket()
            
        # elif val == '<':
            # self.insert(INSERT, '>')
            # self.mark_set(INSERT,
        # f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")
            
        elif val == ')':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == ')':
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
                self.current_bracket()
                # re.match(r'\s*\([^)]+\)', self.get("insert linestart", "insert lineend"))
                
            else:
                self.current_bracket()
                return ')'
            
            return 'break'
        
        elif val == '}':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == '}':
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
                self.current_bracket()
                
            else:
                self.current_bracket()
                return '}'
            
            return 'break'
        
        elif val == ']':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == ']':
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
                self.current_bracket()
                
            else:
                self.current_bracket()
                return ']'
            
            return 'break'
        
        # elif val == '>':
            # if self.get(self.index(INSERT),
        # f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == '>':
            # self.mark_set(INSERT,
        # f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")

            # else:
            # return '>'
            
            # return 'break'
        
        elif val == '"':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == '"':
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
                return 'break'
            
            else:
                if \
                        self.get(f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}",
                                 self.index(INSERT)) in \
                        ['', ' ', '(', '[', '{', '=', ',', 'B', 'br', 'Br', 'bR', 'BR', 'rb', 'rB', 'Rb', 'RB',
                         'r', 'u', 'R', 'U', 'f', 'F', 'fr', 'Fr', 'fR', 'FR', 'rf', 'rF', 'Rf', 'RF']:
                    self.insert(INSERT, '"')
                    self.mark_set(
                        INSERT, f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")

        elif val == "'":
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == "'":
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
                return 'break'
            
            else:
                if \
                        self.get(f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1])-1}",
                                 self.index(INSERT)) in \
                        ['', ' ', '(', '[', '{', '=', ',', 'B', 'br', 'Br', 'bR', 'BR', 'rb', 'rB', 'Rb', 'RB',
                         'r', 'u', 'R', 'U', 'f', 'F', 'fr', 'Fr', 'fR', 'FR', 'rf', 'rF', 'Rf', 'RF']:
                    self.insert(INSERT, "'")
                    self.mark_set(
                        INSERT, f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) - 1}")

        elif val == ':':
            if self.get(self.index(INSERT),
                        f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}") == ":":
                self.mark_set(INSERT,
                              f"{int(self.index(INSERT).split('.')[0])}.{int(self.index(INSERT).split('.')[1]) + 1}")
                return 'break'

        return

    def current_bracket(self):
        start_char = (self.index(INSERT), self.index(INSERT+'+1c'))
        end_char = (self.index(INSERT+'-1c'), self.index(INSERT))
        self.tag_add('bracket', start_char[0], start_char[1])
        self.tag_add('bracket', end_char[0], end_char[1])
        self.tag_config('bracket', )
        # print(self.index(INSERT+'-1c'), self.index(INSERT), self.index(INSERT+'+1c'))

    def check_paren(self, string):
        open_list = ["[", "{", "("]
        close_list = ["]", "}", ")"]
        stack = []

        for i in string:
            if i in open_list:
                stack.append(i)
            elif i in close_list:
                pos = close_list.index(i)

                if ((len(stack) > 0) and (open_list[pos] == stack[len(stack)-1])):
                    stack.pop()
                else:
                    return False

        if len(stack) == 0:
            return True
        else:
            return False

    def find_indent(self, string, value=4) -> dict:
        """returns indent level and spaces for single line `string` value"""
        indent_spaces = 0
        for i in string:
            if i.isspace():
                indent_spaces += 1
            elif not i.isspace():
                break
        return {'spaces': indent_spaces, 'level': indent_spaces//value}

    def toggle_highlight(self, event=None):
        select = self.tag_ranges(SEL)
        # print(select, len(select))
        if len(select) > 0:
            self.highlight_current_line(False)
            return
        self.highlight_current_line(self.config_dict['highlight_current_line'])

    def highlight_current_line(self, event=None):
        if event is True:
            self.tag_remove('active_line', '1.0', END)
            self.tag_add('active_line', 'insert linestart', 'insert lineend+1c')
            self.tag_config(
                'active_line', background=self.config_dict['text_theme_settings'][
                    self.config_dict['selected_theme']]['hcl_color'])
            self.after(25, self.toggle_highlight)
        else:
            self.tag_remove('active_line', 1.0, END)
            self.after(25, self.toggle_highlight)

    def on_return(self, event=None):
        prev_line = self.get(f"{int(self.index(INSERT).split('.')[0])}.0", INSERT)
        # after_line = self.get(INSERT, INSERT+' lineend')
        prev_indent = int(self.find_indent(prev_line, value=self.config_dict['tab_length'])['spaces'])
        # print(self.index('1.0 lineend'))

        if prev_line.rstrip('\t').rstrip(' ').endswith(':') and not prev_line.rstrip('\t').rstrip(' ').startswith('#'):
            self.insert(INSERT, '\n')
            self.insert(f"{int(self.index(INSERT).split('.')[0])}.0",
                        ' '*(prev_indent+self.config_dict['tab_length']))  # +after_line)
            self.see(INSERT)
            return 'break'

        elif len(prev_line) > 0 and prev_line[-1] in ['(', '[', '{']:

            if self.get(INSERT, f"{int(self.index(INSERT).split('.')[0])}."
                                f"{int(self.index(INSERT).split('.')[1])+1}") in [')', ']', '}']:
                self.insert(INSERT, '\n')
                self.insert(INSERT, ' '*(prev_indent+self.config_dict['tab_length']))
                self.insert(INSERT, '\n')
                self.insert(INSERT, ' '*prev_indent)
                self.mark_set(INSERT, f"{int(self.index(INSERT).split('.')[0])-1}.0 lineend")
            else:
                self.insert(INSERT, '\n')
                self.insert(f"{int(self.index(INSERT).split('.')[0])}.0",
                            ' '*(prev_indent+self.config_dict['tab_length']))
                if self.get(self.index('insert lineend-1c'), self.index('insert lineend')) in [')', '}', ']']:
                    self.insert(self.index('insert lineend-1c'), '\n')
                    self.insert(self.index('insert lineend+1c'), ' '*prev_indent)
            self.see(INSERT)
            return 'break'

        elif len(prev_line) > 0 and prev_line.rstrip()[-1] in [',', '\\']:
            ind = prev_line.rfind('(')
            if ind < 0:
                ind = prev_line.rfind('[')
                if ind < 0:
                    ind = prev_line.rfind('{')
            if ind > 0:
                self.insert(INSERT, '\n')
                space_strip_text = self.get(INSERT, 'insert lineend')
                self.delete(INSERT, 'insert lineend')
                self.insert(INSERT, ' ' * (ind + 1) + space_strip_text.lstrip())
                self.mark_set(INSERT, f'insert linestart+{ind+1}c')
            else:
                self.insert(INSERT, '\n')
                space_strip_text = self.get(INSERT, 'insert lineend')
                self.delete(INSERT, 'insert lineend')
                self.insert(INSERT, ' ' * prev_indent + space_strip_text.lstrip())
                self.mark_set(INSERT, f'insert linestart+{prev_indent}c')
            self.see(INSERT)
            return 'break'

        elif 'return' in prev_line or 'pass' in prev_line or 'continue' in prev_line or \
             'yield' in prev_line or 'break' in prev_line:
            self.insert(INSERT, '\n')
            self.insert(f"{int(self.index(INSERT).split('.')[0])}.0",
                        ' ' * (prev_indent - self.config_dict['tab_length']))
            self.see(INSERT)
            return 'break'

        elif self.check_paren(prev_line) is True:
            self.insert(INSERT, '\n')
            self.insert(f"{int(self.index(INSERT).split('.')[0])}.0", ' '*(prev_indent))
            self.see(INSERT)
            return 'break'
        else:
            self.insert(INSERT, '\n')
            self.insert(f"{int(self.index(INSERT).split('.')[0])}.0", ' '*(prev_indent))
            self.see(INSERT)
            return 'break'

    def on_home(self, event):
        cur_line = self.get(f"{int(self.index(INSERT).split('.')[0])}.0", INSERT+' lineend')
        if cur_line.count('\t') == 0 and cur_line.startswith(' '):
            s1 = cur_line.lstrip()
            cur_indent = int(len(cur_line) - len(s1))
        else:
            cur_indent = int(cur_line.count('\t'))
        cur_row = int(self.index(INSERT).split('.')[0])

        # print(cur_row, cur_indent, cur_line)
        # print(self.index(INSERT), float(f'{cur_row}.{cur_indent}'))

        if int(str(self.index(INSERT)).split('.')[0]) == cur_row and \
                int(str(self.index(INSERT)).split('.')[1]) == cur_indent:
            self.mark_set(INSERT, f'{cur_row}.0')
            return 'break'

        elif int(str(self.index(INSERT)).split('.')[0]) == cur_row and int(str(self.index(INSERT)).split('.')[1]) == 0:
            self.mark_set(INSERT, f'{cur_row}.{cur_indent}')
            return 'break'

        else:
            self.mark_set(INSERT, f'{cur_row}.{cur_indent}')

    def on_ctrl_home(self, event):
        self.mark_set(INSERT, index='1.0')

    def on_shift_home(self, event):
        self.tag_add('<<SelectLineStart>>', INSERT, INSERT+' linestart')

    def on_tab(self, event):
        self.insert(INSERT, ' '*self.config_dict['tab_length'])
        return 'break'

    def on_bkspace(self, event):
        """:params: event: parameter for backspace event list"""
        cur_ind = str(self.index(INSERT))
        one_less_char = self.get(f"{int(cur_ind.split('.')[0])}.{int(cur_ind.split('.')[1])-1}", INSERT)
        one_less_char_ind = f"{int(cur_ind.split('.')[0])}.{int(cur_ind.split('.')[1])-1}"
        one_more_char = self.get(INSERT, f"{int(cur_ind.split('.')[0])}.{int(cur_ind.split('.')[1])+1}")
        one_more_char_ind = f"{int(cur_ind.split('.')[0])}.{int(cur_ind.split('.')[1])+1}"
        open_bracs, close_bracs = ['{', '[', '('], ['}', ']', ')']

        if one_less_char in ['"', "'"]:
            if one_more_char == one_less_char:
                self.delete(cur_ind, one_more_char_ind)
        elif one_less_char in open_bracs:
            if one_more_char == close_bracs[open_bracs.index(one_less_char)]:
                self.delete(cur_ind, one_more_char_ind)

        if one_less_char.isspace() is False:
            return

        target_ind = f"{cur_ind.split('.')[0]}.{str(int(cur_ind.split('.')[1]) - 4)}"
        del_chars = 0
        for i in self.get(target_ind, cur_ind):
            if i.isspace():
                del_chars += 1
            elif i.isalnum():
                del_chars -= 1
        if del_chars <= 0:
            del_chars = 1
        self.delete(f"{cur_ind.split('.')[0]}.{str(int(cur_ind.split('.')[1]) - del_chars)}", self.index(INSERT))
        return 'break'

    def on_delete(self, event):
        """:params: event: parameter for delete event list"""
        pass
    #     cur_ind = str(self.index(INSERT))
    #     one_less_char = self.get(f"{int(cur_ind.split('.')[0])}.{int(cur_ind.split('.')[1]) - 1}", INSERT)
    #     one_less_char_ind = f"{int(cur_ind.split('.')[0])}.{int(cur_ind.split('.')[1]) - 1}"
    #     one_more_char = self.get(INSERT, f"{int(cur_ind.split('.')[0])}.{int(cur_ind.split('.')[1]) + 1}")
    #     one_more_char_ind = f"{int(cur_ind.split('.')[0])}.{int(cur_ind.split('.')[1]) + 1}"
    #     open_bracs, close_bracs = ['{', '[', '('], ['}', ']', ')']

    def on_paste(self, event=None):
        # cur_ind = str(self.index(INSERT))
        # text = self.clipboard_get()
        # lines = int(text.count('\n'))
        # self.insert(cur_ind, text)
        # last_ind = f"{str(int(cur_ind.split('.')[0]) + lines)}.0"
        self.inst_trigger()
        self.see(INSERT)
        # return 'break'

    def on_next_char(self, event):
        cur_char = self.get(self.index(INSERT), self.index(INSERT+'+1c'))
        next_char = self.get(self.index(INSERT+'+1c'), self.index(INSERT+'+2c'))
        # print(cur_char, next_char)

    def on_prev_char(self, event):
        # cur_char = self.get(self.index(INSERT), self.index(INSERT+'+1c'))
        prev_char = self.get(self.index(INSERT+'-1c'), self.index(INSERT))
        # print(cur_char, prev_char)

    def on_select(self, event=None):
        if self.tag_ranges(SEL) == ():
            self.tag_remove('similar_selection', 1.0, END)
            return
        selected_text_ind = [self.tag_ranges(SEL)[0], self.tag_ranges(SEL)[1]]
        selected_text = self.get(selected_text_ind[0], selected_text_ind[1])
        if selected_text.strip() in ['', ' ', '\t', '\n']:
            return
        self.tag_remove('similar_selection', 1.0, END)
        start_pos = '1.0'
        while True:
            start_pos = self.search(selected_text, start_pos, nocase=False, exact=True, stopindex=END)
            if not start_pos:
                break
            end_pos = "{}+{}c".format(start_pos, len(selected_text))
            self.tag_add('similar_selection', start_pos, end_pos)
            if start_pos == selected_text_ind[0]:
                pass
            else:
                start_pos = end_pos
        self.tag_config('similar_selection', background=self.theme[4])
        self.tag_remove('similar_selection', selected_text_ind[0], selected_text_ind[1])
        self.tag_config(SEL, background=self.theme[3])

    def on_select_remove(self, event=None):
        self.tag_remove('similar_selection', 1.0, END)

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

    def re_place(self, event=None):
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
        self.inst_trigger()
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

    # def execute(self, event=None):
        # output = Toplevel(self, width=200, height=200)
        # output.title('Output Window')
        # output_win = Console(output, locals(), output.destroy)

        # if self.executing is True:
            # self.save()
            # code = self.get('1.0', END + '-1c')
            # stdin = sys.stdin
            # stdout = sys.stdout
            # stderr = sys.stderr

            # sys.stdout = StdoutRedirector(output_win)
            # sys.stderr = StdoutRedirector(output_win)

            # interp = InteractiveInterpreter()
            # interp.runcode(code)

            # sys.stdout = stdout
            # sys.stderr = stderr
            # sys.stdin = stdin
        # else:
            # self.save()

            # self.executing = True
            # output_win.pack(side=BOTTOM, expand=TRUE, fill=BOTH)

            # code = self.get('1.0', END + '-1c')
            # stdin = sys.stdin
            # stdout = sys.stdout
            # stderr = sys.stderr

            #    def a():
            #        sys.stdin = StdinRedirector(output)
            #    output.bind('<Return>', lambda: a)

            # sys.stdout = StdoutRedirector(output_win)
            # sys.stderr = StdoutRedirector(output_win)

            # interp = InteractiveInterpreter()
            # interp.runcode(code)

            # sys.stdout = stdout
            # sys.stderr = stderr
            # sys.stdin = stdin

    def _any(self, name, alternates):
        """Return a named group pattern matching list of alternates."""
        return "(?P<%s>" % name + "|".join(alternates) + ")"

    def sort_regex(self):
        """Returns a compiled list of all the regex alternates for group pattern matching"""

        # Regex for list of Python keywords
        kw = r"\b" + self._any("KEYWORD", keyword.kwlist) + r"\b"

        # Regex for list of Python built-in functions
        builtinlist = [str(name) for name in dir(builtins) if not name.startswith('_') and name not in keyword.kwlist]
        builtin = r"([^.'\"\\#]\b|^)" + self._any("BUILTIN", builtinlist) + r"\b"

        # Regex for comments
        comment = self._any("COMMENT", [r"#[^\n]*|@[^ ][^\n][^ ]*"])

        # Regex for Python strings
        stringprefix = r"(\bB|b|br|Br|bR|BR|rb|rB|Rb|RB|r|u|R|U)?"
        sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
        dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
        sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
        dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
        string = self._any("STRING", [sq3string, dq3string, sqstring, dqstring])

        # Regex for natural, exponential, decimal, hexadecimal numbers
        numbers = self._any(
            "NUMBERS", [r'0(?:[0x|0X][a-fA-F0-9]+)|\b[-|+]?(?:\b[0-9]+(?:\.[0-9]*)?|\.[0-9]+\b)(?:[eE][-+]?[0-9]+\b)?\b'
                        ])

        # Regex for special characters
        speciallist = ['=', '@', '-', ':', '<', '>', r'[+]', r'[*]', r'[.]', r'[!]', r'[%]', r'[\\]']
        special = self._any("SPECIAL", speciallist)

        # Regex for brackets
        bracketlist = [r'[(]', r'[)]', r'[{]', r'[}]', r'[[]', r'[]]']
        bracket = self._any("BRACKET", bracketlist)

        # definitions = self._any("CLASSDEF", [r"(\bdef|class)?[^'\\\n]*(\\.[^'\\\n]*)*(:\b)?"])

        # Regex for module list on a system
        modules = r"([^.'\"\\#]\b|^)" + self._any('MODULES', self.module_list) + r"\b"

        # Regex for Python dunders or double underlined keywords
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

        return kw + "|" + builtin + "|" + comment + '|' + string + "|" + numbers + '|' + special + '|' + bracket +\
            '|' + modules + '|' + dunder + '|' + self._any("SYNC", [r"\n"])

    def _coordinate(self, start, end, string):
        """Returns indices of the start and end of matched `string`"""
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

    def check(self, k: dict):
        font = list(self.config_dict['color_text_font'])
        if k['COMMENT'] is not None:
            return (
                'comment', self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['comment'][0],
                f"{font[0]} {font[1]}" +
                f" {self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['comment'][1]}")

        elif k['BUILTIN'] is not None:
            return (
                'builtin', self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['builtin'][0],
                f"{font[0]} {font[1]}" +
                f" {self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['builtin'][1]}")

        elif k['STRING'] is not None:
            return (
                'string', self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['string'][0],
                f"{font[0]} {font[1]}" +
                f" {self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['string'][1]}")

        elif k['KEYWORD'] is not None:
            return (
                'keyword', self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['keyword'][0],
                f"{font[0]} {font[1]}" +
                f" {self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['keyword'][1]}")

        elif k['NUMBERS'] is not None:
            return (
                'numbers', self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['numbers'][0],
                f"{font[0]} {font[1]}" +
                f" {self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['numbers'][1]}")

        elif k['SPECIAL'] is not None:
            return (
                'special', self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['special'][0],
                f"{font[0]} {font[1]}" +
                f" {self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['special'][1]}")


        elif k['BRACKET'] is not None:
            return (
                'bracket', self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['bracket'][0],
                f"{font[0]} {font[1]}" +
                f" {self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['bracket'][1]}")

        elif k['MODULES'] is not None:
            return (
                'modules', self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['modules'][0],
                f"{font[0]} {font[1]}" +
                f" {self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['modules'][1]}")

        elif k['DUNDER'] is not None:
            return (
                'dunder', self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['dunder'][0],
                f"{font[0]} {font[1]}" +
                f" {self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['dunder'][1]}")

        # elif k['CLASSDEF'] is not None:
        #     return 'classdef', '#0000ff'

        # elif k['LINK'] is not None:
        #     return (
        #         'link', self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['link'][0],
        #         f"{font[0]} {font[1]}" +
        #         f" {self.config_dict['text_theme_settings'][self.config_dict['selected_theme']]['link'][1]}")
        else:
            return 'ss', 'NILL', 'NILL'

    def binding_functions_configuration(self):
        self.storeobj['ColorLight'] = self.trigger
        return

    def trigger(self, event=None):
        val = self.get(INSERT + ' linestart', INSERT + ' lineend')
        # print(val, self.text.index(INSERT+' linestart'), self.text.index(INSERT+' lineend'))
        if len(val) == 1:
            return

        for i in ['comment', 'builtin', 'string', 'keyword', 'numbers', 'special', 'bracket', 'modules', 'dunder']:
            self.tag_remove(i, INSERT + ' linestart', INSERT + ' lineend')

        for i in self.textfilter.finditer(val):
            start = i.start()
            end = i.end() - 1
            tagtype, color, font_style = self.check(k=i.groupdict())
            # print(tagtype, color, font_style)
            if color != 'NILL':
                ind1, ind2 = self._coordinate(start=start, end=end, string=val)
                self.tag_add(tagtype,
                             f"{int(self.index(INSERT).split('.')[0])}.{str(ind1).split('.')[1]}",
                             f"{int(self.index(INSERT).split('.')[0])}.{str(ind2).split('.')[1]}")
                self.tag_config(tagtype, foreground=color, font=font_style)
                # print('tagtype:', tagtype, 'ind1:', ind1, 'ind2:', ind2, 'start:', start, 'end:', end, 'val:',val)

    # def color_code_block(self, event=None):
    #     self.update()
    #     self.update_idletasks()
    #     cur_ind = self.index(INSERT)
    #     cur_ind_bbox = self.bbox(cur_ind)
    #     self.event_generate('<<PrevPara>>')
    #     prev_para_ind = self.index(INSERT)
    #     self.event_generate('<<NextPara>>')
    #     next_para_ind = self.index(INSERT)
    #     self.inst_trigger(start=prev_para_ind, stop=next_para_ind)
    #     self.mark_set(INSERT, cur_ind)
    #     self.see(INSERT)
    #     # print(cur_ind, prev_para_ind, next_para_ind)
    #     # print(cur_ind_bbox)
    #     self.after(5000, self.color_code_block)

    def inst_trigger(self, event=None, start='1.0', stop=END):
        val = self.get(start, stop)
        if len(val) == 1:
            return

        for i in ['comment', 'builtin', 'string', 'keyword', 'numbers', 'special', 'bracket', 'modules', 'dunder']:
            self.tag_remove(start, stop)

        for i in self.textfilter.finditer(val):
            _start = i.start()
            end = i.end() - 1
            tagtype, color, font_style = self.check(k=i.groupdict())
            # print(tagtype, color, font_style)
            if color != 'NILL':
                ind1, ind2 = self._coordinate(start=_start, end=end, string=val)
                self.tag_add(tagtype, ind1, ind2)
                self.tag_config(tagtype, foreground=color, font=font_style)
            # self.tag_bind('link', '<Control-Button-1>', self.open_link)
            # self.tag_bind('link', '<Double-1>', self.open_link)
            # self.tag_configure('link', foreground='#0000ff')
            # self.tag_raise('link', 'string')
            # self.tag_raise('link', 'comment')
        return 'break'

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
        self.linenumbers.connect(self)
        self.linenumbers.pack(side=LEFT, fill=Y)
        return

    def changed(self, event):
        self.linenumbers.re_render()
        return

    def binding_keys(self):
        for key in ['<Down>', '<Up>', "<<Changed>>", "<Configure>", '<Home>', '<End>', '<Prior>', '<Control_L>',
                    '<Next>', '<Control_R>']:
            self.bind(key, self.changed)
        self.linenumbers.bind('<Button-1>', self.linenumbers.get_breakpoint_number)
        return


    def r_click(self, event):
        """right click context menu for all Tk Entry and Text widgets"""
        try:
            def r_click_copy(evnt, apnd=0):
                evnt.widget.event_generate('<Control-c>')

            def r_click_cut(evnt):
                evnt.widget.event_generate('<Control-x>')

            def r_click_paste(evnt):
                evnt.widget.event_generate('<Control-v>')
                self.inst_trigger()

            event.widget.focus()

            nclst = [
                     (' Cut', lambda evt=event: r_click_cut(evt)),
                     (' Copy', lambda evt=event: r_click_copy(evt)),
                     (' Paste', lambda evt=event: r_click_paste(evt)),
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

    def linenum_width(self, event=None):
        if self.linenumbers.temp is not None:
            self.linenumbers.configure(width=len(self.linenumbers.temp.split('.')[0])*10+5, bg=self.theme[1])
        self.after(10, self.linenum_width)

    def up_date(self, event=None):
        with open('config.json') as _file:
            self.config_dict = json.load(_file)
        self.theme = self.config_dict['themes'][self.config_dict['selected_theme']].split('.')
        self.config(fg=self.theme[0], bg=self.theme[1], insertbackground=self.theme[2])
        #           tabs=str(0.95*(int(self.config_dict['tab_length'])/4))+'c')
        
        # self.linenumbers.id.config(fill=self.theme[0])
        # print(self.dlineinfo(INSERT))

        self.after(1500, self.up_date)


class TestApp(Tk):
    def __init__(self, *args, **kwargs):
        import tkinter.ttk as ttk
        
        Tk.__init__(self, *args, **kwargs)
        self.overrideredirect(True)
        self.minsize(193, 109)
        self.x = None
        self.y = None

        self.frame = Frame(self, bg='gray38')
        self.frame.pack(side=TOP, fill=X)
        self.name = Label(self.frame, text='Color Text', font='Consolas 11',
                          bg=self.frame.cget('background'), fg='white')
        self.name.pack(side=LEFT, fill=X, anchor=CENTER)
        self.close = Button(self.frame, text='✕', bd=0, width=3, font='Consolas 13',
                            command=lambda: self.destroy(), bg=self.frame.cget('background'))
        self.close.pack(side=RIGHT)
        self.maximize = Button(self.frame, text=u"\U0001F5D6", bd=0, width=3, font='Consolas',
                               command=self.maximize_win, bg=self.frame.cget('background'))
        self.maximize.pack(side=RIGHT)
        self.minimize = Button(self.frame, text='—', bd=0, width=3, font='Consolas 13',
                               command=self.minimize_win, bg=self.frame.cget('background'))
        self.minimize.pack(side=RIGHT)

        self.scroll_frame = Frame(self)
        v_scroll = Scrollbar(self.scroll_frame, orient=VERTICAL)
        h_scroll = Scrollbar(self, orient=HORIZONTAL)
        self.grip = ttk.Sizegrip(self.scroll_frame)

        self.text = ColorText(self, wrap=NONE, yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.config(command=self.text.yview)
        h_scroll.config(command=self.text.xview)

        self.scroll_frame.pack(side=RIGHT, fill=Y)
        v_scroll.pack(side=TOP, fill=Y, expand=Y)
        self.grip.pack(side=BOTTOM)
        self.text.pack(side=TOP, expand=TRUE, fill=BOTH)
        h_scroll.pack(side=BOTTOM, fill=X)
        
        # self.grip.lift(self.label)
        self.grip.bind("<B1-Motion>", self.onmotion)

        self.call('encoding', 'system', 'utf-8')

        self.close.bind('<Enter>', lambda _: self.close.config(bg='red'))
        self.close.bind('<Leave>', lambda _: self.close.config(bg=self.frame.cget('background')))
        self.minimize.bind('<Enter>', lambda _: self.minimize.config(bg='gray58'))
        self.minimize.bind('<Leave>', lambda _: self.minimize.config(bg=self.frame.cget('background')))
        self.maximize.bind('<Enter>', lambda _: self.maximize.config(bg='gray58'))
        self.maximize.bind('<Leave>', lambda _: self.maximize.config(bg=self.frame.cget('background')))
        self.frame.bind("<ButtonPress-1>", self.start_move)
        self.frame.bind("<ButtonRelease-1>", self.stop_move)
        self.frame.bind("<B1-Motion>", self.do_move)
        self.frame.bind('<Double-1>', self.maximize_win)
        self.name.bind("<ButtonPress-1>", self.start_move)
        self.name.bind("<ButtonRelease-1>", self.stop_move)
        self.name.bind("<B1-Motion>", self.do_move)
        self.name.bind('<Double-1>', self.maximize_win)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        self.wm_state('normal')
        self.maximize.config(text=u"\U0001F5D6")
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def onmotion(self, event):
        self.wm_state('normal')
        self.maximize.config(text=u"\U0001F5D6")
        x1 = self.winfo_pointerx()
        y1 = self.winfo_pointery()
        x0 = self.winfo_rootx()
        y0 = self.winfo_rooty()
        self.geometry("%sx%s" % ((x1-x0), (y1-y0)))
        return

    def minimize_win(self, event=None):
        self.overrideredirect(False)
        self.wm_iconify()
        self.bind('<FocusIn>', self.on_deiconify)

    def maximize_win(self, event=None):
        if self.maximize.cget('text') == u"\U0001F5D7":
            self.wm_state('normal')
            self.maximize.config(text=u"\U0001F5D6")
            return
        self.wm_state('zoomed')
        self.maximize.config(text=u"\U0001F5D7")

    def on_deiconify(self, event):
        self.overrideredirect(True)
        set_appwindow(root=self)


def set_appwindow(root):
    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
    # re-assert the new window style
    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())


if __name__ == '__main__':
    GWL_EXSTYLE = -20
    WS_EX_APPWINDOW = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080
    app = TestApp()
    app.title('Color Text')
    app.tk.call('tk', 'windowingsystem')
    app.after(10, lambda: set_appwindow(root=app))
    app.focus_force()
    app.text.focus_force()
    app.mainloop()
