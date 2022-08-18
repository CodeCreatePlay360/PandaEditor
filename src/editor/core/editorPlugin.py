import editor.constants as constants
from editor.core.pModBase import PModBase


class EditorPlugin(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)

        self._le = kwargs.pop("level_editor", None)
        self.module_type = constants.EditorPlugin
        self.discarded_attrs = "_le"
