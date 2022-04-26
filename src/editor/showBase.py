from direct.showbase import ShowBase as SB
from panda3d.core import NodePath, Camera, OrthographicLens, PGTop
from editor.constants import ED_GEO_MASK, GAME_GEO_MASK
from editor.core import EditorCamera


class ShowBase(SB.ShowBase):
    def __init__(self, ed_wx_win):
        SB.ShowBase.__init__(self)

        self.ed_wx_win = ed_wx_win  # wx python window
        self.main_win = None  # Panda3d editor window we will render into

        self.edRender = None
        self.edRender2d = None
        self.ed_camera = None
        self.ed_camera_2d = None

        self.player_camera = None

        self.dr = None  # default 3d display region
        self.dr2d = None  # default 2d display region
        self.edDr = None  # editor 3d display region that will replace default 3d display region
        self.edDr2d = None  # editor 2d display region that will replace default 2d display region
        self.ed_pixel_2d = None
        self.game_dr = None

        self.ed_mouse_watcher = None  # editor mouse watcher for editor display region
        self.ed_mouse_watcher_node = None

        self.forcedAspectWins = []
        self.update_task = None

    def finish_init(self):
        self.init_editor_win()
        self.setup_editor_window()

        # Add the editor window, camera and pixel 2d to the list of forced
        # aspect windows so aspect is fixed when the window is resized.
        self.forcedAspectWins.append((self.main_win, self.ed_camera, self.ed_pixel_2d))

        # turn on per pixel lightning
        self.edRender.setShaderAuto()

    def init_editor_win(self):
        self.ed_wx_win.Initialize(useMainWin=True)

    def setup_editor_window(self):
        """set up an editor rendering, it included setting up 2d and 3d display regions,
        an editor scene graph and editor mouse watchers"""

        # clear existing / default 3d display regions
        self.dr = self.cam.node().getDisplayRegion(0)
        self.dr.setClearColorActive(True)
        self.dr.setClearColor(self.getBackgroundColor())
        self.dr.setActive(False)
        self.dr.setSort(20)

        # clear existing / default 2d display regions
        self.dr2d = self.cam2d.node().getDisplayRegion(0)
        self.dr2d.setActive(False)
        self.dr2d.setSort(21)

        # Setup mouse watcher for the editor window
        self.main_win = self.ed_wx_win.GetWindow()
        button_throwers, pointer_watcher_nodes = self.setupMouseCB(self.main_win)
        self.ed_mouse_watcher = button_throwers[0].getParent()
        self.ed_mouse_watcher_node = self.ed_mouse_watcher.node()
        ed_mouse_watcher_parent = self.ed_mouse_watcher.getParent()

        # ------------------ 2d rendering setup ------------------ #
        # create new 2d display region
        self.edDr2d = self.win.makeDisplayRegion()
        self.edDr2d.setSort(20)
        self.edDr2d.setActive(True)

        # create a new 2d scene graph
        self.edRender2d = NodePath('EdRender2d')
        self.edRender2d.setDepthTest(False)
        self.edRender2d.setDepthWrite(False)

        # create a 2d camera for 2d display region
        self.ed_camera_2d = NodePath(Camera('EdCamera2d'))
        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1000, 1000)
        self.ed_camera_2d.node().setLens(lens)
        self.edDr2d.setCamera(self.ed_camera_2d)

        # create an aspect corrected 2d scene graph
        self.ed_pixel_2d = self.edRender2d.attachNewNode(PGTop('EdPixel2d'))
        self.ed_pixel_2d.node().setMouseWatcher(self.mouseWatcherNode)
        self.ed_pixel_2d.set_pos(0, 0, 0)
        self.ed_camera_2d.reparentTo(self.edRender2d)

        # ------------------ 3d rendering setup ------------------ #
        # create editor root node behind render node, so we can keep editor only
        # nodes out of the scene
        self.edRender = NodePath('EdRender')
        self.render.reparentTo(self.edRender)

        # create new 3d display region
        self.edDr = self.main_win.makeDisplayRegion(0, 1, 0, 1)
        self.edDr.setClearColorActive(True)
        self.edDr.setClearColor((0.6, 0.6, 0.6, 1.0))

        self.ed_camera = EditorCamera(
            mouse_watcher_node=self.ed_mouse_watcher_node,
            render2d=self.ed_pixel_2d,
            win=self.main_win,
            default_pos=(300, 150 + 300, 100 + 300),
        )
        self.ed_camera.reparentTo(self.edRender)
        self.ed_camera.start()
        self.set_ed_dr_camera(self.ed_camera)

        # create a game display region
        self.game_dr = self.main_win.makeDisplayRegion(0, 0.4, 0, 0.4)
        self.game_dr.setClearColorActive(True)
        self.game_dr.setClearColor((0.8, 0.8, 0.8, 1.0))

    def set_ed_dr_camera(self, cam):
        """set scene display region's camera"""
        self.edDr.setCamera(cam)
        cam.node().setCameraMask(ED_GEO_MASK)

    def set_player_camera(self, cam):
        self.player_camera = cam
        self.game_dr.setCamera(cam)
        cam.node().setCameraMask(GAME_GEO_MASK)

    def on_enable_game(self):
        self.edDr.setActive(False)
        self.game_dr.set_dimensions((0, 1, 0, 1))

    def on_enable_editor(self):
        self.edDr.setActive(True)
        self.game_dr.set_dimensions((0, 0.4, 0, 0.4))

    def update_aspect_ratio(self):
        aspect_ratio = self.getAspectRatio(self.main_win)

        if self.ed_camera is not None:
            self.ed_camera.node().getLens().setAspectRatio(aspect_ratio)
            self.ed_camera.update_axes()

        if self.player_camera is not None:
            self.player_camera.node().getLens().setAspectRatio(aspect_ratio)

        # maintain aspect ratio pixel2d
        if self.ed_pixel_2d is not None:
            self.ed_pixel_2d.set_pos(0, 0, 0)
            self.ed_pixel_2d.setScale(1 / aspect_ratio, 1.0, 1.0)

    def windowEvent(self, *args, **kwargs):
        """ Overridden to fix the aspect ratio of the editor camera and
        editor pixel2d."""
        super(ShowBase, self).windowEvent(*args, **kwargs)
        self.update_aspect_ratio()
