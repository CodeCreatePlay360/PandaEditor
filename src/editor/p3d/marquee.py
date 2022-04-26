from panda3d.core import NodePath, CardMaker, LineSegs, Point2
from editor.p3d import SingleTask

TOLERANCE = 1e-3


class Marquee(NodePath, SingleTask):
    
    """Class representing a 2D marquee drawn by the mouse."""
    
    def __init__(self, *args, **kwargs):
        color = kwargs.pop('colour', (1, 1, 1, 0.2))
        SingleTask.__init__(self, *args, **kwargs)

        # Create a card maker
        cm = CardMaker(self._name)
        cm.setFrame(0, 1, 0, 1)

        # Init the node path, wrapping the card maker to make a rectangle
        NodePath.__init__(self, cm.generate())
        self.setColor(color)

        self.setTransparency(1)
        self.reparentTo(self.root2d)
        self.hide()
        
        # Create the rectangle border
        ls = LineSegs()
        ls.moveTo(0, 0, 0)
        ls.drawTo(1, 0, 0)
        ls.drawTo(1, 0, 1)
        ls.drawTo(0, 0, 1)
        ls.drawTo(0, 0, 0)
        
        # Attach border to rectangle
        self.attachNewNode(ls.create())
        
    def on_update(self):
        """
        Called every frame to keep the marquee scaled to fit the region marked
        by the mouse's initial position and the current mouse position.
        """
        # Check for mouse first, in case the mouse is outside the Panda window
        if self.mouseWatcherNode.hasMouse():
            # Get the other marquee point and scale to fit
            pos = self.mouseWatcherNode.getMouse() - self.initMousePos
            self.setScale(pos[0] if pos[0] else TOLERANCE, 1, pos[1] if pos[1] else TOLERANCE)
            
    def on_start(self):
        # Move the marquee to the mouse position and show it
        self.initMousePos = Point2(self.mouseWatcherNode.getMouse())
        self.setPos(self.initMousePos[0], 1, self.initMousePos[1])
        self.show()
                    
    def on_stop(self):
        # Hide the marquee
        self.hide()
    
    def IsNodePathInside(self, np):
        """Test if the specified node path lies within the marquee area."""

        np_world_pos = np.getPos(self.rootNp)
        p3 = self.camera.getRelativePoint(self.rootNp, np_world_pos)

        # Convert it through the lens to render2d coordinates
        p2 = Point2()

        if not self.camera.node().getLens().project(p3, p2):
            return False

        # Test point is within bounds of the marquee
        _min, _max = self.getTightBounds()

        if (_min.getX() < p2.getX() < _max.getX() and
                _min.getZ() < p2.getY() < _max.getZ()):
            return True

        return False
