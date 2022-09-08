from editor.commandManager import Command
from editor.constants import obs


class AddCamera(Command):
    def __init__(self, app, *args, **kwargs):
        super(AddCamera, self).__init__(app)

        self.camera_np = None

    def do(self, *args, **kwargs):
        self.camera_np = self.app.level_editor.add_camera()
        obs.trigger("OnAddNPs", [self.camera_np])

    def undo(self):
        self.app.level_editor.remove_nps([self.camera_np])
        obs.trigger("OnRemoveNPs", [self.camera_np])
