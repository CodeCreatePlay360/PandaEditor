from editor.commandManager import EdCommand
from editor.globals import editor


class SelectObjects(EdCommand):
    def __init__(self, app, nps: list, last_selections=None, from_le=True, *args, **kwargs):
        super(SelectObjects, self).__init__(app)

        if last_selections is None:
            last_selections = []
        self.selected_nps = nps
        self.last_selections = last_selections
        self.from_le = from_le

    def do(self, *args, **kwargs):
        self.app.level_editor.set_selected(self.selected_nps)
        np = self.selected_nps[0]

        editor.wx_main.freeze()

        editor.inspector.set_object(np, np.get_name(), np.get_properties())
        editor.resource_browser.deselect_all_files()

        if self.from_le:
            editor.scene_graph.select(self.selected_nps)

        editor.wx_main.thaw()

    def undo(self):
        editor.wx_main.freeze()

        if len(self.last_selections) > 0:
            self.app.level_editor.set_selected(self.last_selections)
            editor.scene_graph.select(self.last_selections)

            obj = self.last_selections[0]
            editor.inspector.set_object(obj, obj.get_name(), obj.get_properties())
        else:
            self.app.level_editor.set_selected(self.selected_nps)
            editor.scene_graph.select(self.selected_nps)

            obj = self.selected_nps[0]
            editor.inspector.set_object(obj, obj.get_name(), obj.get_properties())

        editor.wx_main.thaw()
