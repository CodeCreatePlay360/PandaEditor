import sys
import importlib
from importlib import util
from pathlib import Path


def import_module(path):
    file = Path(path)
    mod_name = file.stem  # Using .stem to get the file name without extension
    cls_name_ = mod_name[0].upper() + mod_name[1:]

    # load the module
    spec = importlib.util.spec_from_file_location(mod_name, str(file))
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
