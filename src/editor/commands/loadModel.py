from editor.commandManager import Command
from editor.globals import editor


class LoadModel(Command):
    def __init__(self, path, *args, **kwargs):
        self.path = path[len(editor.level_editor.project.project_path) + 1:]
        self.model = None

    def do(self, *args, **kwargs):
        self.model = editor.level_editor.load_model(self.path)
        # editor.observer.trigger("OnAddNPs", [self.model])

    def undo(self):
        editor.level_editor.remove_nps([self.model])
        # editor.observer.trigger("OnRemoveNPs", [self.model])

    def clean(self, **kwargs):
        pass
