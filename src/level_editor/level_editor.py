from panda3d.core import NodePath, KeyboardButton
from system import Systems
from .selection import Selection
from . import gizmos


POS_GIZMO = "PosGizmo"
ROT_GIZMO = "RotGizmo"
SCALE_GIZMO = "ScaleGizmo"


class LevelEditor(object):
    def __init__(self, demon):
        object.__init__(self)
        self.demon = demon

        self.__ed_render = None
        self.__gizmo_mgr = None
        self.__active_gizmo = None

        # create an editor render and reparent main render to it,
        # to keep editor only geometry out of main rendering
        self.__ed_render = NodePath("EditorRender")
        self.demon.engine.render.reparentTo(self.__ed_render)
        self.demon.engine.grid_np.reparentTo(self.__ed_render)

        self.__selection = Selection(demon=self.demon)
        self.setup_gizmo_manager()

        self.demon.accept("mouse1", self.on_mouse1)
        self.demon.accept("shift-mouse1", self.on_mouse1, True)
        self.demon.accept("mouse1-up", self.on_mouse1_up)

        self.demon.accept("w", self.set_active_gizmo, POS_GIZMO)
        self.demon.accept("r", self.set_active_gizmo, ROT_GIZMO)
        self.demon.accept("s", self.set_active_gizmo, SCALE_GIZMO)
        self.demon.accept("q", self.set_active_gizmo, None)
        self.demon.accept("space", self.__gizmo_mgr.set_local, lambda: (not self.__gizmo_mgr.local))
        
    def on_mouse1(self, shift=False):
        if not self.__gizmo_mgr.is_dragging() and not self.demon.engine.mwn.is_button_down(KeyboardButton.alt()):
            self.__selection.start_drag_select(shift)

        elif self.__gizmo_mgr.is_dragging():
            pass

    def on_mouse1_up(self):
        if self.__selection.marquee.is_running():
            last_selections = [np for np in self.__selection.selected_nps]
            nps = self.__selection.stop_drag_select()

            # select nps and start transform
            if len(nps) > 0:
                self.__selection.set_selected(nps)
                # update gizmos
                self.__gizmo_mgr.attach_nodepaths(nps)
                self.__gizmo_mgr.refresh_active_gizmo()
            else:
                self.deselect_all()

        elif self.__gizmo_mgr.is_dragging():
            pass
        
    def on_mouse_1_drag(self):
        pass

    def select_all(self):
        pass

    def deselect_all(self):
        self.__selection.selected_nps = []

        # update gizmos
        self.__gizmo_mgr.attach_nodepaths(None)
        self.__gizmo_mgr.refresh_active_gizmo()

    def setup_gizmo_manager(self):
        """Create gizmo manager."""
        root_np = NodePath("Gizmos")
        root_np.reparent_to(self.__ed_render)

        kwargs = {
            "demon": self.demon,
            "camera": Systems.engine.cam,
            "render": Systems.engine.render,
            "render2D": Systems.engine.render2D,
            "win": Systems.engine.win,
            "mwn": Systems.engine.mwn,  # mouse watcher node,
            "rootNP": root_np,
        }

        self.__gizmo_mgr = gizmos.Manager(**kwargs)
        self.__gizmo_mgr.add_gizmo(gizmos.Translation(POS_GIZMO, **kwargs))
        self.__gizmo_mgr.add_gizmo(gizmos.Rotation(ROT_GIZMO, **kwargs))
        self.__gizmo_mgr.add_gizmo(gizmos.Scale(SCALE_GIZMO, **kwargs))

        '''
        for key in self.__gizmo_mgr._gizmos.keys():
            gizmo = self.__gizmo_mgr._gizmos[key]
            gizmo.hide(ed_constants.GAME_GEO_MASK)
        '''

    def set_active_gizmo(self, gizmo):
        if gizmo is not "None":
            self.__active_gizmo = gizmo

        self.__gizmo_mgr.set_active_gizmo(gizmo)
        self.__gizmo_mgr.refresh_active_gizmo()
