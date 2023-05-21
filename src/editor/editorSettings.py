from editor.utils import EdProperty
from panda3d.core import LColor


class EditorSettings:
    def __init__(self, level_editor, *args):
        self.level_editor = level_editor
        self.properties = []

        # editor grid settings
        self.show_grid = True
        self.grid_size = 200
        self.gridStep = 40
        self.sub_divisions = 5

        # resources settings
        self.auto_reload = False

        # scene background / viewport settings
        self.bg_color = LColor(0.5, 0.5, 0.5, 1.0)

        # hidden
        self.hidden_attrs = "grid_size"
        self.hidden_attrs = "gridStep"
        self.hidden_attrs = "sub_divisions"
        self.hidden_attrs = "bg_color"

        # ----------------------------------------------------------------------------------------------------
        grid_settings = [EdProperty.FuncProperty("show", self.show_grid, self.toggle_grid_visible,
                                                 lambda: self.show_grid),
                         EdProperty.ObjProperty(name="grid_size", value=self.grid_size, obj=self),
                         EdProperty.ObjProperty(name="gridStep", value=self.gridStep, obj=self),
                         EdProperty.ObjProperty(name="sub_divisions", value=self.sub_divisions, obj=self),
                         EdProperty.ButtonProperty("Update Grid", self.set_grid)]

        static_box_1 = EdProperty.StaticBox(name="Grid Settings", properties=grid_settings)
        self.properties.append(static_box_1)

        # ----------------------------------------------------------------------------------------------------
        editor_settings = [EdProperty.ObjProperty("auto_reload", self.auto_reload, self)]

        static_box_2 = EdProperty.StaticBox(name="Editor Settings", properties=editor_settings)
        self.properties.append(EdProperty.EmptySpace(0, 5))
        self.properties.append(static_box_2)

        # ----------------------------------------------------------------------------------------------------
        camera_settings = []
        for prop in EdProperty.Utils.get_lens_properties(
                self.level_editor.app.show_base.ed_camera.node().get_lens()):
            camera_settings.append(prop)

        static_box_3 = EdProperty.StaticBox(name="Camera Settings", properties=camera_settings)
        self.properties.append(EdProperty.EmptySpace(0, 5))
        self.properties.append(static_box_3)

        # ----------------------------------------------------------------------------------------------------
        viewport_settings = [EdProperty.FuncProperty(name="SceneBackgroundColor", value=self.bg_color,
                                                     setter=self.set_bg_color, getter=lambda: self.bg_color)]

        static_box_4 = EdProperty.StaticBox(name="Viewport Settings", properties=viewport_settings)
        self.properties.append(EdProperty.EmptySpace(0, 5))
        self.properties.append(static_box_4)

    def toggle_grid_visible(self, val):
        self.show_grid = not self.show_grid
        if self.show_grid:
            self.level_editor.grid_np.show()
        else:
            self.level_editor.grid_np.hide()

    def set_grid(self):
        self.level_editor.create_grid(self.grid_size, self.gridStep, self.sub_divisions)

    def set_bg_color(self, val):
        pass

    def get_properties(self):
        return self.properties

    def has_ed_property(self, prop_name):
        for prop in self.properties:
            if prop.name == prop_name:
                return True
        return False
