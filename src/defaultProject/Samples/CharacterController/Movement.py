import math
import panda3d.core as p3d_core
from game.resources import Component


class Movement(Component):
    def __init__(self, *args, **kwargs):
        Component.__init__(self, *args, **kwargs)

        # __init__ should not contain anything except for variable declaration

    def on_start(self):
        # this method is called only once
        pass

    def on_update(self):
        # this method is called every frame
        pass

