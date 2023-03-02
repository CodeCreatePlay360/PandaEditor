from editor.commandManager import Command
from editor.globals import editor


class RemoveObjects(Command):
    def __init__(self, nps: list, *args, **kwargs):
        self.clean_up = ""
        self.selected_nps = nps
        self.saved = []

    def do(self, *args, **kwargs):
        selected = [np for np in self.selected_nps]
        for np in selected:
            self.saved.append((np, np.get_parent()))

        # editor.observer.trigger("OnRemoveNPs", selected)
        editor.p3d_app.level_editor.remove_nps(selected)
        editor.inspector.layout_auto()
        self.selected_nps.clear()
        return True

    def undo(self):
        nps = editor.level_editor.restore_nps(self.saved)
        editor.p3d_app.level_editor.set_selected(nps)
        # editor.observer.trigger("OnAddNPs", nps)

    def clean(self, **kwargs):
        nps = []
        for np, parent in self.saved:
            nps.append(np)
        editor.level_editor.remove_nps(nps, permanent=True)

