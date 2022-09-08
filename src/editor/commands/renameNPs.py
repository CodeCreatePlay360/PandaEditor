import editor.constants as constants
from editor.commandManager import Command


class RenameNPs(Command):
    def __init__(self, app, np, old_name, new_name, *args, **kwargs):
        super(RenameNPs, self).__init__(app)

        self.np = np
        self.old_name = old_name
        self.new_name = new_name

    def do(self, *args, **kwargs):
        self.np.set_name(self.new_name)

        inspector = constants.object_manager.get("InspectorPanel")
        inspector.set_object(self.np, self.np.get_name(), self.np.get_properties())

    def undo(self):
        self.np.set_name(self.old_name)
        scene_graph = constants.object_manager.get("SceneGraph")
        inspector = constants.object_manager.get("InspectorPanel")

        scene_graph.rename_item(self.np, self.np.get_name())
        inspector.layout_object_properties(self.np, self.np.get_name(), self.np.get_properties())

