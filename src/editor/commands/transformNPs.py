from editor.commandManager import Command


class TransformNPs(Command):
    def __init__(self, app, old_nps_data, *args, **kwargs):
        super(TransformNPs, self).__init__(app)

        self.old_nps_data = {}
        for np in old_nps_data.keys():
            self.old_nps_data[np] = old_nps_data[np]

    def do(self, *args, **kwargs):
        pass

    def undo(self):
        for np in self.old_nps_data.keys():
            np.set_transform(self.old_nps_data[np])
        self.app.level_editor.update_gizmo()
