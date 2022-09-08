import editor.constants as constants
from editor.wxUI.panels.baseInspectorPanel import BaseInspectorPanel


class InspectorPanel(BaseInspectorPanel):
    def __init__(self, *args, **kwargs):
        BaseInspectorPanel.__init__(self, *args, **kwargs)
        constants.object_manager.add_object("InspectorPanel", self)
