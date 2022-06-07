from editor.core.pModBase import PModBase


class EditorPlugin(PModBase):
    def __init__(self, *args, **kwargs):
        PModBase.__init__(self, *args, **kwargs)

        self._le = kwargs.pop("level_editor", None)
        self._globals = kwargs.pop("globals", None)
        self._panel = None
        self._unique_panel = None

        self.discarded_attrs = "_wx_panel"
        self.discarded_attrs = "_le"
        self.discarded_attrs = "_unique_panel"

    def request_unique_panel(self, unique_panel_name: str):
        if type(unique_panel_name) is str:
            self._unique_panel = unique_panel_name

    # TODO replace this with properties
    def get_unique_panel(self):
        return self._unique_panel

    # TODO replace this with properties
    def has_unique_panel(self):
        return self._unique_panel is not None
