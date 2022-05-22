
class ActionManager:
    def __init__(self, actions_count=30):
        self.undo_list = []
        self.redo_list = []
        self.max_actions_count = actions_count

    def undo(self):
        pass

    def redo(self):
        pass
