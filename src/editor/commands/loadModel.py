from editor.commandManager import Command
from editor.globals import editor


class LoadModel(Command):
    def __init__(self, path):
        self.path = path
        self.model = None

    def do(self, *args, **kwargs):
        self.model = editor.level_editor.load_model(self.path)

    def undo(self):
        editor.level_editor.remove_nps([self.model])

    def clean(self, **kwargs):
        pass
