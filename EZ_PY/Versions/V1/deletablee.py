##for i in range(100):
##    print('YOLO')
##    
##    if i % 2 == 0:
##        print('lolo')
##        if i % 4 == 0:
##            print('lolololololololololololol')
##            if i % 8 == 0:
##                print('alkfmjolafjopiwfjipnfjpi')
##                if i % 16 == 0:
##                    print('aoiwfh oi hpiwfpi hpi hiaf hpiaf ha')
##                    if i % 32 == 0:
##                        print('aloo pakoda')



# from ColorText import ColorText
# import inspect
# from randfuncs import comp_gen_passwd
# import importlib

# print(inspect.signature(ColorText.find_indent))
# print(inspect.signature(ColorText.search_output).__str__().strip('(').rstrip(')').strip().split(','))
# print(inspect.importlib.import_module('EZ_PY'))


# import importlib.util
# import sys
# 
# # For illustrative purposes.
# name = 'ColorText'
# 
# if name in sys.modules:
#     print(f"{name!r} already in sys.modules")
# elif importlib.util.find_spec(name) is not None:
#     # If you chose to perform the actual import ...
#     spec = importlib.util.find_spec(name)
#     module = importlib.util.module_from_spec(spec)
#     sys.modules[name] = module
#     spec.loader.exec_module(module)
#     print(f"{name!r} has been imported")
# else:
#     print(f"can't find the {name!r} module")










##import importlib.util
##import sys
##
##def import_module(name, package=None):
##    """An approximate implementation of import."""
##    absolute_name = importlib.util.resolve_name(name, package)
##    try:
##        return sys.modules[absolute_name]
##    except KeyError:
##        pass
##
##    path = None
##    if '.' in absolute_name:
##        parent_name, _, child_name = absolute_name.rpartition('.')
##        parent_module = import_module(parent_name)
##        path = parent_module.__spec__.submodule_search_locations
##    for finder in sys.meta_path:
##        spec = finder.find_spec(absolute_name, path)
##        if spec is not None:
##            break
##    else:
##        msg = f'No module named {absolute_name!r}'
##        raise ModuleNotFoundError(msg, name=absolute_name)
##    module = importlib.util.module_from_spec(spec)
##    sys.modules[absolute_name] = module
##    spec.loader.exec_module(module)
##    if path is not None:
##        setattr(parent_module, child_name, module)
##    return module
##
##import_module('EZ_PY')



















import tkinter as tk

# Some random text to display in the Text widget
lorem_ipsum = '''Lorem ipsum dolor sit amet, consectetur adipiscing
elit. Aenean lacinia tortor quis quam vehicula semper. Curabitur
faucibus, purus a egestas bibendum, velit metus hendrerit nulla, non
lobortis dolor mi in dolor. Aliquam ultrices felis sit amet dolor
gravida, id ullamcorper odio rutrum. Fusce consectetur tempor nibh, non
dictum dolor dictum nec. In hac habitasse platea dictumst. Morbi laoreet
consequat metus, at lacinia nisl suscipit id. Quisque vitae sodales
velit, a lobortis nisl. Praesent varius convallis efficitur. Vivamus
fringilla at risus nec viverra. Proin suscipit, lorem sed laoreet
ultricies, velit massa ornare nunc, vel egestas nibh ex vitae leo.'''

lorem_ipsum = lorem_ipsum.replace('\n', ' ')


class TextLocationDemo(object):
    """ Text widget cursor location demo """
    def __init__(self):
        root = tk.Tk()
        root.title("Text Location Demo")

        tk.Button(root, text="Show cursor location", command=self.location_cb).pack()

        # Create a Text widget, with word wrapping
        self.textwidget = tw = tk.Text(root, wrap=tk.WORD)
        tw.pack()
        tw.insert(tk.END, lorem_ipsum)

        root.mainloop()

    def alert(self, geometry, msg):
        """ Display `msg` in an Alert with given geometry,
            which is a tuple of (width, height, ox, oy)
        """
        top = tk.Toplevel()
        # widget geometry parameter must be given in X windows format
        top.geometry("%dx%d%+d%+d" % geometry)

        msg = tk.Message(top, text=msg, width=geometry[0])
        msg.pack()

        button = tk.Button(top, text="Ok", command=top.destroy)
        button.pack()

    def location_cb(self):
        ''' Determine the location of the insertion cursor
            and display it in a window just under that location
        '''
        w = self.textwidget

        # Get the Text widget's current location
        pos_x, pos_y = w.winfo_rootx(), w.winfo_rooty()

        # Get the bounding box of the insertion cursor
        cursor = tk.INSERT
        bbox = w.bbox(cursor)
        if bbox is None:
            print('Cursor is not currently visible. Scrolling...')
            w.see(cursor)
            bbox = w.bbox(cursor)

        bb_x, bb_y, bb_w, bb_h = bbox

        # Open a window just beneath the insertion cursor
        width = 200
        height = 80
        ox = pos_x + bb_x
        oy = pos_y + bb_y + bb_h
        s = 'Cursor: (%d, %d)' % (ox, oy)
        print(s)

        geometry = (width, height, ox, oy)
        self.alert(geometry, s)


TextLocationDemo()
