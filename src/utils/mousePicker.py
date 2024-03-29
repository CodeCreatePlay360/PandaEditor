from panda3d.core import CollisionTraverser, CollisionHandlerQueue, BitMask32
from panda3d.core import CollisionNode, CollisionRay
from .singleTask import SingleTask


class MousePicker(SingleTask):
    """
    Class to represent a ray fired from the input camera lens using the mouse.
    """

    def __init__(self, name, cam, render, mwn, *args, **kwargs):
        SingleTask.__init__(self, name, *args, **kwargs)
        
        self.__camera = cam
        self.__render = render
        self.__mwn = mwn
        
        self.__from_collide_mask = kwargs.pop('fromCollideMask', None)
        self.__node = None
        self.__coll_entry = None

        # Create collision nodes
        self.__coll_trav = CollisionTraverser()
        self.__coll_handler = CollisionHandlerQueue()
        self.__picker_ray = CollisionRay()

        # Create collision ray
        picker_node = CollisionNode(self.name)
        picker_node.addSolid(self.__picker_ray)
        picker_node.setIntoCollideMask(BitMask32.allOff())
        picker_np = self.__camera.attachNewNode(picker_node)
        
        self.__coll_trav.addCollider(picker_np, self.__coll_handler)

        # Create collision mask for the ray if one is specified
        if self.__from_collide_mask is not None:
            picker_node.setFromCollideMask(self.__from_collide_mask)
            
        '''
        # Bind mouse button events
        eventNames = ['mouse1', 'control-mouse1', 'mouse1-up']
        for eventName in eventNames:
            self.accept(eventName, self.FireEvent, [eventName])
        '''

    def on_update(self, x=None, y=None):

        # Update the ray's position
        if self.__mwn.hasMouse():
            mp = self.__mwn.getMouse()
            x, y = mp.getX(), mp.getY()

        if x is None or y is None:
            return

        self.__picker_ray.setFromLens(self.__camera.node(), x, y)

        # Traverse the hierarchy and find collisions
        self.__coll_trav.traverse(self.__render)
        
        if self.__coll_handler.getNumEntries():
            # If we have hit something, sort the hits so that the closest is first
            self.__coll_handler.sortEntries()
            collEntry = self.__coll_handler.getEntry(0)
            node = collEntry.getIntoNode()

            # If this node is different to the last node, send a mouse leave
            # event to the last node, and a mouse enter to the new node
            if node != self.__node:
                if self.__node is not None:
                    pass
                    # messenger.send('%s-mouse-leave' % self.__node.getName(), [self.__coll_entry])
                # messenger.send('%s-mouse-enter' % node.getName(), [collEntry])

            # Send a message containing the node name and the event over name,
            # including the collision entry as arguments
            # messenger.send('%s-mouse-over' % node.getName(), [collEntry])

            # Keep these values
            self.__coll_entry = collEntry
            self.__node = node

        elif self.__node is not None:

            # No collisions, clear the node and send a mouse leave to the last
            # node that stored
            # messenger.send('%s-mouse-leave' % self.__node.getName(), [self.__coll_entry])
            self.__node = None

    def FireEvent(self, event):
        """
        Send a message containing the node name and the event name, including
        the collision entry as arguments.
        """
        if self.__node is not None:
            messenger.send('%s-%s' % (self.__node.getName(), event), [self.__coll_entry])

    def get_first_np(self):
        """
        Return the first node in the collision queue if there is one, None
        otherwise.
        """
        if self.__coll_handler.getNumEntries():
            collEntry = self.__coll_handler.getEntry(0)
            self.__node = collEntry.getIntoNodePath()
            return self.__node
        return None
