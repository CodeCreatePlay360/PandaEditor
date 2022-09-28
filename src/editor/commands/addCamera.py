from editor.commandManager import EdCommand
from editor.globals import editor


class AddCamera(EdCommand):
    def __init__(self, app, *args, **kwargs):
        super(AddCamera, self).__init__(app)

        self.camera_np = None

    def do(self, *args, **kwargs):
        self.camera_np = self.app.level_editor.add_camera()
        editor.observer.trigger("OnAddNPs", [self.camera_np])

    def undo(self):
        self.app.level_editor.remove_nps([self.camera_np])
        editor.observer.trigger("OnRemoveNPs", [self.camera_np])
