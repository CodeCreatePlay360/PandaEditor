from editor.commandManager import Command
from editor.globals import editor


class AddCamera(Command):
    def __init__(self, *args, **kwargs):
        self.camera_np = None

    def do(self, *args, **kwargs):
        self.camera_np = editor.p3d_app.level_editor.add_camera()

    def undo(self):
        editor.p3d_app.level_editor.remove_nps([self.camera_np])
        # editor.observer.trigger("OnRemoveNPs", [self.camera_np])

    def clean(self, **kwargs):
        pass
