from editor.commandManager import Command
from editor.globals import editor


class AddCamera(Command):
    def __init__(self, *args, **kwargs):
        self.camera_np = None

    def do(self, *args, **kwargs):
        self.camera_np = editor.p3D_app.level_editor.add_camera()
        return True

    def undo(self):
        editor.p3D_app.level_editor.remove_nps([self.camera_np])
