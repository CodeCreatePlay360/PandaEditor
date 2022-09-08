from editor.commandManager import Command
from editor.constants import object_manager


class TransformNPs(Command):
    def __init__(self, app, old_nps_data, *args, **kwargs):
        super(TransformNPs, self).__init__(app)

        self.old_nps_data = {}
        for np in old_nps_data.keys():
            self.old_nps_data[np] = old_nps_data[np]

    def do(self, *args, **kwargs):
        pass

    def undo(self):
        nps = []
        for np in self.old_nps_data.keys():
            nps.append(np)
            np.set_transform(self.old_nps_data[np])

        self.app.level_editor.set_selected(nps)
        self.app.level_editor.update_gizmo()
        object_manager.get("SceneGraph").select(nps)
        object_manager.get("InspectorPanel").set_object(nps[0], nps[0].get_name(), nps[0].get_properties())
