
class ResourceDragDropData(object):
    PREVIEW_TILES_PANEL = 1
    RESOURCE_BROWSER = 2

    def __init__(self, drag_source):
        self.__paths = []
        self.__drag_source = drag_source

    def set_source(self, data: list):
        self.__paths = data

    def __repr__(self):
        return "DragDropData"

    @property
    def paths(self):
        return self.__paths

    @property
    def drag_source(self):
        return self.__drag_source
