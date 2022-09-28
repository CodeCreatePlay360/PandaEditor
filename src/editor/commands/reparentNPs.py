from editor.commandManager import EdCommand
from editor.globals import editor


class ReparentNPs(EdCommand):
    def __init__(self, app, src_nps, target_np, *args, **kwargs):
        super(ReparentNPs, self).__init__(app)

        self.src_nps = src_nps

        self.original_src_np_parents = []
        for np in self.src_nps:
            self.original_src_np_parents.append(np.get_parent())

        self.target_np = target_np

    def do(self, *args, **kwargs):

        editor.resource_browser.deselect_all_files()

        editor.level_editor.reparent_np(self.src_nps, self.target_np)
        editor.level_editor.set_selected(self.src_nps)
        #
        editor.scene_graph.reparent(self.src_nps, self.target_np)
        editor.scene_graph.select(self.src_nps)

        np = self.src_nps[0]
        editor.inspector.set_object(np, np.get_name(), np.get_properties())

    def undo(self):
        self.app.level_editor.reparent_np(self.src_nps, self.original_src_np_parents)

        editor.scene_graph.rebuild()
        editor.scene_graph.select(self.src_nps)
        self.app.level_editor.set_selected(self.src_nps)
