import editor.constants as constants
from editor.wxUI.baseInspectorPanel import BaseInspectorPanel


class InspectorPanel(BaseInspectorPanel):
    def __init__(self, *args, **kwargs):
        BaseInspectorPanel.__init__(self, *args, **kwargs)
        constants.object_manager.add_object("InspectorPanel", self)
