from editor.commandManager import Command


class DuplicateNPs(Command):
    def __init__(self, app, *args, **kwargs):
        super(DuplicateNPs, self).__init__(app)

        self.duplicated_nps = []

    def __call__(self, *args, **kwargs):
        new_nps = self.app.level_editor.duplicate_nps()
        for np in new_nps:
            self.duplicated_nps.append(np)

    def undo(self):
        self.app.level_editor.remove_nps(self.duplicated_nps, permanent=True)
