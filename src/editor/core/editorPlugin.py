from editor.core.pModBase import PModBase


class EditorPlugin(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)

        self._le = kwargs.pop("level_editor", None)
        self._wx_panel = None
        self.__unique_panel = None

        self._discarded_attrs.append("_wx_panel")
        self._discarded_attrs.append("_le")
        self._discarded_attrs.append("_EditorPlugin__unique_panel")

    def request_unique_panel(self, unique_panel_name: str):
        if type(unique_panel_name) is str:
            self.__unique_panel = unique_panel_name

    def get_unique_panel(self):
        return self.__unique_panel

    def has_unique_panel(self):
        return self.__unique_panel is not None
