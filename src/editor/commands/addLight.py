from editor.commandManager import Command
from editor.globals import editor


class AddLight(Command):
    def __init__(self, light_type, *args, **kwargs):
        self.light_type = light_type
        self.light_np = None

    def do(self, *args, **kwargs):
        self.light_np = editor.level_editor.add_light(self.light_type)
        # editor.observer.trigger("OnAddNPs", [self.light_np])

    def undo(self):
        # editor.observer.trigger("OnRemoveNPs", [self.light_np])
        editor.level_editor.remove_nps([self.light_np])

    def clean(self, **kwargs):
        pass
