import wx
import editor.edPreferences as edPreferences
import editor.wxUI.wxCustomProperties as wxProperty
import editor.constants as constants
from wx.lib.scrolledpanel import ScrolledPanel
from panda3d.core import LVecBase2f, LPoint2f, LVecBase3f, LPoint3f, LColor
from editor.wxUI.wxFoldPanel import WxFoldPanelManager
from editor.utils import EdProperty as edProperty

Selection_btn_color_normal = wx.Colour(127, 127, 127, 255)
Selection_btn_color_pressed = wx.Colour(160, 160, 160, 255)

# icon paths
World_settings_icon = constants.ICONS_PATH + "//" + "globe.png"
Ed_settings_icon = constants.ICONS_PATH + "//" + "gear.png"
Object_settings_icon = constants.ICONS_PATH + "//" + "box_closed.png"
Plugin_icon = constants.ICONS_PATH + "//" + "plugin.png"


Object_Inspector = "ObjectInspector"
World = "World"
EditorSettings = "Editor"
Plugins = "Plugins"


class SelectionGrid(wx.Panel):
    def __init__(self, parent, on_select, *args, **kwargs):
        """on_select = the function to call when a button is selected"""

        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.SetMinSize((-1, 18))
        self.SetWindowStyleFlag(wx.BORDER_NONE)
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.parent = parent
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.buttons = []
        self.selected_btn_index = -1
        self.on_select_function = on_select

    def add_button(self, selection_btn, flags=wx.EXPAND, border=0):
        self.sizer.Add(selection_btn, 1, flags, border=border)
        self.sizer.Layout()
        self.buttons.append(selection_btn)

    def select_button(self, at_index, **kwargs):
        if at_index < len(self.buttons):
            self.deselect_all()
            self.buttons[at_index].on_click(**kwargs)
        else:
            print("[SelectionGrid] Unable to select button, invalid index {0}", at_index)

    def on_button_clicked(self, index, **kwargs):
        self.deselect_all()
        self.selected_btn_index = index
        self.on_select_function(index, **kwargs)

    def deselect_all(self):
        for btn in self.buttons:
            btn.deselect()
        self.selected_btn_index = -1


class SelectionButton(wx.Window):
    def __init__(self, parent, btn_index, image_path, label_text,
                 image_pos=(3, 2), text_pos=(22, 2), image_scale=14.0,
                 *args, **kwargs):
        wx.Window.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.button_index = btn_index
        self.image_position = image_pos
        self.text_pos = text_pos
        self.image_scale = image_scale
        self.label_text = label_text
        self.image_path = image_path

        self.set_defaults()

        self.image = wx.Image(image_path, type=wx.BITMAP_TYPE_ANY)
        self.image = self.image.Scale(image_scale, image_scale)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Image.ConvertToBitmap(self.image))

        self.text_ctrl = wx.StaticText(self, label=self.label_text)
        self.text_ctrl_font = wx.Font(8, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        self.text_ctrl.SetFont(self.text_ctrl_font)
        self.text_ctrl.SetForegroundColour(edPreferences.Colors.Bold_Label)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def set_defaults(self):
        self.SetWindowStyle(wx.BORDER_NONE)
        self.SetBackgroundColour(Selection_btn_color_normal)
        self.Refresh()

    def on_click(self, event=None, **kwargs):
        self.parent.on_button_clicked(self.button_index, **kwargs)
        self.SetBackgroundColour(Selection_btn_color_pressed)
        self.Refresh()
        if event:
            event.Skip()

    def deselect(self):
        self.SetBackgroundColour(Selection_btn_color_normal)
        self.Refresh()

    def on_size(self, event):
        self.imageCtrl.SetPosition(self.image_position)
        self.text_ctrl.SetPosition(self.text_pos)
        self.Refresh()
        event.Skip()


class TextPanel(wx.Panel):
    def __init__(self, parent, text, *args):
        wx.Panel.__init__(self, parent, *args)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        bold_font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        text_colour = edPreferences.Colors.Text

        self.label = wx.StaticText(self, 0, "Readme")
        self.label.SetForegroundColour(text_colour)
        self.label.SetFont(bold_font)

        self.text = wx.StaticText(self, 0, text, style=wx.TE_MULTILINE)
        self.text.SetForegroundColour(text_colour)

        self.sizer.Add(self.label, 0)
        self.sizer.Add(self.text, 1)

        self.SetSizer(self.sizer)
        self.Layout()


class BaseInspectorPanel(ScrolledPanel):
    def __init__(self, parent, *args, **kwargs):
        ScrolledPanel.__init__(self, parent, *args, **kwargs)

        self.SetBackgroundColour(edPreferences.Colors.Panel_Normal)
        self.SetWindowStyleFlag(wx.BORDER_SUNKEN)

        self.wxMain = parent

        self.property_and_type = {
            int: wxProperty.IntProperty,
            float: wxProperty.FloatProperty,
            str: wxProperty.StringProperty,
            bool: wxProperty.BoolProperty,

            LVecBase2f: wxProperty.Vector2Property,
            LPoint2f: wxProperty.Vector2Property,

            LVecBase3f: wxProperty.Vector3Property,
            LPoint3f: wxProperty.Vector3Property,

            LColor: wxProperty.ColorProperty,

            "label": wxProperty.LabelProperty,
            "choice": wxProperty.EnumProperty,
            "button": wxProperty.ButtonProperty,
            "slider": wxProperty.SliderProperty,
            "space": wxProperty.EmptySpace,

            "info_box": wxProperty.InfoBox,

            "horizontal_layout_group": wxProperty.HorizontalLayoutGroup,
        }

        self.property_and_name = {}

        self.selected_object = None
        self.name = ""
        self.properties = []

        self.fold_manager = None  # a FoldPanelManager for laying out variables of a python module
        self.text_panel = None  # a text_panel for displaying .txt files

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.inspector_ids_map = {}
        self.selected_btn_index = -1  # the index of selected button of selection grid.
        self.selection_grid = self.create_selection_buttons()

        self.Bind(wx.EVT_SIZE, self.on_event_size)

    def create_selection_buttons(self):
        # create selection buttons
        selection_grid = SelectionGrid(self, self.on_selection_button_select)

        inspector_panel_btn = SelectionButton(selection_grid, 0, Object_settings_icon, "Inspector")
        world_settings_btn = SelectionButton(selection_grid, 1, World_settings_icon, "World", image_scale=13,
                                             image_pos=(3, 2), text_pos=(21, 2))
        ed_settings_btn = SelectionButton(selection_grid, 2, Ed_settings_icon, "Editor")
        plugins_panel_btn = SelectionButton(selection_grid, 3, Plugin_icon, "Plugins")

        selection_grid.add_button(inspector_panel_btn, flags=wx.EXPAND | wx.RIGHT, border=1)
        selection_grid.add_button(world_settings_btn, flags=wx.EXPAND | wx.RIGHT, border=1)
        selection_grid.add_button(ed_settings_btn, flags=wx.EXPAND | wx.RIGHT, border=1)
        selection_grid.add_button(plugins_panel_btn, flags=wx.EXPAND)

        # map objects to selection buttons
        self.inspector_ids_map[inspector_panel_btn.button_index] = Object_Inspector
        self.inspector_ids_map[world_settings_btn.button_index] = World
        self.inspector_ids_map[ed_settings_btn.button_index] = EditorSettings
        self.inspector_ids_map[plugins_panel_btn.button_index] = Plugins

        self.sizer.Add(selection_grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border=5)
        return selection_grid

    def on_selection_button_select(self, sel_btn_index: int, **kwargs):
        self.selected_btn_index = sel_btn_index
        inspector = self.inspector_ids_map[sel_btn_index]  # get the inspector to layout properties for

        le = constants.object_manager.get("LevelEditor")

        layout_object = None  # the object to layout properties for,
        name = ""  # it's name and
        properties = []  # properties

        constants.obs.trigger("DeselectAll")

        if inspector == Object_Inspector:
            txt = "Select an object in scene to view its inspector"
            self.set_text(txt)
            return

        elif inspector == World:
            layout_object = le.active_scene
            name = "World"
            properties = layout_object.get_properties()

        elif inspector == EditorSettings:
            layout_object = le.editor_settings
            name = "Editor Settings"
            properties = layout_object.get_properties()

        elif inspector == Plugins:
            layout_object = le.plugins_manager
            name = "Plugins Manager"
            properties = layout_object.get_properties()

        self.layout_object_properties(layout_object, name, properties, scene_object=False)

    def layout_object_properties(self, obj, name, properties, scene_object=True):
        """Layout properties for a python class.
        1. obj = the python class,
        2. name = name of class,
        3. properties = editor properties of this class (see editor.utils.property),
        4. scene_object = if this is a user defined object for example a node-path or a user module etc."""

        # workaround to select first button in selection grid
        if scene_object:
            self.selection_grid.deselect_all()
            self.selected_btn_index = 0
            self.selection_grid.selected_btn_index = 0
            btn = self.selection_grid.buttons[0]
            btn.SetBackgroundColour(Selection_btn_color_pressed)
            btn.Refresh()

        toggle_property = None

        # make sure if obj is of type editor plugin or runtime user module
        # the field module_type is added to user modules automatically and set to either EditorPlugin or RuntimeModule
        # see level_editor.load_all_modules
        if hasattr(obj, "module_type"):
            if obj.module_type == constants.EditorPlugin:
                toggle_property = None
            else:
                # create editor property object
                toggle_property = edProperty.FuncProperty(name="", value=obj.get_active_status(),
                                                          setter=obj.set_active, getter=obj.get_active_status)

        #
        self.reset()
        self.selected_object = obj
        self.name = name
        self.properties = properties

        # init fold manager
        self.fold_manager = WxFoldPanelManager(self)
        self.fold_manager.SetWindowStyle(wx.BORDER_DOUBLE)
        self.sizer.Add(self.fold_manager, 0, wx.EXPAND)

        # add a fold panel
        fold_panel = self.fold_manager.add_panel(name[0].upper() + name[1:], None, False if toggle_property else True)
        fold_panel.Hide()

        # set toggle property for fold panel if toggle property is not None
        if toggle_property is not None:
            wx_property = self.get_wx_prop_object(toggle_property, fold_panel, False)  # wrap into wx property object
            fold_panel.set_toggle_property(wx_property)
            fold_panel.create_buttons()

        properties = self.create_wx_properties(properties, fold_panel)
        for wx_property in properties:
            fold_panel.add_control(wx_property)

        self.on_event_size(None)  # this is force update panel sizes
        fold_panel.switch_expanded_state(False)
        fold_panel.Show()

    def set_text_from_file(self, text_file):
        """set text for a .txt file"""

        with open(text_file, "r", encoding="utf-8") as file:
            readme_text = file.read()
            self.set_text(readme_text)

    def set_text(self, text):
        self.reset()

        if type(text) == str:
            self.text_panel = TextPanel(self, text)
            self.text_panel.SetMinSize((self.GetSize().x - 40, self.GetSize().y - 40))

            self.sizer.Add(self.text_panel, 1, wx.EXPAND | wx.ALL, border=10)
            self.Layout()

    def update_properties_panel(self, force_update_all=False):
        for key in self.property_and_name.keys():
            wx_prop = self.property_and_name[key]

            # if the selected object does not contain this saved property, then layout again.
            if not self.selected_object.has_ed_property(wx_prop.label):
                self.layout_object_properties(self.selected_object, self.name, self.properties)
                break

            # don't update these
            if wx_prop.property.get_type() in ["button"]:
                continue

            if not force_update_all and wx_prop.property.get_type() is "choice":
                continue

            # to avoid triggering on_event_text
            # see wxCustomProperties.py bind and unbind methods
            wx_prop.unbind_events()

            if not wx_prop.has_focus():
                wx_prop.set_control_value(wx_prop.property.get_value())

            # bind them again
            wx_prop.bind_events()

    def get_wx_property_object(self, ed_property, parent, save=True):
        ed_property.validate()
        if ed_property.is_valid:
            wx_property = self.get_wx_prop_object(ed_property, parent, save)  # get wx object
            return wx_property
        else:
            print("{0} editor property validation failed".format(ed_property.name))
            return False

    def create_wx_properties(self, ed_properties, parent, save=True):
        """creates and returns a list of wx_properties from ed_property objects
        ed_properties = list of editor property objects"""
        properties = []
        for prop in ed_properties:
            wx_property_obj = self.get_wx_property_object(prop, parent, save)
            if wx_property_obj:
                properties.append(wx_property_obj)
        return properties

    def get_wx_prop_object(self, _property, parent, save=True):
        wx_property = None

        if self.property_and_type.__contains__(_property.get_type()):
            wx_property = self.property_and_type[_property.get_type()]
            wx_property = wx_property(parent, _property, h_offset=6)

            if wx_property.property.get_type() == "horizontal_layout_group":
                wx_properties = self.create_wx_properties(wx_property.property.properties, wx_property, False)
                wx_property.properties = wx_properties

            # wx_property
            wx_property.create_control()
            wx_property.on_control_created()

            if save:
                self.property_and_name[_property.get_name()] = wx_property

        return wx_property

    def has_object(self):
        return self.selected_object is not None

    def reset(self):
        self.selected_object = None
        self.property_and_name.clear()

        if self.fold_manager is not None:
            self.sizer.Detach(self.fold_manager)
            self.fold_manager.reset()
            self.fold_manager.Destroy()
            self.fold_manager = None

        if self.text_panel is not None:
            self.text_panel.Destroy()
            self.text_panel = None

        # self.sizer.Clear()
        self.Layout()

    def on_event_size(self, evt):
        if self.fold_manager is not None:
            offset = wx.Size(self.GetSize().x - 5, self.fold_manager.size_y)
            self.fold_manager.SetMaxSize(offset)
            self.fold_manager.SetMinSize(offset)

        if self.text_panel is not None:
            offset = wx.Size(self.GetSize().x - 5, -1)
            self.text_panel.SetMaxSize(offset)
            self.text_panel.SetMinSize(offset)

        if evt:
            evt.Skip()
