import os
from panda3d.core import Vec3


def get_dir_items(_dir, file_types=()):
    def get_items(dir_path=None):
        dir_files = os.listdir(dir_path)

        for file in dir_files:
            file_path = dir_path + "/" + file

            if os.path.isdir(file_path):
                get_items(file_path)
            elif os.path.isfile(file_path) and file_path.split(".")[-1] in file_types:
                items.append((file_path, file))

    items = []
    get_items(_dir)
    return items


def euler_from_hpr(hpr):
    euler = Vec3(hpr.y, hpr.z, hpr.x)
    return euler


def hpr_from_euler(euler):
    hpr = Vec3(euler.z, euler.x, euler.y)
    return hpr


# convert from one range to another
def convert_to_range(old_min, old_max, new_min, new_max, value):
    oldRange = old_max - old_min
    if oldRange == 0:
        newValue = new_min
        return newValue
    else:
        newRange = new_max - new_min
        newValue = (((value - old_min) * newRange) / oldRange) + new_min
        return newValue


# clamp angle to pi, -pi range
def clamp_angle(angle, min_val, max_val):
    if angle < -360:
        angle += 360
    if angle > 360:
        angle -= 360
    clamp = max(min(angle, max_val), min_val)
    return clamp


def clamp_value(val, min, max):
    n = (val - min) / (max - min)
    return n
