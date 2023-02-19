from editor.commandManager import Command
from editor.globals import editor


class AddActor(Command):
    def __init__(self, path):
        self.path = path
        self.model = None

    def do(self, *args, **kwargs):
        self.model = editor.level_editor.add_actor(self.path)

    def undo(self):
        editor.level_editor.remove_nps([self.model])
