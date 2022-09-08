from editor.commandManager import Command
from editor.constants import object_manager, obs


class RemoveObjects(Command):

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

        obs.trigger("OnRemoveNPs", selected)
        self.app.level_editor.remove_nps(selected)
        object_manager.get("InspectorPanel").layout_auto()

    def undo(self):
        nps = self.app.level_editor.restore_nps(self.saved)
        self.app.level_editor.set_selected(nps)
        obs.trigger("OnAddNPs", nps)

