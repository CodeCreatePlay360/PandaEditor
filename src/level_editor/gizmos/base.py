from panda3d.core import Point3, Vec3, Plane, NodePath
from .constants import *
from utils import SingleTask, math
from system import Systems


class Base(NodePath, SingleTask):

    def __init__(self, name, *args, **kwargs):
        NodePath.__init__(self, name)
        SingleTask.__init__(self, name, *args, **kwargs)
        
        self.mwn = kwargs.pop("mwn")
        self.render = kwargs.pop("rootNP")
        self.camera = kwargs.pop("camera")

        self.attached_nps = []
        self.axes = []
        self.size = 1

        self.last_axis_point = None
        self.start_axis_point = None
        self.init_np_xforms = None

        self.dragging = False
        self.planar = False
        self.local = False

        # Set this node up to be drawn over everything else
        self.setBin('fixed', 40)
        self.setDepthTest(False)
        self.setDepthWrite(False)

    def on_update(self):
        """
        Update method called every frame. Run the transform method if the user
        is dragging, and keep it the same size on the screen.
        """
        if self.dragging:
            self.transform()

        scale = (self.getPos() - self.camera.getPos()).length() / 6
        self.setScale(scale)

    def on_start(self):
        """
        Starts the gizmo adding the task to the task manager, refreshing it
        and deselecting all axes except the default one.
        """
        self.refresh()

        # Select the default axis, deselect all others
        for axis in self.axes:
            if axis.default:
                axis.select()
            else:
                axis.deselect()

        self.accept_events()

    def on_stop(self):
        """
        Stops the gizmo by hiding it and removing its update task from the
        task manager.
        """
        # Hide the gizmo and ignore all events
        self.detachNode()

        Systems.demon.event_manager.remove(''.join([self.name, '-mouse1']), self.on_node_mouse1_down)
        Systems.demon.event_manager.remove(''.join([self.name, '-control-mouse1']), self.on_node_mouse1_down)
        Systems.demon.event_manager.remove(''.join([self.name, '-mouse-over']), self.on_node_mouse_over)
        Systems.demon.event_manager.remove(''.join([self.name, '-mouse-leave']), self.on_node_mouse_leave)

    def accept_events(self):
        """Bind all events for the gizmo."""
        Systems.demon.accept('mouse1-up', self.on_mouse_up)
        Systems.demon.accept('mouse2-up', self.on_mouse_up)
        Systems.demon.accept('mouse2', self.on_mouse2_down)

        Systems.demon.event_manager.register(''.join([self.name, '-mouse1']), self.on_node_mouse1_down)
        Systems.demon.event_manager.register(''.join([self.name, '-control-mouse1']), self.on_node_mouse1_down)
        Systems.demon.event_manager.register(''.join([self.name, '-mouse-over']), self.on_node_mouse_over)
        Systems.demon.event_manager.register(''.join([self.name, '-mouse-leave']), self.on_node_mouse_leave)

    def transform(self):
        """
        Override this method to provide the gizmo with transform behavior.
        """
        pass

    def attach_nodepaths(self, nps):
        """
        Attach node paths to the gizmo. This won't affect the node's position
        in the scene graph, but will transform the objects with the gizmo.
        """
        self.attached_nps = nps

    def set_size(self, factor):
        """
        Used to scale the gizmo by a factor, usually by 2 (scale up) and 0.5
        (scale down). Set both the new size for the gizmo also call set size
        on all axes.
        """
        self.size *= factor

        # Each axis may have different rules on how to appear when scaled, so
        # call set size on each of them
        for axis in self.axes:
            axis.set_size(self.size)

    def get_axis(self, collEntry):
        """
        Iterate over all axes of the gizmo, return the axis that owns the
        solid responsible for the collision.
        """
        for axis in self.axes:
            if collEntry.getIntoNode() in axis.coll_nodes:
                return axis

        # No match found, return None
        return None

    def get_selected_axis(self):
        """Return the selected axis of the gizmo."""
        for axis in self.axes:
            if axis.selected:
                return axis

    def reset_axes(self):
        """
        Reset the default colours and flag as unselected for all axes in the 
        gizmo.
        """
        for axis in self.axes:
            axis.deselect()

    def refresh(self):
        """
        If the gizmo has node paths attached to it then move the gizmo into
        position, set its orientation and show it. Otherwise, hide the gizmo.
        """

        if self.attached_nps:
            # Show the gizmo
            self.reparentTo(self.rootNp)

            # Move the gizmo into position
            if len(self.attached_nps) > 1:
                mean_pos = Vec3()
                for i in range(len(self.attached_nps)):
                    mean_pos += self.attached_nps[i].getPos(self.rootNp)
                mean_pos /= len(self.attached_nps)

                self.setPos(mean_pos)

            else:
                self.setPos(self.attached_nps[0].getPos(self.rootNp))

            # Only set the orientation of the gizmo if in local mode
            if self.local:
                self.setHpr(self.attached_nps[0].getHpr(self.rootNp))
            else:
                self.setHpr(self.rootNp.getHpr())

        else:

            # Hide the gizmo
            self.detachNode()

    def on_mouse_up(self):
        """
        Set the dragging flag to false and reset the size of the gizmo on the
        mouse button is released.
        """
        self.dragging = False
        self.set_size(1)

    def on_node_mouse_leave(self):
        """
        Called when the mouse leaves the collision object. Remove the
        highlight from any axes which aren't selected.
        """
        for axis in self.axes:
            if not axis.selected:
                axis.unhighlight()

    def on_node_mouse1_down(self, planar, collEntry):
        self.planar = planar
        self.dragging = True

        # Store the attached node path's transforms.
        self.init_np_xforms = [np.getTransform() for np in self.attached_nps]

        # Reset colours and deselect all axes, then get the one which the
        # mouse is over
        self.reset_axes()
        axis = self.get_axis(collEntry)
        if axis is not None:
            # Select it
            axis.select()

            # Get the initial point where the mouse clicked the axis
            self.start_axis_point = self.get_axis_point(axis)
            self.last_axis_point = self.get_axis_point(axis)

    def on_mouse2_down(self):
        """
        Continue transform operation if user is holding mouse2 but not over
        the gizmo.
        """
        axis = self.get_selected_axis()
        if axis is not None and self.attached_nps and self.mouseWatcherNode.hasMouse():
            self.dragging = True
            self.init_np_xforms = [np.getTransform() for np in self.__attached_nps]
            self.start_axis_point = self.get_axis_point(axis)
            self.last_axis_point = self.get_axis_point(axis)

    def on_node_mouse_over(self, collEntry):
        """Highlights the different axes as the mouse passes over them."""
        # Don't change highlighting if in dragging mode
        if self.dragging:
            return

        # Remove highlight from all unselected axes
        for axis in self.axes:
            if not axis.selected:
                axis.unhighlight()

        # Highlight the axis which the mouse is over
        axis = self.get_axis(collEntry)
        if axis is not None:
            axis.highlight()

    def get_mouse_plane_collision_point(self, pos, nrml):
        """
        Return the collision point of a ray fired through the mouse and a
        plane with the specified normal.
        """
        # Fire a ray from the camera through the mouse 
        mp = self.mwn.getMouse()
        p1 = Point3()
        p2 = Point3()
        self.camera.node().getLens().extrude(mp, p1, p2)
        p1 = self.rootNp.getRelativePoint(self.camera, p1)
        p2 = self.rootNp.getRelativePoint(self.camera, p2)

        # Get the point of intersection with a plane with the normal
        # specified
        p = Point3()
        Plane(nrml, pos).intersectsLine(p, p1, p2)

        return p

    def get_axis_point(self, axis):
        """
        Return the point of intersection for the mouse picker ray and the axis
        in the gizmo root node space.
        """
        # Get the axis vector - by default this is the selected axis'
        # vector unless we need to use the camera's look vector
        if axis.vector == CAMERA_VECTOR:
            axisVector = self.rootNp.getRelativeVector(self.camera, Vec3(0, -1, 0))
        else:
            axisVector = self.rootNp.getRelativeVector(self, axis.vector)

        # Get the transform plane's normal. If we're transforming in
        # planar mode use the axis vector as the plane normal, otherwise
        # get the normal of a plane along the selected axis
        if self.planar or axis.planar:
            return self.get_mouse_plane_collision_point(self.getPos(), axisVector)
        else:

            # Get the cross of the camera vector and the axis vector - a
            # vector of 0, 1, 0 in camera space is coming out of the lens
            camVector = self.rootNp.getRelativeVector(self.camera, Vec3(0, 1, 0))
            camAxisCross = camVector.cross(axisVector)

            # Cross this back with the axis to get a plane's normal
            planeNormal = camAxisCross.cross(axisVector)
            p = self.get_mouse_plane_collision_point(self.getPos(), planeNormal)
            return math.closest_point_to_line(p, self.getPos(), self.getPos() +
                                              axisVector)
