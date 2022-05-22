from editor.core.pModBase import PModBase


class RuntimeModule(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)

        self._game = kwargs.pop("game", None)

        self._discarded_attrs.append("_game")
