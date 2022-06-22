LIGHT_UIDs = ["PointLight", "SpotLight", "DirectionalLight", "AmbientLight"]
CAMERA_UID = ["CameraNP"]
MODEL_NP = ["ModelNP"]

p3d_app = None


class Globals:
    def __init__(self):
        pass

    @property
    def selected_resource_item(self):
        tiles_panel = p3d_app.wx_main.resource_browser.tiles_panel
        selection = tiles_panel.SELECTED_TILE
        if selection:
            return selection.data
        return None

    @property
    def selected_nps(self):
        selection = p3d_app.level_editor.selection
        return selection.selected_nps
