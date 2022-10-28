from editor.core.component import Component


class Controller(Component):
    def __init__(self, *args, **kwargs):
        """__init__ should not be used for anything except for variable declaration"""
        Component.__init__(self, *args, **kwargs)
