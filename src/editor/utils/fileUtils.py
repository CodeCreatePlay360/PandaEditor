"""implements various directory operations rename, duplicate, delete etc."""

import os


def rename(current_path, new_label, ext=None):
    """current path as on disk, new_label, ext: file extension"""
    old_path = current_path
    old_name = old_path.split("/")[-1]

    new_path = old_path[:len(old_path) - len(old_name) - 1]
    new_path = new_path + "/" + new_label
    if ext:
        new_path += "." + ext

    if not os.path.exists(new_path):
        os.rename(old_path, new_path)
        return True

    return False


def duplicate():
    pass


def delete(path):
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
