from editor.commandManager import Command
from editor.constants import object_manager


class SelectObjects(Command):
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

        wx_main = object_manager.get("WxMain")
        wx_main.freeze()

        object_manager.get("InspectorPanel").set_object(np, np.get_name(), np.get_properties())
        object_manager.get("ResourceTilesPanel").deselect_all()

        if self.from_le:
            object_manager.get("SceneGraph").select(self.selected_nps)

        wx_main.thaw()

    def undo(self):
        wx_main = object_manager.get("WxMain").freeze()
        wx_main.freeze()

        if len(self.last_selections) > 0:
            self.app.level_editor.set_selected(self.last_selections)
            object_manager.get("SceneGraph").select(self.last_selections)

            obj = self.last_selections[0]
            object_manager.get("InspectorPanel").set_object(obj, obj.get_name(), obj.get_properties())
        else:
            self.app.level_editor.set_selected(self.selected_nps)
            object_manager.get("SceneGraph").select(self.selected_nps)

            obj = self.selected_nps[0]
            object_manager.get("InspectorPanel").set_object(obj, obj.get_name(), obj.get_properties())

        wx_main.thaw()
