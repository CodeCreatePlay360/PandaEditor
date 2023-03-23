import sys
import importlib


def import_module(path):
    if sys.platform == "win32" or sys.platform == "win64":
        file = path.split("\\")[-1]
    else:
        file = path.split("/")[-1]

    # print("LOADED \n FILE--> {0} \n PATH {1} \n".format(file, path))

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
        imported.append(import_module(path))

    return imported
