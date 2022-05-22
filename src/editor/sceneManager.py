from game.scene import Scene


class SceneManager:
    def __init__(self, le, *args, **kwargs):
        self.level_ed = le
        self.scenes = []  # list of the scenes in this project
        self.active_scene = None

    def parse_active_scene(self):
        pass

    def load_scene(self, scene):
        pass
