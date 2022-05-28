from editor.commandManager import Command


class RemoveObjects(Command):
    def __init__(self, app, nps, *args, **kwargs):
        super(RemoveObjects, self).__init__(app)

        self.objects = []

    def __call__(self, *args, **kwargs):
        for np in self.app.level_editor.selection.selected_nps:
            self.objects.append(np)

        self.app.level_editor.remove_nps()

    def undo(self):
        self.app.level_editor.restore_nps(self.objects)
