import math
import panda3d.core as p3dCore
from editor.core import RuntimeModule


class TestModule(RuntimeModule):
    def __init__(self, *args, **kwargs):
        RuntimeModule.__init__(self, *args, **kwargs)

        # __init__ should contain anything except for variable declaration...!

    # on_start method is called once
    def on_start(self):
        pass

    # update method is called every frame
    def on_update(self):
        pass

    def foo(self):
        print("Test module...!")
