import wx
import editor.edPreferences as edPreferences
import editor.wxUI.wxCustomProperties as wxProperty
import editor.constants as constants
import editor.wxUI.custom as wx_custom
from editor.utils import EdProperty as edProperty
from wx.lib.scrolledpanel import ScrolledPanel
from editor.wxUI.foldPanel import FoldPanelManager
from panda3d.core import LVecBase2f, LPoint2f, LVecBase3f, LPoint3f, LColor, PerspectiveLens, OrthographicLens

# icon paths
World_settings_icon = constants.ICONS_PATH + "//" + "globe.png"
Ed_settings_icon = constants.ICONS_PATH + "//" + "gear.png"
Object_settings_icon = constants.ICONS_PATH + "//" + "box_closed.png"
Plugin_icon = constants.ICONS_PATH + "//" + "plugin.png"

Object_Inspector = "ObjectInspector"
World_Inspector = "World"
EditorSettings_Inspector = "Editor"
PluginSettings_Inspector = "Plugins"


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

        self.SetBackgroundColour(edPreferences.Colors.Panel_Dark)
        # self.SetWindowStyleFlag(wx.BORDER_SUNKEN)

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
            "foldout_group": wxProperty.FoldoutGroup,

            # "PerspectiveLens": PerspectiveLens,
            # "OrthographicLens": OrthographicLens,
        }

        self.property_and_name = {}

        self.object = None
        self.label = ""
        self.properties = []
        self.wx_properties = []

        self.fold_manager = None  # a FoldPanelManager for laying out variables of a python module
        self.text_panel = None  # a text_panel for displaying .txt files

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.inspector_type_btns_id_map = {}
        self.sel_btn_index = -1  # the index of selected button of selection grid.
        self.inspector_type_btns = self.create_selection_buttons()

        self.Bind(wx.EVT_SIZE, self.on_event_size)
        self.SetupScrolling()

    def create_selection_buttons(self):
        # create selection buttons
        self.inspector_type_btns = wx_custom.ControlGroup(self, size=(-1, 18))

        inspector_panel_btn = wx_custom.SelectionButton(self.inspector_type_btns,
                                                        0,
                                                        "Inspector",
                                                        image_path=Object_settings_icon,
                                                        select_func=self.on_selection_button_select)

        world_settings_btn = wx_custom.SelectionButton(self.inspector_type_btns,
                                                       1,
                                                       "World",
                                                       text_pos=(21, 2),
                                                       image_path=World_settings_icon,
                                                       image_pos=(3, 2),
                                                       image_scale=13,
                                                       select_func=self.on_selection_button_select)

        ed_settings_btn = wx_custom.SelectionButton(self.inspector_type_btns,
                                                    2,
                                                    "Editor",
                                                    image_path=Ed_settings_icon,
                                                    select_func=self.on_selection_button_select)

        plugins_panel_btn = wx_custom.SelectionButton(self.inspector_type_btns,
                                                      3,
                                                      "Plugins",
                                                      image_path=Plugin_icon,
                                                      select_func=self.on_selection_button_select)

        self.inspector_type_btns.add_button(inspector_panel_btn, flags=wx.EXPAND | wx.RIGHT, border=1)
        self.inspector_type_btns.add_button(world_settings_btn, flags=wx.EXPAND | wx.RIGHT, border=1)
        self.inspector_type_btns.add_button(ed_settings_btn, flags=wx.EXPAND | wx.RIGHT, border=1)
        self.inspector_type_btns.add_button(plugins_panel_btn, flags=wx.EXPAND)

        # map objects to selection buttons
        self.inspector_type_btns_id_map[inspector_panel_btn.button_index] = Object_Inspector
        self.inspector_type_btns_id_map[world_settings_btn.button_index] = World_Inspector
        self.inspector_type_btns_id_map[ed_settings_btn.button_index] = EditorSettings_Inspector
        self.inspector_type_btns_id_map[plugins_panel_btn.button_index] = PluginSettings_Inspector

        self.sizer.Add(self.inspector_type_btns, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border=5)
        return self.inspector_type_btns

    def on_selection_button_select(self, sel_btn_index: int, **kwargs):
        self.sel_btn_index = sel_btn_index
        inspector = self.inspector_type_btns_id_map[sel_btn_index]  # get the inspector to layout properties for

        # reset everything
        self.object = self.properties = self.label = None

        is_text = False
        text = ""

        le = constants.object_manager.get("LevelEditor")
        resource_tiles = constants.object_manager.get("ResourceTilesPanel")
        if inspector == Object_Inspector:
            if len(le.selection.selected_nps) > 0:
                obj = le.selection.selected_nps[0]
                self.object = obj
                self.label = obj.get_name()
                self.properties = obj.get_properties()
            elif resource_tiles.SELECTED_TILE:
                path = resource_tiles.SELECTED_TILE.data
                if le.is_module(path):
                    self.object = le.get_module(path)
                    self.label = self.object.name
                    self.properties = self.object.get_properties()
                elif le.is_text_file(path):
                    text = le.get_text_file(path).text
                    is_text = True

        layout_object = self.object if self.object else None  # the inspector to layout properties for
        name = self.label if self.label else None  # it's name and
        properties = self.properties if self.properties else None  # properties

        is_scene_obj = False

        if inspector == Object_Inspector:
            if layout_object and name and properties:
                is_scene_obj = True
            elif is_text:
                self.set_text(text)
                return
            else:
                constants.obs.trigger("DeselectAll")
                txt = "Select an object in scene to view its inspector."
                self.set_text(txt)
                return

        elif inspector == World_Inspector:
            txt = "This section is incomplete, support PandaEditor on Patreon to help speed up its development."
            self.set_text(txt)
            return

        elif inspector == EditorSettings_Inspector:
            layout_object = le.editor_settings
            name = "Editor Settings"
            properties = layout_object.get_properties()

        elif inspector == PluginSettings_Inspector:
            txt = "This section is incomplete, support PandaEditor on Patreon to help speed up its development."
            self.set_text(txt)
            return

        self.layout(layout_object, name, properties, is_scene_obj)

    def set_object(self, obj, name, properties):
        self.layout(obj, name, properties)

    def layout(self, obj=None, name=None, properties=None, scene_obj=True):
        """Layout properties for a python class.
        1. obj = the python class,
        2. name = name of class,
        3. properties = editor properties of this class (see editor.utils.property),
        4. scene_object = if this is a user defined object for example a node-path or a user module etc."""

        # only create inspector for scene object if inspector_type == ObjectInspector
        inspector = self.inspector_type_btns_id_map[self.sel_btn_index]
        if scene_obj:
            if inspector != Object_Inspector:
                return

        toggle_property = None
        # make sure if obj is of type editor plugin or runtime user module
        # the field module_type is added to user modules automatically and set to either EditorPlugin or RuntimeModule
        # see level_editor.load_all_modules
        # TODO replace this with one common interface for all inspectors
        if hasattr(obj, "_PModBase__module_type"):
            if obj.type == constants.EditorPlugin:
                toggle_property = None
            else:
                # create editor property object
                toggle_property = edProperty.FuncProperty(name="", value=obj.get_active_status(),
                                                          setter=obj.set_active, getter=obj.get_active_status)
        # -----------------------------------------------------------------

        self.reset()
        self.object = obj if obj else self.object
        self.label = name if name else self.label
        self.properties = properties if properties else self.properties
        if self.properties is None:
            self.properties = []
        self.wx_properties.clear()

        self.fold_manager = FoldPanelManager(self)
        self.sizer.Add(self.fold_manager, 1, wx.EXPAND, border=0)

        # add a fold panel
        fold_panel = self.fold_manager.add_panel(self.label[0].upper() + self.label[1:],
                                                 None, False if toggle_property else True)
        fold_panel.Hide()

        # set toggle property for fold panel if toggle property is not None
        if toggle_property is not None:
            wx_property = self.get_wx_prop_object(toggle_property, fold_panel, False)  # wrap into wx property object

            wx_property.SetSize((-1, 16))
            wx_property.SetMinSize((-1, 16))
            wx_property.SetMaxSize((-1, 16))

            fold_panel.set_toggle_property(wx_property)
            fold_panel.create_buttons()

        properties = self.create_wx_properties(self.properties, fold_panel)
        fold_panel.set_controls(properties)

        fold_panel.switch_expanded_state(False)
        fold_panel.Show()

        self.SetupScrolling(scroll_x=False)
        self.sizer.Layout()

    def layout_auto(self):
        """automatically create inspector based on selected inspector and selected scene object"""
        # get the inspector
        if self.sel_btn_index == -1:
            return
        inspector = self.inspector_type_btns_id_map[self.sel_btn_index]

        # only create layout for ObjectInspector
        if inspector in [World_Inspector, EditorSettings_Inspector, PluginSettings_Inspector]:
            return

        # get the selected scene object or resource item
        # reset everything
        self.object = self.properties = self.label = None

        is_text = False
        text = ""

        le = constants.object_manager.get("LevelEditor")
        resource_tiles = constants.object_manager.get("ResourceTilesPanel")
        if inspector == Object_Inspector:
            if len(le.selection.selected_nps) > 0:
                obj = le.selection.selected_nps[0]
                self.object = obj
                self.label = obj.get_name()
                self.properties = obj.get_properties()
            elif resource_tiles.SELECTED_TILE:
                path = resource_tiles.SELECTED_TILE.data
                if le.is_module(path):
                    self.object = le.get_module(path)
                    self.label = self.object.name
                    self.properties = self.object.get_properties()
                elif le.is_text_file(path):
                    text = le.get_text_file(path).text
                    is_text = True

        layout_object = self.object if self.object else None  # the inspector to layout properties for

        if layout_object:
            name = self.label if self.label else "Object"  # it's name and
            properties = self.properties if self.properties else []  # properties
            self.layout(layout_object, name, properties, True)
        elif is_text:
            self.set_text(text)
        else:
            constants.obs.trigger("DeselectAll")
            txt = "Select an object in scene to view its inspector."
            self.set_text(txt)

    def set_text_from_file(self, text_file):
        """set text from a .txt file"""
        with open(text_file, "r", encoding="utf-8") as file:
            readme_text = file.read()
            self.set_text(readme_text)

    def set_text(self, text, reset=True):
        if reset:
            self.reset()

        if type(text) == str:
            self.text_panel = TextPanel(self, text)
            self.text_panel.SetMinSize((self.GetSize().x - 40, self.GetSize().y - 40))
            self.sizer.Add(self.text_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
            self.Layout()

    def update_properties_panel(self, label=None, force_update_all=False):
        """updates the selected object's properties
        label : new label if None then existing label is used
        force_update_all : """

        if label:
            self.fold_manager.panels[0].label = label
            self.label = label

        for key in self.property_and_name.keys():
            wx_prop = self.property_and_name[key]

            # TODO can cause recursion, should be replaced with error message
            # if the selected object does not contain this saved property, then layout again.
            if not self.object.has_ed_property(wx_prop.label):
                self.layout(self.object, self.label, self.properties)
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

            if wx_property.property.get_type() == "horizontal_layout_group" or wx_property.property.get_type() == \
                    "foldout_group":
                wx_properties = self.create_wx_properties(wx_property.property.properties, wx_property, False)
                wx_property.properties = wx_properties

                # see wxProperties.Foldout for explanation for this.
                if hasattr(wx_property, "scrolled_panel"):
                    wx_property.scrolled_panel = self

            # wx_property
            wx_property.create_control()
            wx_property.on_control_created()

            if save:
                self.property_and_name[_property.get_name()] = wx_property

        return wx_property

    def has_object(self):
        return self.object is not None

    def reset(self):
        self.object = None
        self.label = None
        self.properties = None
        self.property_and_name.clear()

        if self.text_panel is not None:
            self.sizer.Detach(self.text_panel)
            self.text_panel.Destroy()
            self.text_panel = None

        if self.fold_manager is not None:
            self.sizer.Detach(self.fold_manager)
            self.fold_manager.Destroy()
            self.fold_manager = None

        self.SetupScrolling(scroll_x=False)
        self.Layout()

    def on_event_size(self, evt):
        if self.text_panel is not None:
            offset = wx.Size(self.GetSize().x - 5, -1)
            self.text_panel.SetMaxSize(offset)
            self.text_panel.SetMinSize(offset)

        if evt:
            evt.Skip()

