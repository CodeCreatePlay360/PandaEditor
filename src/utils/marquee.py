from panda3d.core import NodePath, CardMaker, LineSegs, Point2
from .singleTask import SingleTask

TOLERANCE = 1e-3


class Marquee(NodePath, SingleTask):
    
    """Class representing a 2D marquee drawn by the mouse."""
    
    def __init__(self, name, **kwargs):
        SingleTask.__init__(self, name, **kwargs)
        
        self.cam = kwargs.pop("camera")
        self.render2d = kwargs.pop("render2D")
        self.mwn = kwargs.pop("mwn")
        color = kwargs.pop('Color', (1, 1, 1, 0.2))

        # Create a card maker
        cm = CardMaker(name)
        cm.setFrame(0, 1, 0, 1)

        # Init the node path, wrapping the card maker to make a rectangle
        NodePath.__init__(self, cm.generate())
        self.setColor(color)

        self.setTransparency(1)
        self.reparentTo(self.render2d)
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
        if self.mwn.hasMouse():
            # Get the other marquee point and scale to fit
            pos = self.mwn.getMouse() - self.init_mouse_pos
            self.setScale(pos[0] if pos[0] else TOLERANCE, 1, pos[1] if pos[1] else TOLERANCE)
            
    def on_start(self):
        # Move the marquee to the mouse position and show it
        self.init_mouse_pos = Point2(self.mwn.getMouse())
        self.setPos(self.init_mouse_pos[0], 1, self.init_mouse_pos[1])
        self.setScale(TOLERANCE, 1, TOLERANCE)
        self.show()
                    
    def on_stop(self):
        # Hide the marquee
        self.hide()
    
    def is_nodepath_inside(self, np):
        """Test if the specified node path lies within the marquee area."""

        np_world_pos = np.getPos(self.render2d)
        p3 = self.cam.getRelativePoint(self.render2d, np_world_pos)

        # Convert it through the lens to render2d coordinates
        p2 = Point2()

        if not self.cam.node().getLens().project(p3, p2):
            return False

        # Test point is within bounds of the marquee
        _min, _max = self.getTightBounds()

        if (_min.getX() < p2.getX() < _max.getX() and
                _min.getZ() < p2.getY() < _max.getZ()):
            return True

        return False
