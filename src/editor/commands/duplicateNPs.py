from editor.commandManager import Command
from editor.globals import editor


class DuplicateNPs(Command):
    def __init__(self, *args, **kwargs):
        self.duplicated_nps = []

    def do(self, *args, **kwargs):
        new_nps = editor.level_editor.duplicate_nps()
        for np in new_nps:
            self.duplicated_nps.append(np)
        return True

    def undo(self):
        editor.level_editor.remove_nps(self.duplicated_nps, permanent=True)
