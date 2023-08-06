import math
import panda3d.core as p3d_core
from editor.core import EditorPlugin


class SamplePlugin(EditorPlugin):
    def __init__(self, *args, **kwargs):
        # __init__ should not contain anything except for field declaration
        EditorPlugin.__init__(self, *args, **kwargs)

    def on_start(self):
        # this method is called only once
        pass

    def on_update(self):
        # this method is called every frame
        pass
