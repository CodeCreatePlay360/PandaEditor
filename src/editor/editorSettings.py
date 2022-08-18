from editor.utils import EdProperty


class EditorSettings:
    def __init__(self, level_editor, *args):
        self.level_editor = level_editor
        self.properties = []

        # editor grid settings
        self.grid_size = 200
        self.gridStep = 40
        self.sub_divisions = 5

        self.hidden_attrs = "grid_size"
        self.hidden_attrs = "gridStep"
        self.hidden_attrs = "sub_divisions"

        self.properties.append(EdProperty.Label(name="GridSettings", is_bold=True))
        self.properties.append(EdProperty.ObjProperty(name="grid_size", value=self.grid_size, _type=float, obj=self))
        self.properties.append(EdProperty.ObjProperty(name="gridStep", value=self.gridStep, _type=float, obj=self))
        self.properties.append(EdProperty.ObjProperty(name="sub_divisions", value=self.sub_divisions, _type=float, obj=self))
        self.properties.append(EdProperty.ButtonProperty("SetGrid", self.set_grid))

    def set_grid(self):
        self.level_editor.create_grid(self.grid_size, self.gridStep, self.sub_divisions)

    def get_properties(self):
        return self.properties

    def has_ed_property(self, prop_name):
        for prop in self.properties:
            if prop.name == prop_name:
                return True
        return False
