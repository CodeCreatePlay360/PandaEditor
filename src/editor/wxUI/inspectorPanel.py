from editor.wxUI.baseInspectorPanel import BaseInspectorPanel
from editor.constants import *


class InspectorPanel(BaseInspectorPanel):
    def __init__(self, *args, **kwargs):
        BaseInspectorPanel.__init__(self, *args, **kwargs)
        object_manager.add_object("PropertiesPanel", self)
