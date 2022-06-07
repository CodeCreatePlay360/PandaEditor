from editor.commandManager import Command


class RemoveObjects(Command):

    # TODO explanation
    RemoveNPsCmd = None

    def __init__(self, app, nps, *args, **kwargs):
        super(RemoveObjects, self).__init__(app)
        self.clean_up = ""
        self.nps = []

    def do(self, *args, **kwargs):
        for np in self.app.level_editor.selection.selected_nps:
            self.nps.append(np)

        self.app.level_editor.remove_nps()

    def undo(self):
        self.app.level_editor.restore_nps(self.nps)
