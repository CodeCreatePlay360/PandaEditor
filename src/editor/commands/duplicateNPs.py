from editor.commandManager import EdCommand
from editor.globals import editor


class DuplicateNPs(EdCommand):
    def __init__(self, app, *args, **kwargs):
        super(DuplicateNPs, self).__init__(app)

        self.duplicated_nps = []

    def do(self, *args, **kwargs):
        new_nps = self.app.level_editor.duplicate_nps()
        for np in new_nps:
            self.duplicated_nps.append(np)
        editor.observer.trigger("OnAddNPs", self.duplicated_nps)

    def undo(self):
        editor.observer.trigger("OnRemoveNPs", self.duplicated_nps)
        self.app.level_editor.remove_nps(self.duplicated_nps, permanent=True)
