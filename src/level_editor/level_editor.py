import panda3d.core as p3d
from system import Systems
from commons.constants import *

from .selection import MousePicker, Selection
from .constants import GizmoIconsPaths

from . import gizmos

from utils import geometry


POS_GIZMO = "PosGizmo"
ROT_GIZMO = "RotGizmo"
SCALE_GIZMO = "ScaleGizmo"


class LevelEditor(object):
    def __init__(self, demon):
        object.__init__(self)
        self.__demon = demon
        
        # -- create instance attributes
        # shaders
        self.__billboard_shader = None
        self.__gradient_shader = None
        self.__gizmo_shader = None
        
        # xform gizmos
        self.__xform_gizmo_mgr = None
        self.__xform_gizmo_np = None
        self.__active_xform_gizmo = None

        # editor render to keep editor only geometry out of
        # main / game rendering
        self.__ed_render = None
                
        # selection system
        self.__selection = None
        
    def init(self):
        # create an editor render and reparent main render to it,
        # to keep editor only geometry out of main / game rendering
        self.__ed_render = p3d.NodePath("EditorRender")
        
        # load shader
        self.load_shaders()

        # setup selection and gizmo manager
        self.__selection = Selection(self.__ed_render)
        self.setup_xform_gizmos()
        
        # finally, setup editor window rendering
        self.setup_editor_rendering()
        
        # accept and bind events
        self.__demon.accept("mouse1", self.on_mouse1)
        self.__demon.accept("shift-mouse1", self.on_mouse1, True)
        self.__demon.accept("mouse1-up", self.on_mouse1_up)

        self.__demon.accept("w", self.set_active_gizmo, POS_GIZMO)
        self.__demon.accept("r", self.set_active_gizmo, ROT_GIZMO)
        self.__demon.accept("s", self.set_active_gizmo, SCALE_GIZMO)
        self.__demon.accept("q", self.set_active_gizmo, None)
        self.__demon.accept("space", self.__xform_gizmo_mgr.set_local,
                            lambda: (not self.__xform_gizmo_mgr.local))
                
        # finally, start the level editor update
        task = p3d.PythonTask(self.on_update, "LEUpdate")
        p3d.AsyncTaskManager.getGlobalPtr().add(task)
        
    def setup_editor_rendering(self):
        # 01. reparent render to ed_render to keep editor only geo out of
        # main scene graph
        self.__demon.engine.render.reparentTo(self.__ed_render)
        
        # 02. reparent editor only geo to ed_render
        self.__demon.engine.cam.reparent_to(self.__ed_render)
        self.__demon.engine.grid_np.reparentTo(self.__ed_render)

        # 03. set bitmaks on editor only geo to hide from cameras with
        # with GAME_CAMERA_MASK
        self.__demon.engine.grid_np.hide(GAME_CAMERA_MASK)
        
        self.__xform_gizmo_np.hide(GAME_CAMERA_MASK)
        for key in self.__xform_gizmo_mgr.gizmos.keys():
            gizmo = self.__xform_gizmo_mgr.gizmos[key]
            gizmo.hide(GAME_CAMERA_MASK)
        
        # 04. finally, set masks on cameras as well
        # editor camera should render both game and editor geo and game
        # camera would render game geo only.
        ed_cam_node = self.__demon.engine.cam.node()
        ed_cam_node.setCameraMask(ED_CAMERA_MASK|GAME_CAMERA_MASK)

    def load_shaders(self):
        pass
        
    def on_update(self, task):
        return task.DS_cont
        
    def on_mouse1(self, shift=False):
        if not self.__xform_gizmo_mgr.is_dragging() and \
        not self.__demon.engine.mw.node().is_button_down(p3d.KeyboardButton.alt()):
            self.__selection.start_drag_select(shift)

        elif self.__xform_gizmo_mgr.is_dragging():
            pass

    def on_mouse1_up(self):
        if self.__selection.marquee.is_running():
            last_selections = [np for np in self.__selection.selected_nps]
            nps = self.__selection.stop_drag_select()

            if len(nps) > 0:
                # update gizmos
                self.__xform_gizmo_mgr.attach_nodepaths(nps)
                self.__xform_gizmo_mgr.refresh_active_gizmo()
            else:
                self.deselect_all()

        elif self.__xform_gizmo_mgr.is_dragging():
            pass
        
    def on_mouse_1_drag(self):
        pass

    def select_all(self):
        pass

    def deselect_all(self):
        self.__selection.selected_nps = []

        # update gizmos
        self.__xform_gizmo_mgr.attach_nodepaths(None)
        self.__xform_gizmo_mgr.refresh_active_gizmo()

    def setup_xform_gizmos(self):
        """Create gizmo manager."""
        root_np = p3d.NodePath("Gizmos")
        root_np.reparent_to(self.__ed_render)

        kwargs = {
            "camera": Systems.cam,
            "rootNP": root_np,
            "render2D": Systems.render2d,
            "win": Systems.win,
            "mwn": Systems.mw.node(),  # mouse watcher node,
        }
        
        gizmo_mgr = gizmos.Manager(**kwargs)
        
        pos_gizmo = gizmo_mgr.add_gizmo(gizmos.Translation(POS_GIZMO, **kwargs))
        rot_gizmo = gizmo_mgr.add_gizmo(gizmos.Rotation(ROT_GIZMO, **kwargs))
        scale_gizmo = gizmo_mgr.add_gizmo(gizmos.Scale(SCALE_GIZMO, **kwargs))
        
        self.__xform_gizmo_mgr = gizmo_mgr
        self.__xform_gizmo_np = root_np

    def set_active_gizmo(self, gizmo):
        if gizmo is not "None":
            self.__active_xform_gizmo = gizmo

        self.__xform_gizmo_mgr.set_active_gizmo(gizmo)
        self.__xform_gizmo_mgr.refresh_active_gizmo()
                
    def add_light(self, light_type=None):
        if not isinstance(light_type, LightType):
            print("[LevelEditor] Invalid argument to method 'add_light'.")
            return

        # create gizmo geometry and add it to render
        points = geometry.GetPointsForSquare(1, 1, True)
        points = [p3d.Point3(x, 0, y) for x, y in points]
        tex_coords = [(0.0, 1.0), (0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]                
        gizmo_np = geometry.Polygon(points,
                                    label=light_type.name,
                                    texcoords=tex_coords)
        
        # get, set gizmo icon
        if light_type.Point:
            path_ = GizmoIconsPaths.point_light()
            
        elif light_type.Directional:
            light_node = GizmoIconsPaths.point_light()
            
        elif light_type.Spot:
            light_node = GizmoIconsPaths.point_light()
            
        elif light.Ambient:
            light_type_node = GizmoIconsPaths.point_light()
            
        '''
        rm = self.__demon.engine.resource_manager
        icon = rm.load_texture(path_)
        gizmo_np.setTexture(icon, 1)
        
        # set shader
        gizmo_np.setShader(self.__gizmo_shader)
        gizmo_np.setShaderInput("scale", 1.0)
        gizmo_np.setShaderInput("gizmoColor", (0.25, 0.5, 1))
        gizmo_np.setShaderInput("colorIntensity", 1)
        
        # create panda3D light object
        light_np = self.__project.game.active_scene.add_light(light_type)
        '''
        
        # finally, add it to render
        render = self.__project.game.active_scene.render
        gizmo_np.reparent_to(render)
        light_np.reparent_to(gizmo_np)

    def add_camera(self):
        pass
    
    def add_node(self, path):
        pass
