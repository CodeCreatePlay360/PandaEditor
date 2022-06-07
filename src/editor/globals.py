LIGHT_UIDs = ["PointLight", "SpotLight", "DirectionalLight", "AmbientLight"]
CAMERA_UID = ["CameraNP"]
MODEL_NP = ["ModelNP"]

p3d_app = None


class Globals:
    def __init__(self):
        pass

    @property
    def selected_resource_item(self):
        resource_browser = p3d_app.wx_main.resource_browser.resource_browser
        selection = resource_browser.GetSelection()
        if selection:
            return resource_browser.GetItemData(selection)
        return None

    @property
    def selected_nps(self):
        selection = p3d_app.level_editor.selection
        return selection.selected_nps
