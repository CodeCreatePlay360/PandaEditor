from direct.showbase.DirectObject import DirectObject
from editor.constants import TAG_IGNORE


class Object(DirectObject, object):
    def __init__(self, *args, **kwargs):
        DirectObject.__init__(self)
        
        # Default camera to base camera if None is specified
        self.camera = kwargs.pop('camera', base.camera)

        # Default root node to render if None is specified
        self.rootNp = kwargs.pop('render', base.render)

        # Default root 2d node to render2d if None is specified
        self.root2d = kwargs.pop('root2d', base.render2d)

        # Default root aspect 2d node to aspect2d if None is specified
        self.rootA2d = kwargs.pop('rootA2d', base.aspect2d)

        # Default root pixel 2d node to pixel2d if None is specified
        self.rootP2d = kwargs.pop('rootP2d', base.pixel2d)

        # Default win to base.win if None specified.
        self.win = kwargs.pop('win', base.win)
        
        # Default mouse watcher node to base.win if None specified.
        self.mouseWatcherNode = kwargs.pop('mouseWatcherNode', base.mouseWatcherNode)

        # default tag to IGNORE if none is specified
        self.tag = kwargs.pop("tag", TAG_IGNORE)
