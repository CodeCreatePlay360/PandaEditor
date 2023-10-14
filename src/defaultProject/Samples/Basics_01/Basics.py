import panda3d.core as p3dCore
import direct.gui.DirectGui as gui

from pathlib import Path
from direct.showbase.Loader import Loader
from commons import EditorProperty
from game.resources import RuntimeModule


class Basics(RuntimeModule):
    def __init__(self, *args, **kwargs):
        RuntimeModule.__init__(self, *args, **kwargs)

        # __init__ should not contain anything except for variable declaration
        # by default all public attributes will be displayed in inspector and saved during editor reload.
        self.add_property(EditorProperty.Label(name="Default Properties", is_bold=True, draw_idx=-1))

        self.int_property = 5
        self.float_property = 7.5
        self.str_property = "Panda3d"
        self.bool_property = True
        self.vector3 = p3dCore.LVecBase3f(10, 17, 28)
        self.vector2 = p3dCore.LVecBase2f(25, 46)

        # private attributes by default are hidden in inspector, however
        # they are saved/reloaded during editor reload.
        self.__color = p3dCore.LColor(1, 1, 1, 1)
        self.__curr_choice = 0
        self.__temperature = 5

        # ** -------------------------------------------------------------------- **
        # CUSTOM PROPERTIES

        # empty space property
        self.add_property(EditorProperty.EmptySpace(0, 5))

        # label property
        self.add_property(EditorProperty.Label(name="Custom Properties", is_bold=True))

        # button property
        self.add_property(EditorProperty.ButtonProperty(name="Button Property", method=self.on_button))

        # slider property
        self.add_property(EditorProperty.Slider(name="Slider",
                                                initial_value=self.__temperature,  # initial value
                                                min_value=0,
                                                max_value=10,
                                                setter=self.set_temperature,
                                                getter=lambda: self.__temperature))

        # choice property
        choices = ["Apple", "PineApple", "BigApple", "Blueberry"]
        self.add_property(EditorProperty.ChoiceProperty(name="Choice",
                                                        choices=choices,
                                                        initial_value=self.__curr_choice,  # initial value
                                                        setter=self.set_choice,
                                                        getter=lambda: self.__curr_choice))

        # color property
        self.add_property(EditorProperty.FuncProperty(name="Color_picker",
                                                      initial_value=self.__color,
                                                      setter=self.set_color,
                                                      getter=lambda: self.__color))

        # --------------------------------
        # horizontal layout group property
        self.toggle = True
        properties = [EditorProperty.Label(name="HorizontalGroup: ", is_bold=True),
                      EditorProperty.ObjProperty(name="vector2", initial_value=self.vector2, obj=self),
                      EditorProperty.ObjProperty(name="toggle", initial_value=self.toggle, obj=self)]

        horizontal_layout_group = EditorProperty.HorizontalLayoutGroup(name="HLayoutGroup", properties=properties)
        self.add_property(horizontal_layout_group)

        # -------------------------------
        properties = [EditorProperty.Label(name="StaticBox: ", is_bold=True),
                      EditorProperty.ObjProperty(name="vector2", initial_value=self.vector2, obj=self),
                      EditorProperty.ObjProperty(name="toggle", initial_value=self.toggle, obj=self)]

        # a static box container to group together logically similar attributes
        static_box = EditorProperty.StaticBox(name="Properties-Group", properties=properties)
        self.add_property(static_box)

        # --------------------------------------
        # vertical layout group or foldout group
        self.__integer = 45
        self.__boolean = False
        self.__vector = p3dCore.LVecBase3f(5, 10, 15)

        properties = [EditorProperty.ObjProperty(name="_Basics__integer", initial_value=self.__integer, obj=self),
                      EditorProperty.ObjProperty(name="_Basics__boolean", initial_value=self.__boolean, obj=self),
                      EditorProperty.ObjProperty(name="_Basics__vector", initial_value=self.__vector, obj=self)]

        foldout_group = EditorProperty.FoldoutGroup(properties=properties)
        self.add_property(foldout_group)

        # CUSTOMIZATION ----------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------------------
        # to stop public attributes from displaying in inspector add them to list of hidden attributes
        self.hidden_attrs = "toggle"
        self.hidden_attrs = "temperature"

        # ------------------------------------------------------------------------------------------------
        # to stop attributes from being saved during editor reload, add them to list of
        # discarded attributes
        self.non_serialized_attrs = "toggle"

    def on_start(self):
        # this method is called only once

        # attributes defined in RuntimeModule base class, they act as bridge between PandaEditor and Panda3d engine
        # self.show_base           : a reference to show_base
        # self.win                 : the rendering window
        # self.mouse_watcher_node  : mouse watcher node
        # self.render              : this is the current scene's parent node-path
        # self.game                : instance of current running game
        loader = Loader(self.show_base)

        # ---------------------------
        # basic scene graph operations
        np = self.render.find("**/cube.fbx")
        camera_np = self.render.find("**/Camera")

        # ------------------------------------------------------------
        # get reference to other runtime modules or NodePath components
        test_module = self.game.get_module(self.game.path + str(Path("/Samples/Basics_01/TestModule.py")))
        if test_module is not None:
            test_module.foo()  # foo is a method defined TestModule

        # ---------------------------
        # creating direct gui elements
        button = gui.DirectButton(text=("OK", "click!", "rolling over", "disabled"),
                                  scale=.2,
                                  command=self.on_direct_gui_btn_press)
        button.setPos((0, 0, 0))
        button.reparent_to(self.aspect2d)

        # --------------------
        # basic event handling
        self.accept("a", self.on_key_down, ["a"])
        self.accept("a-up", self.on_key_up, ["a"])

        # house = self.render.find("**/RussianHouse2.gltf")
        # obj = house.find("**/defaultMaterial")
        #
        # mat = p3dCore.Material("SomeMat")
        # obj.setMaterial(mat, 1)
        # path = str(pathlib.Path("/Samples/RPG Character/brick-c.jpg"))
        # obj.setTexture(self.__loader.load_texture(path), 1)
        # obj.ls()
        # print(obj.get_material())

    def on_update(self):
        # this method is called every frame
        pass

    def on_late_update(self):
        # this method is called after update
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
        self.__temperature = val

    def set_choice(self, val):
        print(val)
        self.__curr_choice = val

    def set_color(self, val):
        self.__color = val
