import pickle
import wx
import editor.edPreferences as edPreferences
import editor.constants as constants
import editor.wxUI.custom as wx_custom

from editor.utils import EdProperty as edProperty
from wx.lib.scrolledpanel import ScrolledPanel
from editor.wxUI.foldPanel import FoldPanelManager
from editor.wxUI.wxCustomProperties import Property_And_Type
from editor.globals import editor
from panda3d.core import NodePath

# icon paths
World_settings_icon = constants.ICONS_PATH + "//" + "globe.png"
Ed_settings_icon = constants.ICONS_PATH + "//" + "gear.png"
Object_settings_icon = constants.ICONS_PATH + "//" + "box_closed.png"
Plugin_icon = constants.ICONS_PATH + "//" + "plugin.png"

PIN_ICON = constants.ICONS_PATH + "//" + "pin.png"
REMOVE_ICON = constants.ICONS_PATH + "//" + "close.png"
# REFRESH_BTN_ICON = constants.ICONS_PATH + "//" + "arrow_refresh.png"

Object_Inspector = 0
World_Inspector = 1
EditorSettings_Inspector = 2
PluginSettings_Inspector = 3


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


class BaseInspectorPanel(wx.Panel):
    class FoldManagerPanel(ScrolledPanel):
        """a sub scrolled-panel for adding the FoldManager"""

        def __init__(self, parent):
            ScrolledPanel.__init__(self, parent)
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.SetSizer(self.sizer)
            self.SetupScrolling(scroll_x=False)

    class DragDropCompPanel(wx.Panel):
        class TestDropTarget(wx.PyDropTarget):
            """ This is a custom DropTarget object designed to match drop behavior to the feedback given by the custom
               Drag Object's GiveFeedback() method. """

            def __init__(self, image_tiles):
                wx.DropTarget.__init__(self)
                self.image_tiles = image_tiles

                self.drop_item = None
                self.drop_location = None

                # specify the data formats to accept
                self.data_format = wx.DataFormat('ImageTileData')
                self.custom_data_obj = wx.CustomDataObject(self.data_format)
                self.SetDataObject(self.custom_data_obj)

            def OnEnter(self, x, y, d):
                # print "OnEnter %s, %s, %s" % (x, y, d)
                # Just allow the normal wxDragResult (d) to pass through here
                editor.wx_main.SetCursor(wx.Cursor(wx.CURSOR_HAND))
                return d

            def OnLeave(self):
                editor.wx_main.SetCursor(wx.Cursor(wx.CURSOR_NO_ENTRY))

            def OnDrop(self, x, y):
                return True

            def OnData(self, x, y, d):
                if self.GetData():
                    data = pickle.loads(self.custom_data_obj.GetData())
                    editor.level_editor.register_component(data.path)
                else:
                    return wx.DragNone

                return d

        def __init__(self, *args, **kwargs):
            wx.Panel.__init__(self, *args, **kwargs)
            self.SetWindowStyleFlag(wx.BORDER_DOUBLE)
            self.SetBackgroundColour(edPreferences.Colors.Panel_Normal)
            self.SetMinSize(wx.Size(-1, 40))
            self.SetMaxSize(wx.Size(-1, 40))
            self.SetSize(wx.Size(-1, 40))

            self.main_sizer = wx.BoxSizer(wx.VERTICAL)
            self.SetSizer(self.main_sizer)

            self.font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.BOLD)

            self.ctrl_label = wx.StaticText(self, label="DRAG COMPONENTS HERE.")
            self.ctrl_label.SetFont(self.font)
            self.ctrl_label.SetForegroundColour(edPreferences.Colors.Inspector_properties_label)

            # self.static_line = wx.StaticLine(self, style=wx.SL_HORIZONTAL)

            self.main_sizer.AddStretchSpacer()
            self.main_sizer.Add(self.ctrl_label, 0, wx.CENTER)
            # self.main_sizer.Add(self.static_line, 0, wx.EXPAND | wx.CENTER | wx.LEFT | wx.RIGHT, border=50)
            self.main_sizer.AddStretchSpacer()

            # create a drop target
            dt = BaseInspectorPanel.DragDropCompPanel.TestDropTarget(self)
            self.SetDropTarget(dt)

    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        self.SetBackgroundColour(edPreferences.Colors.Panel_Dark)
        self.wxMain = parent

        self.property_and_name = {}

        self.object = None
        self.label = ""
        self.properties = []

        self.fold_manager_panel = BaseInspectorPanel.FoldManagerPanel(self)
        self.fold_manager = None  # a FoldPanelManager for laying out variables of a python module
        self.text_panel = None  # a text_panel for displaying .txt files

        self.components_dnd_panel = None  # components drag and drop panel

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.inspector_type_btns_id_map = {}
        self.sel_btn_index = -1  # the index of selected button of selection grid.
        self.inspector_type_btns = self.create_inspector_type_buttons()

        self.__is_dirty = False

        self.static_line = wx.StaticLine(self, style=wx.SL_HORIZONTAL)
        # self.v_sizer.Add(self.static_line, 0, wx.EXPAND | wx.BOTTOM, border=0)

        self.main_sizer.Add(self.inspector_type_btns, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border=5)
        self.main_sizer.Add(self.static_line, 0, wx.EXPAND | wx.BOTTOM, border=1)
        self.main_sizer.Add(self.fold_manager_panel, 1, wx.EXPAND)

    def create_inspector_type_buttons(self):
        # create selection buttons
        self.inspector_type_btns = wx_custom.ControlGroup(self, size=(-1, 18))

        inspector_panel_btn = wx_custom.SelectionButton(self.inspector_type_btns,
                                                        0,
                                                        "Inspector",
                                                        image_path=Object_settings_icon,
                                                        select_func=self.on_inspector_select)

        world_settings_btn = wx_custom.SelectionButton(self.inspector_type_btns,
                                                       1,
                                                       "World",
                                                       text_pos=(21, 2),
                                                       image_path=World_settings_icon,
                                                       image_pos=(3, 2),
                                                       image_scale=13,
                                                       select_func=self.on_inspector_select)

        ed_settings_btn = wx_custom.SelectionButton(self.inspector_type_btns,
                                                    2,
                                                    "Editor",
                                                    image_path=Ed_settings_icon,
                                                    select_func=self.on_inspector_select)

        plugins_panel_btn = wx_custom.SelectionButton(self.inspector_type_btns,
                                                      3,
                                                      "Plugins",
                                                      image_path=Plugin_icon,
                                                      select_func=self.on_inspector_select)

        self.inspector_type_btns.add_button(inspector_panel_btn, flags=wx.EXPAND | wx.RIGHT, border=1)
        self.inspector_type_btns.add_button(world_settings_btn, flags=wx.EXPAND | wx.RIGHT, border=1)
        self.inspector_type_btns.add_button(ed_settings_btn, flags=wx.EXPAND | wx.RIGHT, border=1)
        self.inspector_type_btns.add_button(plugins_panel_btn, flags=wx.EXPAND)

        # map objects to selection buttons
        self.inspector_type_btns_id_map[inspector_panel_btn.button_index] = Object_Inspector
        self.inspector_type_btns_id_map[world_settings_btn.button_index] = World_Inspector
        self.inspector_type_btns_id_map[ed_settings_btn.button_index] = EditorSettings_Inspector
        self.inspector_type_btns_id_map[plugins_panel_btn.button_index] = PluginSettings_Inspector

        return self.inspector_type_btns

    def create_fold_panel_controls(self, parent,
                                   pin_btn=False, pin_btn_data=None,
                                   remove_btn=False, remove_btn_data=None):
        control_group = wx_custom.ControlGroup(parent, size=(-1, 18))

        """creates wx_custom.ControlGroup for a fold_panel"""

        idx = 0

        if pin_btn:
            pin_btn = wx_custom.ToggleButton(
                parent=control_group,
                btn_index=idx,
                label_text="",
                image_path=PIN_ICON,
                image_pos=(1, 2),
                image_scale=16,
                select_func=self.set_pinned,
                deselect_func=self.clear_pinned,
                bg_color=parent.GetBackgroundColour(),
                data=pin_btn_data,
            )
            control_group.add_button(pin_btn, border=0)
            idx += 1

        if remove_btn:
            remove_btn = wx_custom.BasicButton(
                parent=control_group,
                btn_index=idx,
                label_text="",
                image_path=REMOVE_ICON,
                image_pos=(0, 4),
                image_scale=8,
                select_func=self.remove_component,
                bg_color=parent.GetBackgroundColour(),
                data=remove_btn_data,
            )
            control_group.add_button(remove_btn, flags=wx.EXPAND, border=0)
            idx += 1

        return control_group

    def on_inspector_select(self, index, data=None):
        self.sel_btn_index = index
        inspector = self.inspector_type_btns_id_map[index]  # get the inspector to layout properties for

        # reset everything
        self.object = self.properties = self.label = None

        is_text = False
        text = ""

        le = editor.level_editor
        resource_tree = editor.resource_browser

        if inspector == Object_Inspector:
            if len(le.selection.selected_nps) > 0:
                obj = le.selection.selected_nps[0]
                self.object = obj
                self.label = obj.get_name()
                self.properties = obj.get_properties()
            elif len(resource_tree.selected_files) > 0:
                path = resource_tree.selected_files[0]
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
                editor.observer.trigger("DeselectAll")
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

    def layout_auto(self):
        """automatically create inspector based on selected inspector and selected scene object"""
        # get the inspector
        if self.sel_btn_index == -1:
            return

        inspector = self.inspector_type_btns_id_map[self.sel_btn_index]
        if inspector in [World_Inspector, EditorSettings_Inspector, PluginSettings_Inspector]:
            return

        # get the selected scene object or resource item
        # reset everything
        self.object = self.properties = self.label = None

        is_text = False
        text = ""

        le = editor.level_editor
        resource_tree = editor.resource_browser
        if inspector == Object_Inspector:
            if len(le.selection.selected_nps) > 0:
                obj = le.selection.selected_nps[0]
                self.object = obj
                self.label = obj.get_name()
                self.properties = obj.getPythonTag(constants.TAG_GAME_OBJECT).get_properties()
            elif len(resource_tree.selected_files) > 0:
                path = resource_tree.selected_files[0]
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
            self.layout(layout_object, name, properties)
        elif is_text:
            self.set_text(text)
        else:
            editor.observer.trigger("DeselectAll")
            txt = "Select an object in scene to view its inspector."
            self.set_text(txt)

    def layout(self, obj=None, name=None, properties=None, scene_obj=True, reset=True):
        """Layout properties for a python class.
        1. obj = the python class,
        2. name = name of class,
        3. properties = editor properties of this class (see editor.utils.property),
        4. scene_object = if this is a user defined object for example a node-path or a user module etc."""

        def get_toggle_property(parent):
            if hasattr(obj, "_PModBase__module_type"):
                if obj.type in [constants.RuntimeModule, constants.Component]:
                    # create a toggle property object
                    property_ = edProperty.FuncProperty(name="",
                                                        value=obj.get_active_status(),
                                                        setter=obj.set_active,
                                                        getter=obj.get_active_status)
                    #
                    # and wrap it into wx_property object
                    wx_property = self.get_wx_property_object(property_, parent, False)
                    wx_property.SetBackgroundColour(parent.GetBackgroundColour())
                    wx_property.SetSize((-1, 16))
                    wx_property.SetMinSize((-1, 16))
                    wx_property.SetMaxSize((-1, 16))
                    #
                    return wx_property

            return None

        # only create inspector for scene object if inspector_type == ObjectInspector
        inspector = self.inspector_type_btns_id_map[self.sel_btn_index]
        if scene_obj:
            if inspector != Object_Inspector:
                return

        if reset:
            self.reset()
            self.object = obj
            self.label = name if name else self.label
            self.properties.extend(properties)
            self.fold_manager = FoldPanelManager(self.fold_manager_panel)
            self.fold_manager_panel.sizer.Add(self.fold_manager, 0, wx.EXPAND, border=0)
            obj_label = self.label[0].upper() + self.label[1:]

            # for objects of type NodePaths, create a drop target to drag and drop components from project
            # onto this NodePath
            if isinstance(obj, NodePath):
                if self.components_dnd_panel is None:
                    self.components_dnd_panel = BaseInspectorPanel.DragDropCompPanel(self.fold_manager_panel)
                    self.fold_manager_panel.sizer.Add(self.components_dnd_panel, 1, wx.EXPAND | wx.LEFT | wx.TOP,
                                                      border=8)

        else:
            self.properties.extend(properties)
            obj_label = name[0].upper() + name[1:]

        # add a fold panel for the top object
        fold_panel = self.fold_manager.add_panel(obj_label, False)
        fold_panel.Hide()

        # the first fold_panel will always contain the object (NodePath or any other resource item), so only
        # create a pin button for it
        if len(self.fold_manager.panels) == 1:
            fold_panel.create_buttons(
                toggle_btn=get_toggle_property(fold_panel),
                control_group=self.create_fold_panel_controls(fold_panel, pin_btn=True))
        else:
            if obj.type == constants.Component:
                fold_panel.create_buttons(
                    toggle_btn=get_toggle_property(fold_panel),
                    control_group=self.create_fold_panel_controls(fold_panel,
                                                                  remove_btn=True,
                                                                  remove_btn_data=(self.object, obj.path)))

        #
        properties = self.create_wx_properties(properties, fold_panel)
        #
        fold_panel.set_controls(properties)
        fold_panel.switch_expanded_state(False)
        fold_panel.Show()

        # if object is of type NodePath, then layout properties for its components as well.
        if isinstance(obj, NodePath):
            if hasattr(obj, "components"):
                for key in obj.components:
                    comp = obj.components[key].class_instance
                    self.layout(comp,
                                obj.components[key].class_instance.name,
                                comp.get_properties(),
                                scene_obj=True,
                                reset=False)

        self.fold_manager_panel.SetupScrolling(scroll_x=False)
        self.main_sizer.Layout()
        self.__is_dirty = False

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
            self.main_sizer.Add(self.text_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
            self.Layout()

    def update(self, label=None, force_update_all=False):
        """updates the selected object's properties
        label : new label if None then existing label is used
        force_update_all : """

        if self.__is_dirty:
            editor.wx_main.freeze()
            if self.has_object():
                self.layout_auto()
            editor.wx_main.thaw()
            return

        if label:
            self.fold_manager.panels[0].label = label
            self.label = label

        for key in self.property_and_name.keys():
            wx_prop = self.property_and_name[key]

            # don't update these
            if wx_prop.property.type_ in ["button"]:
                continue

            if not force_update_all and wx_prop.property.type_ is "choice":
                continue

            # to avoid triggering on_event_text
            # see wxCustomProperties.py bind and unbind methods
            wx_prop.unbind_events()

            if not wx_prop.has_focus():
                wx_prop.set_control_value(wx_prop.property.get_value())

            # bind them again
            wx_prop.bind_events()

    def create_wx_properties(self, ed_properties, parent, save=True):
        """creates and returns a list of wx_properties from ed_property objects
        ed_properties = list of editor property objects"""
        properties = []
        for prop in ed_properties:
            wx_property_obj = self.get_wx_property_object(prop, parent, save)
            if wx_property_obj:
                properties.append(wx_property_obj)
        return properties

    def get_wx_property_object(self, ed_property, parent, save=True):
        ed_property.validate()
        wx_property = None

        if ed_property.is_valid:
            # ------------------------------------------------------------------------------
            if Property_And_Type.__contains__(ed_property.type_):
                wx_property = Property_And_Type[ed_property.type_]
                wx_property = wx_property(parent, ed_property)

                if wx_property.property.type_ == "horizontal_layout_group" or wx_property.property.type_ == \
                        "foldout_group":
                    wx_properties = self.create_wx_properties(wx_property.property.properties, wx_property, False)
                    wx_property.properties = wx_properties
                    # see wxProperties.Foldout for explanation on this.
                    if hasattr(wx_property, "scrolled_panel"):
                        wx_property.scrolled_panel = self

                # wx_property
                wx_property.create_control()
                wx_property.on_control_created()

                if save:
                    self.property_and_name[ed_property.name] = wx_property
            # ------------------------------------------------------------------------------

        return wx_property

    def set_pinned(self, *args):
        print("pinned")
        pass

    def clear_pinned(self, *args):
        print("clear pinned")
        pass

    def remove_component(self, idx, data):
        obj = data[0]
        comp_path = data[1]
        obj.detach_component(comp_path)
        self.mark_dirty()

    def mark_dirty(self):
        self.__is_dirty = True

    def has_object(self):
        return self.object is not None

    def reset(self):
        self.object = None
        self.label = None
        self.properties = []
        self.property_and_name.clear()

        if self.text_panel is not None:
            self.main_sizer.Detach(self.text_panel)
            self.text_panel.Destroy()
            self.text_panel = None

        if self.fold_manager is not None:
            self.main_sizer.Detach(self.fold_manager)
            self.fold_manager.Destroy()
            self.fold_manager = None

        if self.components_dnd_panel:
            self.main_sizer.Detach(self.components_dnd_panel)
            self.components_dnd_panel.Destroy()
            self.components_dnd_panel = None

        # self.sizer.Clear()
        self.fold_manager_panel.SetupScrolling(scroll_x=False)
        self.Layout()
