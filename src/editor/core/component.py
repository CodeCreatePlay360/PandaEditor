import editor.constants as constants
from panda3d.core import NodePath
from editor.core.runtimeModule import RuntimeModule


class Component(RuntimeModule, NodePath):
    def __init__(self, np, *args, **kwargs):
        NodePath.__init__(self, np)
        RuntimeModule.__init__(self, *args, **kwargs)
        self.type = constants.Component

    def __detach__(self):
        pass
