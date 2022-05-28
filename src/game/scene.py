import panda3d.core as p3d_core


class Scene:
    """Scene class represents a game scene"""
    def __init__(self, game, name, *args, **kwargs):
        self.game = game
        self.name = name
        self.active_camera = None
        self.lights = []

        # create a scene render and re-parent it to game_render
        self.render = p3d_core.NodePath(self.name)
        self.render.reparent_to(self.game.render)

        self.aspect2d = self.game.aspect2d

        self.scene_lights = []   # all scene lights in one repository
        self.scene_cameras = []  # all scene camera in one repository
