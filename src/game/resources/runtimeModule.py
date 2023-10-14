import game.constants as constants
from game.resources.pModBase import PModBase


class RuntimeModule(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)

        self.__game = kwargs.pop("game", None)
        self.module_type = constants.RuntimeModule
        self.non_serialized_attrs = "_RuntimeModule__game"

    @property
    def game(self):
        return self.__game
