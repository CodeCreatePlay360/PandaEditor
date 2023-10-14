from commons import EditorProperty
from panda3d.core import LColor
from editor.globals import editor


class EditorSettings:
    def __init__(self):
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

        self.properties.append(EditorProperty.EmptySpace(0, 1))

        # ----------------------------------------------------------------------------------------------------
        grid_settings = [
            EditorProperty.Label(name="Viewport Grid", is_bold=True),
            EditorProperty.FuncProperty("show", self.show_grid, self.toggle_grid_visible, lambda: self.show_grid),
            EditorProperty.ObjProperty(name="grid_size", initial_value=self.grid_size, obj=self),
            EditorProperty.ObjProperty(name="gridStep", initial_value=self.gridStep, obj=self),
            EditorProperty.ObjProperty(name="sub_divisions", initial_value=self.sub_divisions, obj=self),
            EditorProperty.ButtonProperty("Update Grid", self.set_grid)]

        static_box_1 = EditorProperty.StaticBox(name="Grid Settings", properties=grid_settings)
        self.properties.append(static_box_1)

        # ----------------------------------------------------------------------------------------------------
        editor_settings = [
            EditorProperty.Label(name="Editor", is_bold=True),
            EditorProperty.ObjProperty("auto_reload", self.auto_reload, self)]

        static_box_2 = EditorProperty.StaticBox(name="Editor Settings", properties=editor_settings)
        self.properties.append(EditorProperty.EmptySpace(0, 5))
        self.properties.append(static_box_2)

        # ----------------------------------------------------------------------------------------------------
        camera_settings = [EditorProperty.Label(name="Viewport Cam", is_bold=True)]
        for prop in EditorProperty.Utils.get_properties_for_lens(
                editor.p3D_app.editor_workspace.ed_camera.node().get_lens()):
            camera_settings.append(prop)

        static_box_3 = EditorProperty.StaticBox(name="Camera Settings", properties=camera_settings)
        self.properties.append(EditorProperty.EmptySpace(0, 5))
        self.properties.append(static_box_3)
        self.properties.append(EditorProperty.EmptySpace(0, 5))

    def toggle_grid_visible(self, val):
        self.show_grid = not self.show_grid
        if self.show_grid:
            editor.level_editor.grid_np.show()
        else:
            editor.level_editor.grid_np.hide()

    def set_grid(self):
        editor.level_editor.create_grid(self.grid_size, self.gridStep, self.sub_divisions)

    def set_bg_color(self, val):
        pass

    def get_properties(self):
        return self.properties

    def has_ed_property(self, prop_name):
        for prop in self.properties:
            if prop.name == prop_name:
                return True
        return False
