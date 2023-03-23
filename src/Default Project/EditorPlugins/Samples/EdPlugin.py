import random
import panda3d.core as p3d_core
from editor.core import EditorPlugin
from editor.commandManager import Command
from editor.globals import editor


class OffsetCube(Command):
    def __init__(self, *args, **kwargs):
        Command.__init__(self, *args, **kwargs)
        self.np = None
        self.last_pos = p3d_core.LVecBase3f()

    def do(self):
        render = editor.game.active_scene.render  # get the active scene render
        np = render.find("**/cube.fbx")  # get the NodePath

        # make sure NodePath exists otherwise return False
        if np:
            self.np = np
        else:  # np is None, raise assertion
            assert np is None

        # record the last position
        self.last_pos = self.np.getPos()

        # randomly offset the node-path
        x = random.randrange(0, 300)
        y = random.randrange(0, 300)
        z = random.randrange(0, 300)
        self.np.setPos(p3d_core.LVecBase3f(x, y, z))

    def undo(self):
        self.np.setPos(self.last_pos)


class EdPlugin(EditorPlugin):
    def __init__(self, *args, **kwargs):
        EditorPlugin.__init__(self, *args, **kwargs)
        # __init__ should not contain anything except for variable declaration...!
        le = self.le  # instance of level editor

    def on_start(self):
        self.add_command("Math", OffsetCube, self.render.find("**/cube.fbx"))

    def on_update(self):
        pass
