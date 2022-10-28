from editor.commandManager import Command
from editor.globals import editor


class ObjectAdd(Command):
    def __init__(self, obj_path, *args, **kwargs):
        """Adds any of the default editor prototype objects, Menubar > Object > GameObject > (Any)"""

        self.path = obj_path
        self.object = None

    def do(self, *args, **kwargs):
        self.object = editor.level_editor.add_object(self.path)
        # editor.observer.trigger("OnAddNPs", [self.object])

    def undo(self):
        editor.level_editor.remove_nps([self.object])
        # editor.observer.trigger("OnRemoveNPs", [self.object])

    def clean(self, **kwargs):
        pass
