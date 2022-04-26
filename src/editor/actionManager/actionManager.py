from editor.constants import *


class ActionManager:
    def __init__(self, actns_count):
        self.undo_list = []
        self.redo_list = []
        self.max_actions_count = actns_count

    def undo(self):
        pass

    def redo(self):
        pass
