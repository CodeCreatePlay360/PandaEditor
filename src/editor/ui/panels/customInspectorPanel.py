from editor.wxUI.baseInspectorPanel import BaseInspectorPanel
from editor.constants import *


class CustomInspectorPanel(BaseInspectorPanel):
    def __init__(self, *args, **kwargs):
        BaseInspectorPanel.__init__(self, *args, **kwargs)
        