import editor.constants as constants
from editor.core.pModBase import PModBase


class RuntimeModule(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)

        self.__game = kwargs.pop("game", None)
        self.type = constants.RuntimeModule
        self.discarded_attrs = "_RuntimeModule__game"

    @property
    def game(self):
        return self.__game
