import panda3d.core as p3d_core


class Scene:
    """Scene class represents a game scene"""
    def __init__(self, game, name, *args, **kwargs):
        self.__game = game
        self.__name = name
        self.__main_camera = None  # this is main rendering camera

        # create a 3d rendering setup
        self.__render = p3d_core.NodePath(self.__name)
        self.__render.reparent_to(self.__game.render)

        # -----------------------------------------
        # create a 2d rendering setup
        self.__render_2D = None
        self.__aspect_2d = None
        self.__camera_2D = None

        self.setup_2d_render()

        # -----------------------------------------
        self.__scene_lights = []   # all scene lights in one repository
        self.__scene_cameras = []    # all scene camera in one repository

    def setup_2d_render(self):
        """setup a 2d rendering"""

        # create a 2d scene graph
        self.__render_2D = p3d_core.NodePath("Render2d")
        self.__render_2D.setDepthTest(False)
        self.__render_2D.setDepthWrite(False)

        self.__aspect_2d = self.__render_2D.attachNewNode(p3d_core.PGTop("__aspect_2d__"))
        self.__aspect_2d.set_scale(1.0 / self.__game.show_base.getAspectRatio(self.__game.win), 1.0, 1.0)
        self.__aspect_2d.node().set_mouse_watcher(self.__game.mouse_watcher_node_2d)

        # create a 2d-camera
        self.__camera_2D = p3d_core.NodePath(p3d_core.Camera("__camera2D__"))
        lens = p3d_core.OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1000, 1000)
        self.__camera_2D.node().setLens(lens)
        self.__camera_2D.reparent_to(self.__render_2D)

        self.__game.dr_2d.setCamera(self.__camera_2D)

    def set_active_camera(self, cam):
        self.__main_camera = cam
        self.__game.set_active_cam(cam)

    def clear_cam(self, cam=None):
        if cam is None:
            cam = self.__main_camera

        if cam:
            self.__main_camera = None
            self.__game.clear_active_dr_3d()

    @property
    def main_camera(self):
        return self.__main_camera

    @property
    def camera_2D(self):
        return self.__camera_2D

    @property
    def render(self):
        return self.__render

    @property
    def render_2D(self):
        return self.__render_2D

    @property
    def aspect_2D(self):
        return self.__aspect_2d

    @property
    def scene_lights(self):
        def get_all_scene_lights(np):
            for np_ in np.getChildren():
                if np_.getPythonTag("__GAME_OBJECT__") and \
                        np_.getPythonTag("__GAME_OBJECT__").ed_id in \
                        ["__PointLight__", "__SpotLight__", "__DirectionalLight__", "__AmbientLight__"]:
                    lights.append(np_)

                get_all_scene_lights(np_)

        lights = []
        get_all_scene_lights(self.__render)
        self.__scene_lights = lights

        return self.__scene_lights

    @property
    def scene_cameras(self):
        def get_all_scene_cameras(np):
            for np_ in np.getChildren():
                obj = np_.getPythonTag("__GAME_OBJECT__")
                if obj.ed_id == "__CameraNodePath__":
                    cameras_.append(obj)

                get_all_scene_cameras(np_)

        cameras_ = []
        get_all_scene_cameras(self.__render)
        self.__scene_cameras = cameras_
        return self.__scene_cameras
