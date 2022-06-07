from editor.commandManager import Command


class SelectObjects(Command):
    def __init__(self, app, nps: list, last_selections=[], *args, **kwargs):
        super(SelectObjects, self).__init__(app)

        self.selected_nps = nps
        self.last_selections = last_selections

    def do(self, *args, **kwargs):
        self.app.level_editor.set_selected(self.selected_nps)

    def undo(self):
        if len(self.last_selections) > 0:
            self.app.level_editor.set_selected(self.last_selections)
        else:
            self.app.level_editor.deselect_all()
