from tkinter import *
import tkinter.ttk as ttk
import json
from ColorText import ColorText


class ThemeWin(Toplevel):
    def __init__(self, master, **kwargs):
        Toplevel.__init__(self, master)
        self.geometry('510x303+400+200')
        self.resizable(False, False)
        self.wm_attributes('-topmost', True)
        
        with open('config.json') as file:
            self.config_dict = json.load(file)

        self.ctt_frame = LabelFrame(self, text='Sample', font='Consolas 13 bold')

        self.d_text = '#import modules\nimport math\n\ndef fac(n):\n\t"""prints factorial of n"""\n\tif n <= 1:\n\t\tr'\
                      'eturn 1\n\telse:\n\t\treturn n*fac(n-1)\n\nfacs = []\nfor i in range(10):\n\tlist.__add__(f'\
                      'acs, fac(i))\nprint(s)'

        self.display_text = ColorText(master=self.ctt_frame, width=38, height=14)
        self.display_text.bind('<Any-Key>', self.t_cmd)
        self.display_text.insert(1.0, self.d_text)
        self.display_text.inst_trigger()

        self.list_frame = LabelFrame(self, text='Themes', font='Consolas 12 bold')
        self.theme_list = Listbox(self.list_frame, selectmode=BROWSE, height=10)
        for i, j in enumerate(self.config_dict['themes'].keys()):
            self.theme_list.insert(i, j)
        self.theme_list.bind('<<ListboxSelect>>', self.display_theme)
        self.theme_list.bind('<Double-1>', self.display_text.up_date)

        self.theme_list.pack(side=LEFT, anchor=N, fill=Y, padx=5, pady=2)
        self.list_frame.pack(side=LEFT, expand=TRUE, fill=Y, padx=5, pady=2)
        self.ctt_frame.pack(side=LEFT, anchor=N, padx=5, pady=2)
        self.display_text.pack(side=TOP, padx=5, pady=2)

    def t_cmd(self, event):
        if event.keysym not in ('Control_R', 'Control_L', 'Shift_R', 'Shift_L'):
            return 'break'

    def display_theme(self, event):
        h = self.theme_list.get(self.theme_list.curselection()[0])
        self.config_dict['selected_theme'] = h
        json_object = json.dumps(self.config_dict, indent=4)
        with open('config.json', 'w') as f:
            f.write(json_object)
        self.display_text.up_date()
        self.display_text.inst_trigger()

if __name__ == '__main__':
    root = Tk()
    s = ThemeWin(root)
    root.mainloop()