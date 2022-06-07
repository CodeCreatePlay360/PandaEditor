from editor.commandManager import Command


class AddLight(Command):
    def __init__(self, app, light_type, *args, **kwargs):
        super(AddLight, self).__init__(app)

        self.light_type = light_type
        self.light_np = None

    def do(self, *args, **kwargs):
        self.light_np = self.app.level_editor.add_light(self.light_type)

    def undo(self):
        self.app.level_editor.remove_nps([self.light_np])
