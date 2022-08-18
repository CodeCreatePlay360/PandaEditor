import editor.constants as constants
from editor.core.pModBase import PModBase


class RuntimeModule(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)
        self._game = kwargs.pop("game", None)
        self.module_type = constants.RuntimeModule
        self.discarded_attrs = "_game"
