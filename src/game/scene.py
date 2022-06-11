import panda3d.core as p3d_core


class Scene:
    """Scene class represents a game scene"""
    def __init__(self, game, name, *args, **kwargs):
        self.game = game
        self.name = name
        self.active_camera = None  # this is 3d rendering camera

        # create a 3d rendering setup
        self.render = p3d_core.NodePath(self.name)
        self.render.reparent_to(self.game.render)
        # -----------------------------------------

        # create a 2d rendering setup
        self.render_2d = None
        self.camera_2d = None
        # -----------------------------------------

        self.scene_lights = []   # all scene lights in one repository
        self.scene_cameras = []  # all scene camera in one repository

    def setup_render(self):
        """setup a 3d rendering"""
        pass

    def setup_2d_render(self):
        """setup a 2d rendering"""

        # create a 2d scene graph
        self.render_2d = p3d_core.NodePath("Render2d")
        self.render_2d.setDepthTest(False)
        self.render_2d.setDepthWrite(False)

        # create a 2d-camera
        self.camera_2d = p3d_core.NodePath(p3d_core.Camera("Camera2d"))
        lens = p3d_core.OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setNearFar(-1000, 1000)
        self.camera_2d.node().setLens(lens)

        self.game.display_region_2d.setCamera(self.camera_2d)
