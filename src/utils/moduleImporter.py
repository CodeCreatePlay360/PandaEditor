import sys
import importlib
from pathlib import Path


def import_module(path):
    file = Path(path)
    mod_name = file.split(".")[0]
    cls_name_ = mod_name[0].upper() + mod_name[1:]

    # load the module
    spec = importlib.util.spec_from_file_location(mod_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    data = (path, module, cls_name_)
    return data


def import_modules(modules_paths):
    imported = []

    for path in modules_paths:
        try:
            module = import_module(path)
            imported.append(module)
        except Exception as exception:
            print(exception)

    return imported
