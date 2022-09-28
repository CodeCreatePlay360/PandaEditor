from editor.commandManager import EdCommand
from editor.globals import editor


class AddLight(EdCommand):
    def __init__(self, app, light_type, *args, **kwargs):
        super(AddLight, self).__init__(app)

        self.light_type = light_type
        self.light_np = None

    def do(self, *args, **kwargs):
        self.light_np = self.app.level_editor.add_light(self.light_type)
        editor.observer.trigger("OnAddNPs", [self.light_np])

    def undo(self):
        self.app.level_editor.remove_nps([self.light_np])
        editor.observer.trigger("OnRemoveNPs", [self.light_np])
