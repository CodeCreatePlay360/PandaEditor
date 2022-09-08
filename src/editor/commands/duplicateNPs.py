from editor.commandManager import Command
from editor.constants import obs


class DuplicateNPs(Command):
    def __init__(self, app, *args, **kwargs):
        super(DuplicateNPs, self).__init__(app)

        self.duplicated_nps = []

    def do(self, *args, **kwargs):
        new_nps = self.app.level_editor.duplicate_nps()
        for np in new_nps:
            self.duplicated_nps.append(np)
        obs.trigger("OnAddNPs", self.duplicated_nps)

    def undo(self):
        obs.trigger("OnRemoveNPs", self.duplicated_nps)
        self.app.level_editor.remove_nps(self.duplicated_nps, permanent=True)
