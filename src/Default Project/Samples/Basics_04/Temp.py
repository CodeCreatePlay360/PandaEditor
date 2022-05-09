import math
import panda3d.core as p3dCore
from editor.core.pModBase import PModBase


class Temp(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)
        # __init__ should not contain anything except for variable declaration...!

    def on_start(self):
        # this method is called only once
        pass

    def on_update(self):
        # this method is called evert frame
        pass

