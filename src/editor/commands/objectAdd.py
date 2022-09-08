from editor.commandManager import Command
from editor.constants import obs


class ObjectAdd(Command):
    def __init__(self, app, obj_path, *args, **kwargs):
        """Adds any of the default editor prototype objects, Menubar > Object > GameObject > (Any)"""

        super(ObjectAdd, self).__init__(app)

        self.path = obj_path
        self.object = None

    def do(self, *args, **kwargs):
        self.object = self.app.level_editor.add_object(self.path)
        obs.trigger("OnAddNPs", [self.object])

    def undo(self):
        self.app.level_editor.remove_nps([self.object])
        obs.trigger("OnRemoveNPs", [self.object])
