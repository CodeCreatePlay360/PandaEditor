"""implements various directory operations rename, duplicate, delete etc."""

import sys
import os


def delete(path):
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
