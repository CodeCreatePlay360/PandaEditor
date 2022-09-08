from editor.commandManager import Command
from editor.constants import object_manager


class ReparentNPs(Command):
    def __init__(self, app, src_nps, target_np, *args, **kwargs):
        super(ReparentNPs, self).__init__(app)

        self.src_nps = src_nps

        self.original_src_np_parents = []
        for np in self.src_nps:
            self.original_src_np_parents.append(np.get_parent())

        self.target_np = target_np

    def do(self, *args, **kwargs):

        inspector = object_manager.get("InspectorPanel")
        scene_graph = object_manager.get("SceneGraph")
        le = object_manager.get("LevelEditor")
        object_manager.get("ResourceTilesPanel").deselect_all()

        le.reparent_np(self.src_nps, self.target_np)
        le.set_selected(self.src_nps)
        #
        scene_graph.reparent(self.src_nps, self.target_np)
        scene_graph.select(self.src_nps)

        np = self.src_nps[0]
        inspector.set_object(np, np.get_name(), np.get_properties())

    def undo(self):
        self.app.level_editor.reparent_np(self.src_nps, self.original_src_np_parents)

        scene_graph = object_manager.get("SceneGraph")
        scene_graph.rebuild()
        scene_graph.select(self.src_nps)
