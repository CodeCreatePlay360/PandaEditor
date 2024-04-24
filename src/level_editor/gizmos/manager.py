from panda3d.core import DirectionalLight
from utils.mousePicker import MousePicker


class Manager(object):
    def __init__(self, **kwargs):
        object.__init__(self)

        self.__demon = kwargs.pop("demon")
        self.__cam = kwargs.pop("camera")
        self.__render = kwargs.pop("render")

        self.__gizmos = {}
        self.local = False
        self.__active_gizmo = None

        # Create gizmo manager mouse picker
        self.__picker = MousePicker('GizmoMgrMousePicker',
                                    demon=self.__demon,
                                    camera=self.__cam,
                                    render=self.__render,
                                    mwn=kwargs.pop("mwn"),
                                    evt_mgr=self.__demon.event_manager)
        self.__picker.start()

        # Create a directional light and attach it to the camera so the gizmos
        # don't look flat
        dl = DirectionalLight('GizmoManagerSunLight')
        self.__directional_light = self.__cam.attachNewNode(dl)

    def add_gizmo(self, gizmo):
        """Add a gizmo to be managed by the gizmo manager."""
        gizmo.rootNp = self.__render
        self.__gizmos[gizmo.getName()] = gizmo

        for axis in gizmo.axes:
            axis.setLight(self.__directional_light)

    def get_gizmo(self, name):
        """
        Find and return a gizmo by name, return None if no gizmo with the
        specified name exists.
        """
        if name in self.__gizmos:
            return self.__gizmos[name]

        return None

    def get_active_gizmo(self):
        """Return the active gizmo."""
        return self.__active_gizmo

    def set_active_gizmo(self, name):
        """
        Stops the currently active gizmo then finds the specified gizmo by
        name and starts it.
        """
        # Stop the active gizmo
        if self.__active_gizmo is not None:
            self.__active_gizmo.stop()

        # Get the gizmo by name and start it if it is a valid gizmo

        self.__active_gizmo = self.get_gizmo(name)
        if self.__active_gizmo is not None:
            self.__active_gizmo.start()

    def refresh_active_gizmo(self):
        """Refresh the active gizmo if there is one."""
        if self.__active_gizmo is not None:
            self.__active_gizmo.refresh()

    def set_local(self, val):
        self.local = val
        for gizmo in self.__gizmos.values():
            gizmo.local = val
        self.refresh_active_gizmo()

    def set_size(self, factor):
        """Resize the gizmo by a factor."""
        for gizmo in self.__gizmos.values():
            gizmo.set_size(factor)

    def attach_nodepaths(self, nps=None):
        """Attach node paths to be transformed by the gizmos."""

        if nps is None:
            nps = []

        for gizmo in self.__gizmos.values():
            gizmo.attach_nodepaths(nps)

    def is_dragging(self):
        """
        Return True if the active gizmo is in the middle of a dragging
        operation, False otherwise.
        """
        return self.__active_gizmo is not None and self.__active_gizmo.dragging
