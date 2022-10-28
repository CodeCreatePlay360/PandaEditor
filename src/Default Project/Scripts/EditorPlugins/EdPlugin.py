import panda3d.core as p3d_core
from editor.core import EditorPlugin
from editor.commandManager import Command


class MyCommand(Command):
    def __init__(self, np, *args, **kwargs):
        Command.__init__(self, *args, **kwargs)
        self.np = None

    def do(self):
        pass

    def undo(self):
        print("command undo")

    def clean(self):
        pass


class EdPlugin(EditorPlugin):
    def __init__(self, *args, **kwargs):
        EditorPlugin.__init__(self, *args, **kwargs)

        # __init__ should not contain anything except for variable declaration...!

        le = self.le  # instance of level editor

    def on_start(self):
        """on_start method is called once when editor is loaded,
        new node-paths such as direct gui elements, should be created here."""
        command = MyCommand(self.render.find("**/Cube.fbx"))
        self.add_command("Math", command)
        pass

    def on_update(self):
        """update method is called every frame"""
