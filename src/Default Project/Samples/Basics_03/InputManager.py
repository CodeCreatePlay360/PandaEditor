from panda3d.core import Vec2
from editor.core.runtimeModule import RuntimeModule


class InputManager(RuntimeModule):
    def __init__(self, *args, **kwargs):
        RuntimeModule.__init__(self, *args, **kwargs)
        self._sort = 3
                
        # keyboard events
        self.key_map = {}

        # list of all the key events to bind
        # extend this list to fit your project
        # do not create key-up events they are automatically created
        self.keys = ["w", "a", "s", "d", "q", "e", "r", "arrow_up", "arrow_left", "arrow_right", "escape", "mouse1"]
        self.add_discarded_attr("keys")

        self.__dx = 0
        self.__dy = 0
        self.__lastMousePos = Vec2(0, 0)
        self.mouseInput = Vec2(0, 0)
        self.zoom = 0
        self.autoCenterMouse = False

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
        if not self._mouse_watcher_node.hasMouse():
            self.mouseInput = Vec2(0, 0)
            return

        self.get_mouse_input()

        if self.autoCenterMouse:
            self._win.movePointer(0,
                                  int(self._win.getProperties().getXSize() / 2),
                                  int(self._win.getProperties().getYSize() / 2))

        # particularly for mouse wheels,
        if self.key_map["wheel_up"] > 0:
            self.zoom = 1
        elif self.key_map["wheel_down"] < 0:
            self.zoom = -1
        else:
            self.zoom = 0
            
        if self.key_map["escape"] > 0:
            self.autoCenterMouse = False
        elif self.key_map["mouse1"] > 0:
            self.autoCenterMouse = True
 
    def on_late_update(self):
        for key in self.key_map.keys():
            # exclude 
            if key not in self.keys or "-" in key:  
                self.key_map[key] = 0
        
    def on_stop(self):
        # TODO remove this, automatically called
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
        mouse_x = self._mouse_watcher_node.getMouseX()
        mouse_y = self._mouse_watcher_node.getMouseY()

        if self.autoCenterMouse:
            self.__dx = mouse_x - self.__lastMousePos.x
            self.__dy = mouse_y - self.__lastMousePos.y

            if abs(self.__dx) > 0:
                self.mouseInput.x = mouse_x
            else:
                self.mouseInput.x = 0
                
            if abs(self.__dy) > 0:
                self.mouseInput.y = mouse_y
            else:
                self.mouseInput.y = 0

            self.__lastMousePos.x = mouse_x
            self.__lastMousePos.y = mouse_y

            return

        else:  # calculate displacement based to previous pos
            self.__dx = mouse_x - self.__lastMousePos.x
            self.__dy = mouse_y - self.__lastMousePos.y
            
        # set last pos to current pos
        self.__lastMousePos.x = mouse_x
        self.__lastMousePos.y = mouse_y

        if self.__dx > 0:
            self.mouseInput.x = 1
        
        if self.__dx < 0:
            self.mouseInput.x = -1
            
        if self.__dy > 0:
            self.mouseInput.y = 1
        
        if self.__dy < 0:
            self.mouseInput.y = -1
