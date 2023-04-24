from panda3d.core import LVecBase2f
from editor.core import RuntimeModule


class InputManager(RuntimeModule):
    def __init__(self, *args, **kwargs):
        RuntimeModule.__init__(self, *args, **kwargs)
        self._sort = 3

        # keyboard events
        self.key_map = {}

        # list of all the key events to bind
        # extend this list to fit your project
        # do not create key-up events they are automatically created
        alphabets = ["q", "w", "e", "r", "t", "y", "u", "i", "o",
                     "a", "s", "d", "f", "g", "h", "j", "k", "l",
                     "z", "x", "c", "v", "b", "n", "m"]
        arrow_keys = ["arrow_down", "arrow_up", "arrow_left", "arrow_right"]
        other_keys = ["escape", "mouse1"]

        self.keys = []
        self.keys.extend(alphabets)
        self.keys.extend(arrow_keys)
        self.keys.extend(other_keys)

        self.__dx = 0
        self.__dy = 0
        self.__last_mouse_pos = LVecBase2f(0, 0)
        self.__mouse_input = LVecBase2f(0, 0)
        self.__zoom = 0
        self.center_mouse = False

        self.discarded_attrs = "keys"
        self.discarded_attrs = "_InputManager__dx"
        self.discarded_attrs = "_InputManager__dy"
        self.discarded_attrs = "_InputManager__lastMousePos"

    def register_key(self, key: str):
        if not isinstance(key, str):
            print("[InputManager] key must be of type string")
            return

        if not self.keys.__contains__(key):
            pass  # register key

    def on_start(self):
        # self._le.app.set_mouse_mode("Relative")
        self.key_map.clear()

        for key in self.keys:
            self.accept(key, self.on_key_event, [key, 1])

            # also create an up key event
            key_up_evt = key + "-up"
            self.accept(key_up_evt, self.on_key_event, [key_up_evt, 1, True])

            # and append both keys
            self.key_map[key] = 0
            self.key_map[key_up_evt] = 0

        self.accept("wheel_up", self.on_key_event, ["wheel_up", 1])
        self.accept("wheel_down", self.on_key_event, ["wheel_down", -1])

        self.key_map["wheel_up"] = 0
        self.key_map["wheel_down"] = 0

    def on_update(self):
        if not self.mouse_watcher_node.hasMouse():
            self.__mouse_input = LVecBase2f(0, 0)
            return

        self.get_mouse_input()

        if self.center_mouse:
            self.win.movePointer(0,
                                 int(self.win.getProperties().getXSize() / 2),
                                 int(self.win.getProperties().getYSize() / 2))

        # particularly for mouse wheels,
        if self.key_map["wheel_up"] > 0:
            self.__zoom = 1
        elif self.key_map["wheel_down"] < 0:
            self.__zoom = -1
        else:
            self.__zoom = 0

        if self.key_map["escape"] > 0:
            self.center_mouse = False
        elif self.key_map["mouse1"] > 0 and self.center_mouse:
            self.center_mouse = True

    def on_late_update(self):
        for key in self.key_map.keys():
            # exclude 
            if key not in self.keys or "-" in key:
                self.key_map[key] = 0

    def on_stop(self):
        # TODO should be done automatically on game.stop
        for key in self.key_map.keys():
            self.ignore(key)

    def on_key(self, key, value):
        pass

    def on_key_event(self, key, value, is_evt_key_up=False):
        self.key_map[key] = value
        if is_evt_key_up:
            key = key.split("-")[0]
            self.key_map[key] = 0

    def get_mouse_input(self):
        mouse_x = self.mouse_watcher_node.getMouseX()
        mouse_y = self.mouse_watcher_node.getMouseY()

        if self.center_mouse:
            self.__dx = mouse_x - self.__last_mouse_pos.x
            self.__dy = mouse_y - self.__last_mouse_pos.y

            if abs(self.__dx) > 0:
                self.__mouse_input.x = mouse_x
            else:
                self.__mouse_input.x = 0

            if abs(self.__dy) > 0:
                self.__mouse_input.y = mouse_y
            else:
                self.__mouse_input.y = 0

            self.__last_mouse_pos.x = mouse_x
            self.__last_mouse_pos.y = mouse_y

            return

        else:  # calculate displacement based to previous pos
            self.__dx = mouse_x - self.__last_mouse_pos.x
            self.__dy = mouse_y - self.__last_mouse_pos.y

        # set last pos to current pos
        self.__last_mouse_pos.x = mouse_x
        self.__last_mouse_pos.y = mouse_y

        if self.__dx > 0:
            self.__mouse_input.x = 1
        elif self.__dx < 0:
            self.__mouse_input.x = -1
        else:
            self.__mouse_input.x = 0

        if self.__dy > 0:
            self.__mouse_input.y = 1
        elif self.__dy < 0:
            self.__mouse_input.y = -1
        else:
            self.__mouse_input.y = 0

    @property
    def mouse_input(self):
        return self.__mouse_input

    @property
    def zoom(self):
        return self.__zoom
