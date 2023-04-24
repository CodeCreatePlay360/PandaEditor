import panda3d.core as p3d_core
import editor.constants as constants

from direct.showbase import ShowBase as sb
from panda3d.core import NodePath, Camera, OrthographicLens, PGTop
from editor.core import EditorCamera
from editor.globals import editor


class ShowBase(sb.ShowBase):
    def __init__(self, ed_wx_win):
        sb.ShowBase.__init__(self)
        base.cTrav = None

        self.scene_win = ed_wx_win  # wx python window
        self.main_win = None  # Panda3d editor window we will render into

        self.edRender = None
        self.edRender2d = None
        self.ed_camera = None
        self.ed_camera_2d = None

        self.dr = None
        self.dr2d = None
        self.edDr = None
        self.edDr2d = None
        self.__ed_aspect2d = None

        self.ed_mouse_watcher = None
        self.ed_mouse_watcher_node = None

        self.ed_mouse_watcher_2d = None
        self.ed_mouse_watcher_node_2d = None

        self.forcedAspectWins = []
        self.update_task = None

    def finish_init(self):
        self.init_editor_win()
        self.setup_editor_window()

        # Add the editor window, camera and pixel 2d to the list of forced
        # aspect windows so aspect is fixed when the window is resized.
        self.forcedAspectWins.append((self.main_win, self.ed_camera, self.__ed_aspect2d))

        # turn on per pixel lightning
        self.edRender.setShaderAuto()

    def init_editor_win(self):
        self.scene_win.initialize(use_main_win=True)

    def setup_editor_window(self):
        """set up an editor rendering, it included setting up 2d and 3d display regions,
        an editor scene graph and editor mouse watchers"""

        # ------------------------------------------- #
        # clear existing / default 3d display regions
        self.dr = self.cam.node().getDisplayRegion(0)
        self.dr.setClearColorActive(False)
        self.dr.setClearColor(self.getBackgroundColor())
        self.dr.setActive(False)
        self.dr.setSort(0)

        # clear existing / default 2d display regions
        self.dr2d = self.cam2d.node().getDisplayRegion(0)
        self.dr2d.setActive(False)
        self.dr2d.setSort(0)
        # ------------------------------------------- #

        self.main_win = self.scene_win.get_window()

        # ------------------ 2d rendering setup ------------------
        # create new 2d display region
        self.edDr2d = self.win.makeDisplayRegion(0, 1, 0, 1)
        self.edDr2d.setSort(1)
        self.edDr2d.setActive(True)

        # create a 2d mouse watcher
        self.ed_mouse_watcher_node_2d = p3d_core.MouseWatcher()
        self.mouseWatcher.get_parent().attachNewNode(self.ed_mouse_watcher_node_2d)
        self.ed_mouse_watcher_node_2d.set_display_region(self.edDr2d)

        # create a new 2d scene graph
        self.edRender2d = NodePath('EdRender2d')
        self.edRender2d.setDepthTest(False)
        self.edRender2d.setDepthWrite(False)

        # create a 2d camera
        self.ed_camera_2d = NodePath(Camera('EdCamera2d'))
        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1000, 1000)
        self.ed_camera_2d.node().setLens(lens)

        self.ed_camera_2d.reparentTo(self.edRender2d)
        self.edDr2d.setCamera(self.ed_camera_2d)

        # create an aspect corrected 2d scene graph
        self.__ed_aspect2d = self.edRender2d.attachNewNode(PGTop('EdAspect2d'))
        self.__ed_aspect2d.node().setMouseWatcher(self.ed_mouse_watcher_node_2d)

        # ------------------ 3d rendering setup ------------------ #
        # create editor root node behind render node, so we can keep editor only
        # nodes out of the scene
        self.edRender = NodePath('EdRender')
        self.render.reparentTo(self.edRender)

        # setup editor mouse watcher 3d
        # button_throwers, pointer_watcher_nodes = self.setupMouseCB(self.main_win)
        # self.ed_mouse_watcher = button_throwers[0].getParent()
        self.ed_mouse_watcher_node = p3d_core.MouseWatcher()
        self.mouseWatcher.get_parent().attachNewNode(self.ed_mouse_watcher_node)

        # create new 3d display region
        self.edDr = self.main_win.makeDisplayRegion(0, 1, 0, 1)
        self.edDr.setSort(0)
        self.edDr.setClearColorActive(True)
        self.edDr.setClearColor((0.6, 0.6, 0.6, 1.0))

        self.ed_mouse_watcher_node.set_display_region(self.edDr)

        self.ed_camera = EditorCamera(
            win=self.main_win,
            mouse_watcher_node=self.ed_mouse_watcher_node,
            render=self.edRender,
            render2d=self.__ed_aspect2d,
            default_pos=(300, 150 + 300, 100 + 300),
        )
        self.ed_camera.reparentTo(self.edRender)
        self.ed_camera.node().setCameraMask(constants.ED_GEO_MASK)
        self.ed_camera.start()

        self.edDr.setCamera(self.ed_camera)

    def clear_ed_aspect_2d(self):
        for np in self.aspect2d.getChildren():
            if np.get_name() == "CameraAxes":
                continue
            else:
                np.remove_node()

    def update_aspect_ratio(self):
        aspect_ratio = self.getAspectRatio(self.main_win)

        # maintain aspect ratio pixel2d
        if self.__ed_aspect2d is not None:
            self.__ed_aspect2d.setScale(1.0 / aspect_ratio, 1.0, 1.0)

        if self.ed_camera is not None:
            self.ed_camera.node().getLens().setAspectRatio(aspect_ratio)
            self.ed_camera.update_axes()

    def windowEvent(self, *args, **kwargs):
        """ Overridden to fix the aspect ratio of the editor camera and
        editor pixel2d."""
        super(ShowBase, self).windowEvent(*args, **kwargs)
        self.update_aspect_ratio()
        if editor.observer:
            editor.observer.trigger("ShowBaseResize")

    @property
    def ed_aspect2d(self):
        return self.__ed_aspect2d
