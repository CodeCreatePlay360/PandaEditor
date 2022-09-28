from editor.commandManager import EdCommand
from editor.globals import editor


class TransformNPs(EdCommand):
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
        editor.scene_graph.select(nps)
        editor.inspector.set_object(nps[0], nps[0].get_name(), nps[0].get_properties())
