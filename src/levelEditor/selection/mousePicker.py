from panda3d.core import CollisionTraverser, CollisionHandlerQueue, BitMask32
from panda3d.core import CollisionNode, CollisionRay
from panda3d.core import AsyncTaskManager, PythonTask
from system import Systems
from utils.singleTask import SingleTask


class MousePicker:
    """
    Class to represent a ray fired from the input camera lens using the mouse.
    """

    def __init__(self, name, create_update_task=False, **kwargs):
        self.__mwn = kwargs.pop("mwn")
        self.__render = kwargs.pop("render")
        self.__camera = kwargs.pop("camera")
        
        self.__coll_handler = CollisionHandlerQueue()
        self.__coll_entry = None
        self.__node = None
                          
        # cache
        self.__last_x, self.__last_y = 0, 0
                              
        # Create collision ray
        self.__picker_ray = CollisionRay()
        
        # Create collision node
        picker_node = CollisionNode('%s%s' % (name, "CollisionNode"))
        picker_node.addSolid(self.__picker_ray)
        picker_node.setIntoCollideMask(BitMask32.allOff())
        
        # Create collision mask for the ray if one is specified
        from_collide_mask = kwargs.pop('from_collide_mask', None)
        if from_collide_mask is not None:
            picker_node.setFromCollideMask(from_collide_mask)
        
        picker_np = self.__camera.attachNewNode(picker_node)

        # add picker np to coll traverser
        Systems.coll_trav.addCollider(picker_np, self.__coll_handler)

        # Bind mouse button events
        for event_name in ['mouse1', 'control-mouse1', 'mouse1-up']:
            Systems.demon.accept(event_name, self.fire_event, event_name)
            
        if create_update_task:
            # create a task object
            task = PythonTask(self.update, '%s%s' % (name, "Task"))
            AsyncTaskManager.getGlobalPtr().add(task)

    def update(self, task=None, x=None, y=None):
        # Update the ray's position
        if self.__mwn.hasMouse():
            x = self.__mwn.getMouse().getX()
            y = self.__mwn.getMouse().getY()

        if x is None or y is None:
            return task.DS_cont if task else None
        
        
        if x == self.__last_x and y == self.__last_y:
            return task.DS_cont if task else None
        else:
            self.__last_x, self.__last_y = x, y
        

        self.__coll_handler.clearEntries()
        self.__picker_ray.setFromLens(self.__camera.node(), x, y)
                
        # Traverse the hierarchy and find collisions
        Systems.coll_trav.traverse(self.__render)

        if self.__coll_handler.getNumEntries():            
            # If we have hit something, sort the hits so that the closest is first
            self.__coll_handler.sortEntries()
            collEntry =self.__coll_handler.getEntry(0)
            node = collEntry.getIntoNode()

            # If this node is different to the last node, send a mouse leave
            # event to the last node, and a mouse enter to the new node
            if node != self.__node:
                if self.__node is not None:
                    Systems.evt_mgr.trigger('%s-mouse-leave' % self.__node.getName())
                    
                Systems.evt_mgr.trigger('%s-mouse-enter' % node.getName(), [collEntry])

            # Send a message containing the node name and the event over name,
            # including the collision entry as arguments
            Systems.evt_mgr.trigger('%s-mouse-over' % node.getName(), collEntry)
            
            # Keep these values
            self.__coll_entry = collEntry
            self.__node = node

        elif self.__node is not None:
            # No collisions, clear the node and send a mouse leave to the last
            # node that stored
            # messenger.send('%s-mouse-leave' % self.__node.getName(), [self.__coll_entry])
            Systems.evt_mgr.trigger('%s-mouse-leave' % self.__node.getName())
            self.__node = None
            
        if task:
            return task.DS_cont

    def fire_event(self, event):
        """
        Send a message containing the node name and the event name, including
        the collision entry as arguments.
        """

        if self.__node is not None:
            args = [False, self.__coll_entry]
            Systems.evt_mgr.trigger('%s-%s' % (self.__node.getName(), event),
                                    False, self.__coll_entry)

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
