from editor.commandManager import EdCommand
from editor.globals import editor


class RemoveObjects(EdCommand):

    # TODO explanation
    RemoveNPsCmd = None

    def __init__(self, app, nps, *args, **kwargs):
        super(RemoveObjects, self).__init__(app)
        self.clean_up = ""
        self.saved = []

    def do(self, *args, **kwargs):
        selected = [np for np in self.app.level_editor.selection.selected_nps]
        for np in selected:
            self.saved.append((np, np.get_parent()))

        editor.observer.trigger("OnRemoveNPs", selected)
        self.app.level_editor.remove_nps(selected)
        editor.inspector.layout_auto()

    def undo(self):
        nps = self.app.level_editor.restore_nps(self.saved)
        self.app.level_editor.set_selected(nps)
        editor.observer.trigger("OnAddNPs", nps)

