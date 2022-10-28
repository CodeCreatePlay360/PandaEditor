import math
import panda3d.core as p3d_core
from editor.core.component import Component


class Camera(Component):
    def __init__(self, *args, **kwargs):
        Component.__init__(self, *args, **kwargs)
        # __init__ should not contain anything except for variable declaration...!
        self.pos = 3
        self.nicole = "Ass"

    def on_start(self):
        # this method is called only once
        self.pos += self.pos
        self.set_pos(self.pos)

    def on_update(self):
        # this method is called every frame
        pass

