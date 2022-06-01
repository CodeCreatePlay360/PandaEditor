import panda3d.core as p3dCore
from editor.core.runtimeModule import RuntimeModule
from editor.utils import EdProperty


class Basics(RuntimeModule):
    def __init__(self, *args, **kwargs):
        """__init__ should not be used for anything but variable declaration"""

        RuntimeModule.__init__(self, *args, **kwargs)

        # --------------------------------------------------------------------
        # create some properties that will be displayed in inspector
        # properties of these types are laid out automatically by the editor
        self.int_property = 5
        self.float_property = 7.5
        self.str_property = "Panda3d"
        self.bool_property = False
        self.vector3 = p3dCore.Vec3(10, 17, 28)
        self.vector2 = p3dCore.Vec3(25, 46)
        # --------------------------------------------------------------------

        # --------------------------------------------------------------------
        # Custom properties
        self.add_property(EdProperty.EmptySpace(0, 10))  # add some empty space
        self.add_property(EdProperty.Label(name="Custom Properties", is_bold=True))  # label property
        self.add_property(EdProperty.ButtonProperty("Button", self.on_button))  # button property

        # a slider property
        self.temperature = 5  # private to hide in inspector
        self.add_property(EdProperty.Slider("Temperature",
                                            value=self.temperature,  # initial value
                                            min_value=0,
                                            max_value=10,
                                            setter=self.set_temperature,
                                            getter=self.get_temperature
                                            ))

        # a choice property
        self.curr_choice = 0
        self.add_property(EdProperty.ChoiceProperty("Apple",
                                                    choices=["Apple", "PineApple", "BigApple", "Blueberry"],
                                                    value=self.curr_choice,  # initial value
                                                    setter=self.set_choice,
                                                    getter=self.get_choice))
        # --------------------------------------------------------------------

        win = self._win                                # the window we are rendering into currently
        mouse_watcher_node = self._mouse_watcher_node  # mouse watcher node
        render = self._render                          # this is the current scene's parent node-path
        self.game = self._game                         # instance of current running game
        self.np = self._render.find("**/cube.fbx")
        self.camera_np = self._render.find("**/Camera")

    def on_start(self):
        """on_start method is called only once"""
        test_module = self._game.get_module("TestModule")  # get a reference to other modules or editor plugins
        if test_module is not None:
            test_module.foo()

        self.accept("q", self.bar, [])

    def foo(self):
        return self.bar

    def on_update(self):
        """update method is called every frame"""
        pass

    def on_late_update(self):
        """on late update is called after update"""
        pass

    def bar(self, *args):
        print("[Basics.py] event Q")

    def on_button(self):
        print("button pressed")

    def set_temperature(self, val):
        self.temperature = val

    def get_temperature(self):
        return self.temperature

    def set_choice(self, val):
        self.curr_choice = val

    def get_choice(self):
        return self.curr_choice
