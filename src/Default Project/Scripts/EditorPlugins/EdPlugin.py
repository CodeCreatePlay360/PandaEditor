import panda3d.core as p3d_core
from editor.core import EditorPlugin
from editor.commandManager import Command


class MyCommand(Command):
    def __init__(self, *args, **kwargs):
        Command.__init__(self, *args, **kwargs)

    def do(self, s):
        print("command do")

    def undo(self):
        print("command undo")


class EdPlugin(EditorPlugin):
    def __init__(self, *args, **kwargs):
        EditorPlugin.__init__(self, *args, **kwargs)

        # __init__ should not contain anything except for variable declaration...!

        le = self.le  # instance of level editor

        command = MyCommand()
        self.add_command("Math", command)

    def on_start(self):
        """on_start method is called once when editor is loaded,
        new node-paths such as direct gui elements, should be created here."""
        pass

    def on_update(self):
        """update method is called every frame"""
        pass
