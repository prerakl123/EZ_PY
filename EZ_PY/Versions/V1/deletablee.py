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










import importlib.util
import sys

def import_module(name, package=None):
    """An approximate implementation of import."""
    absolute_name = importlib.util.resolve_name(name, package)
    try:
        return sys.modules[absolute_name]
    except KeyError:
        pass

    path = None
    if '.' in absolute_name:
        parent_name, _, child_name = absolute_name.rpartition('.')
        parent_module = import_module(parent_name)
        path = parent_module.__spec__.submodule_search_locations
    for finder in sys.meta_path:
        spec = finder.find_spec(absolute_name, path)
        if spec is not None:
            break
    else:
        msg = f'No module named {absolute_name!r}'
        raise ModuleNotFoundError(msg, name=absolute_name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[absolute_name] = module
    spec.loader.exec_module(module)
    if path is not None:
        setattr(parent_module, child_name, module)
    return module

import_module('EZ_PY')
