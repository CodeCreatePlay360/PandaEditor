from editor.commandManager import Command
from editor.globals import editor
from game.constants import TAG_GAME_OBJECT


class TransformNPs(Command):
    def __init__(self, old_nps_data):

        self.old_nps_data = {}
        for np in old_nps_data.keys():
            self.old_nps_data[np] = old_nps_data[np]

    def do(self):
        return True

    def undo(self):
        nps = []
        for np in self.old_nps_data.keys():
            nps.append(np)
            np.set_transform(self.old_nps_data[np])

        editor.level_editor.set_selected(nps)
        editor.scene_graph.select(nps)
        editor.inspector.layout(nps[0], nps[0].get_name(), nps[0].getPythonTag(TAG_GAME_OBJECT).get_properties())
