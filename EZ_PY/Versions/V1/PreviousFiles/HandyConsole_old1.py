from tkinter import *
from code import InteractiveConsole
from io import StringIO
from contextlib import redirect_stderr, redirect_stdout
import queue
import sys
# import time
# import threading
# import traceback
# import code
# import subprocess
from tkinter import Text as ColorText


class History(list):
    def __getitem__(self, index):
        try:
            print(list.__getitem__(self, index))
            return list.__getitem__(self, index)
        except IndexError:
            return


class Pipe:
    """mock stdin stdout or stderr"""

    def __init__(self):
        self.buffer = queue.Queue()
        self.reading = False

    def write(self, data):
        self.buffer.put(data)

    def flush(self):
        pass

    def readline(self):
        self.reading = True
        line = self.buffer.get()
        self.reading = False
        return line


class TextConsole(ColorText):
    def __init__(self, master, **kw):
        kw.setdefault('width', 50)
        kw.setdefault('wrap', 'word')
        kw.setdefault('prompt1', '>>> ')
        kw.setdefault('prompt2', '    ')
        banner = kw.pop('banner', 'Python %s\n' % sys.version)
        self._prompt1 = kw.pop('prompt1')
        self._prompt2 = kw.pop('prompt2')
        ColorText.__init__(self, master, **kw)
        # --- history
        self.history = History()
        self._hist_item = 0
        self._hist_match = ''

        # --- initialization
        self._console = InteractiveConsole()  # python console to execute commands
        sys.stdin = Pipe()
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
        self.unbind('<Control-Shift-Home>')
        self.unbind('<Control-Shift-End>')

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
        if sys.stdin.reading:
            pass
        if result:
            self.insert('end', self._prompt2, 'prompt')
        else:
            self.insert('end', self._prompt1, 'prompt')
        self.mark_set('input', 'end-1c')

    def on_key_press(self, event):
        """Prevent text insertion in command history"""
        # self.trigger(event=event)
        if self.compare('insert', '<', 'input') and event.keysym not in ['Left', 'Right']:
            self._hist_item = len(self.history)
            self.mark_set('insert', 'input lineend')
            if not event.char.isalnum():
                return 'break'

    def on_key_release(self, event):
        """Reset history scrolling"""
        # self.trigger(event=event)
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
            # self.inst_trigger()
            return 'break'
        else:
            self.eval_current(True)
            self.see('end')
            # self.inst_trigger()
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


if __name__ == '__main__':
    root = Tk()
    s = Scrollbar(root, orient=VERTICAL)
    t = TextConsole(root, yscrollcommand=s.set, font='Consolas 10')
    s.config(command=t.yview)
    s.pack(side=RIGHT, fill=Y)
    t.pack(side=TOP, fill=BOTH, expand=TRUE)
    t.focus()
    root.mainloop()
