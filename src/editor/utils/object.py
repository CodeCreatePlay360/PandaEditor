from direct.showbase.DirectObject import DirectObject


class Object(DirectObject, object):
    def __init__(self, **kwargs):
        DirectObject.__init__(self)

        self.camera = kwargs.pop('camera', None)
        self.rootNp = kwargs.pop('render', None)
        self.root2d = kwargs.pop('render2d', None)
        self.rootA2d = kwargs.pop('renderA2d', None)
        self.rootP2d = kwargs.pop('renderP2d', None)
        self.win = kwargs.pop('win', None)
        self.mouseWatcherNode = kwargs.pop('mouseWatcherNode', None)
