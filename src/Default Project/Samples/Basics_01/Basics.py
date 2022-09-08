import panda3d.core as p3dCore
import direct.gui.DirectGui as gui
from editor.core import RuntimeModule
from editor.utils import EdProperty


class Basics(RuntimeModule):
    def __init__(self, *args, **kwargs):
        """__init__ should not be used for anything except for variable declaration"""

        RuntimeModule.__init__(self, *args, **kwargs)

        # create some properties that will be displayed in inspector
        # properties of these types are laid out automatically by the editor
        self.int_property = 5
        self.float_property = 7.5
        self.str_property = "Panda3d"
        self.bool_property = False
        self.vector3 = p3dCore.LVecBase3f(10, 17, 28)
        self.vector2 = p3dCore.LVecBase2f(25, 46)

        # Custom properties --------------------------------------------------------------------
        # add some empty space
        self.add_property(EdProperty.EmptySpace(0, 55))

        # label property
        self.add_property(EdProperty.Label(name="Custom Properties", is_bold=True))

        # button property
        self.add_property(EdProperty.ButtonProperty("Button", self.on_button))

        # a slider property
        self.temperature = 5  # private to hide in inspector
        self.add_property(EdProperty.Slider("Slider",
                                            value=self.temperature,  # initial value
                                            min_value=0,
                                            max_value=10,
                                            setter=self.set_temperature,
                                            getter=self.get_temperature
                                            ))

        # a choice property
        self.curr_choice = 0
        self.hidden_attrs = "curr_choice"
        choices = ["Apple", "PineApple", "BigApple", "Blueberry"]
        self.add_property(EdProperty.ChoiceProperty("Choice",
                                                    choices=choices,
                                                    value=self.curr_choice,  # initial value
                                                    setter=self.set_choice,
                                                    getter=self.get_choice))

        self.bool_a = True
        properties = [EdProperty.ObjProperty("bool_a", self.bool_a, self)]
        horizontal_layout_group = EdProperty.HorizontalLayoutGroup(properties)
        self.add_property(horizontal_layout_group)

        self.bool_b = False
        properties = [EdProperty.ObjProperty("bool_b", self.bool_b, self),
                      EdProperty.ObjProperty("bool_b", self.bool_b, self),
                      EdProperty.ObjProperty("bool_b", self.bool_b, self),
                      EdProperty.ObjProperty("bool_b", self.bool_b, self),
                      EdProperty.ObjProperty("bool_b", self.bool_b, self),
                      EdProperty.ObjProperty("bool_b", self.bool_b, self),
                      EdProperty.ObjProperty("bool_b", self.bool_b, self),
                      EdProperty.ObjProperty("bool_b", self.bool_b, self),
                      EdProperty.ObjProperty("bool_b", self.bool_b, self),
                      ]
        foldout_group = EdProperty.FoldoutGroup(properties)
        self.add_property(foldout_group)

        self.bool_c = False
        properties = [EdProperty.ObjProperty("bool_b", self.bool_c, self),
                      EdProperty.ObjProperty("bool_b", self.bool_c, self),
                      EdProperty.ObjProperty("bool_b", self.bool_c, self),
                      EdProperty.ObjProperty("bool_b", self.bool_c, self),
                      EdProperty.ObjProperty("bool_b", self.bool_c, self),
                      EdProperty.ObjProperty("bool_b", self.bool_c, self),
                      EdProperty.ObjProperty("bool_b", self.bool_c, self),
                      EdProperty.ObjProperty("bool_b", self.bool_c, self),
                      EdProperty.ObjProperty("bool_b", self.bool_c, self),
                      ]
        foldout_group = EdProperty.FoldoutGroup(properties)
        self.add_property(foldout_group)

        # --------------------------------------------------------------------
        # attributes defined in Runtime module, they act as bridge between PandaEditor and Panda3d engine
        # self._win                : the window we are rendering into currently
        # self.mouse_watcher_node  : mouse watcher node
        # self.render              : this is the current scene's parent node-path
        # self.game                : instance of current running game

    def on_start(self):
        """on_start method is called only once"""

        # basic scene graph operations
        np = self.render.find("**/cube.fbx")
        camera_np = self.render.find("**/Camera")

        # get a reference to other runtime modules
        test_module = self.game.get_module("TestModule")
        if test_module is not None:
            # foo is a method defined TestModule
            test_module.foo()

        # creating direct gui elements
        self.create_ui()

        # basic event handling
        self.accept("a", self.on_key_down, ["a"])
        self.accept("a-up", self.on_key_up, ["a"])

    def create_ui(self):
        b = gui.DirectButton(text=("OK", "click!", "rolling over", "disabled"), scale=.2,
                             command=self.on_direct_gui_btn_press)
        b.setPos((0, 0, 0))
        b.reparent_to(self.aspect2d)

    def on_update(self):
        """update method is called every frame"""
        pass

    def on_late_update(self):
        """on late update is called after update"""
        pass

    def on_key_down(self, key: str):
        print("[Basics.py] event key down {0}".format(key))

    def on_key_up(self, key: str):
        print("[Basics.py] event key up {0}".format(key))

    def on_direct_gui_btn_press(self):
        print("[Basics.py] Direct gui button pressed.")

    def on_button(self):
        print("[Basics.py] EdProperty button pressed.")

    def set_temperature(self, val):
        self.temperature = val

    def get_temperature(self):
        return self.temperature

    def set_choice(self, val):
        self.curr_choice = val

    def get_choice(self):
        return self.curr_choice
