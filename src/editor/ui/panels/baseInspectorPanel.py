import os.path
import pickle
import wx
import editor.ui.custom as wx_custom
import game.constants as constants

from pathlib import Path
from wx.lib.scrolledpanel import ScrolledPanel
from panda3d.core import NodePath
from commons import EditorProperty
from commons import ed_logging

from editor.constants import ICONS_PATH, GAME_STATE
from editor.globals import editor
from editor.ui.splitwindow import SplitWindow
from editor.ui.foldPanel import FoldPanelManager
from editor.ui.wxCustomProperties import Property_And_Type

from game.resources import PModBase, Component


# icons
OBJECT = str(Path(ICONS_PATH + "/properties panel/box_closed.png"))
GLOBE = str(Path(ICONS_PATH + "/properties panel/globe.png"))
GEAR = str(Path(ICONS_PATH + "/properties panel/gear.png"))
PLUGIN = str(Path(ICONS_PATH + "/properties panel/plugin.png"))
#
Object_Icon = str(Path(ICONS_PATH + "/properties panel/cube.png"))
Camera_Icon = str(Path(ICONS_PATH + "/properties panel/video.png"))
Light_Icon = str(Path(ICONS_PATH + "/properties panel/lightbulb.png"))
#
Script_Icon = str(Path(ICONS_PATH + "/properties panel/script_code.png"))
Component_Icon = str(Path(ICONS_PATH + "/properties panel/script_gear.png"))
Plugin_icon = str(Path(ICONS_PATH + "/properties panel/script_code_red.png"))
#
PIN_ICON = str(Path(ICONS_PATH + "/properties panel/pin.png"))
REMOVE_ICON = str(Path(ICONS_PATH + "/properties panel/close.png"))
INFO_ICON = str(Path(ICONS_PATH + "/properties panel/information.png"))


# map_ = object_type: (bitmap_path, scale)
OBJ_TYPE_ICON_MAP = {constants.Component: (Component_Icon, (14, 14)),
                     constants.RuntimeModule: (Script_Icon, (14, 14)),
                     constants.EditorPlugin: (Plugin_icon, (14, 14)),

                     constants.NODEPATH: (Object_Icon, (13, 13)),
                     constants.ACTOR_NODEPATH: (Object_Icon, (13, 13)),
                     constants.CAMERA_NODEPATH: (Camera_Icon, (15, 15)),

                     constants.POINT_LIGHT: (Light_Icon, (15, 15)),
                     constants.DIRECTIONAL_LIGHT: (Light_Icon, (15, 15)),
                     constants.SPOT_LIGHT: (Light_Icon, (15, 15)),
                     constants.AMBIENT_LIGHT: (Light_Icon, (15, 15))}


ID_PROPERTIES_PANEL_OBJECT_TAB = 0
ID_PROPERTIES_PANEL_WORLD_TAB = 1
ID_PROPERTIES_PANEL_INSPECTOR_TAB = 2
ID_PROPERTIES_PANEL_PLUGINS_TAB = 3


class SelectionGroup(wx.Window):
    def __init__(self, *args, **kwargs):
        wx.Window.__init__(self, *args, **kwargs)
        self.SetBackgroundColour(editor.ui_config.color_map("Panel_Dark"))
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.__buttons = []
        self.__call_back = None

    def add_button(self, text, image_path, image_scale: tuple = None) -> wx_custom.SelectionButton:
        btn = wx_custom.SelectionButton(self, len(self.__buttons), text, image_path=image_path, image_scale=image_scale,
                                        select_func=self.on_btn)
        self.__buttons.append(btn)
        self.sizer.Add(btn, 1, wx.EXPAND | wx.RIGHT, border=1)
        return btn

    def select(self, idx):
        if idx < len(self.__buttons):
            self.__buttons[idx].on_click()

    def set_call_back(self, call_back):
        self.__call_back = call_back

    def on_btn(self, idx, data):
        for btn in self.__buttons:
            btn.deselect()
        if self.__call_back:
            self.__call_back(idx, data)


class TextPanel(wx.Panel):
    def __init__(self, parent, text, *args):
        wx.Panel.__init__(self, parent, *args)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.label = wx.StaticText(self, 0, "Readme")
        self.label.SetForegroundColour(editor.ui_config.color_map("Text_Secondary"))
        self.label.SetFont(font)

        self.text = wx.StaticText(self, 0, text, style=wx.TE_MULTILINE)
        self.text.SetForegroundColour(editor.ui_config.color_map("Text_Primary"))

        font = wx.Font(10, editor.ui_config.font, wx.NORMAL, wx.NORMAL)
        self.text.SetFont(font)

        self.sizer.Add(self.label, 0)
        self.sizer.Add(self.text, 1)

        self.SetSizer(self.sizer)
        self.Layout()



class BaseInspectorPanel(SplitWindow):
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
                self.data_format = wx.DataFormat('ResourceBrowserData | ImageTileData')
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
                    files = [path for path in data.paths if os.path.isfile(path) and os.path.splitext(path)[1] == ".py"]
                    editor.level_editor.register_component(files)
                else:
                    return wx.DragNone

                return d

        def __init__(self, *args, **kwargs):
            wx.Panel.__init__(self, *args, **kwargs)
            self.SetBackgroundColour(editor.ui_config.color_map("Panel_Normal"))
            self.SetMinSize(wx.Size(-1, 40))
            self.SetMaxSize(wx.Size(-1, 40))
            self.SetSize(wx.Size(-1, 40))

            self.main_sizer = wx.BoxSizer(wx.VERTICAL)
            self.SetSizer(self.main_sizer)

            self.font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.BOLD)

            self.ctrl_label = wx.StaticText(self, label="DRAG COMPONENTS HERE.")
            self.ctrl_label.SetFont(self.font)
            self.ctrl_label.SetForegroundColour(editor.ui_config.color_map("Text_Secondary"))

            self.main_sizer.AddStretchSpacer()
            self.main_sizer.Add(self.ctrl_label, 0, wx.CENTER)
            self.main_sizer.AddStretchSpacer()

            # create a drop target
            dt = BaseInspectorPanel.DragDropCompPanel.TestDropTarget(self)
            self.SetDropTarget(dt)

            self.Bind(wx.EVT_SIZE, self.on_size)
            self.Bind(wx.EVT_PAINT, self.on_paint)
            
        def on_size(self, evt):
            self.Refresh()
            evt.Skip()
            
        def on_paint(self, evt):
            pdc = wx.PaintDC(self)
            gc = pdc

            gc.SetPen(wx.Pen(wx.Colour(150, 150, 150, 255), 1))
            gc.SetBrush(wx.Brush(wx.Colour(editor.ui_config.color_map("Panel_Normal"))))
            gc.DrawRectangle(0, 0, self.GetSize().x, self.GetSize().y)

            gc.DrawLine(wx.Point(0, 0), wx.Point(self.GetSize().x, 0))  # top
            gc.DrawLine(wx.Point(0, self.GetSize().y), wx.Point(self.GetSize().x, self.GetSize().y))  # bottom
            gc.DrawLine(wx.Point(0, 0), wx.Point(0, self.GetSize().y))  # left
            gc.DrawLine(wx.Point(self.GetSize().x, 0), wx.Point(self.GetSize().x, self.GetSize().y))  # right
            evt.Skip()

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self.SetBackgroundColour(editor.ui_config.color_map("Panel_Dark"))
        self.create_header()
        
        self.__object = None
        self.__label = ""
        self.__properties = []
        self.property_name_map = {}

        self.__fold_manager = None  # a FoldPanelManager for laying out variables of a python module
        self.__text_panel = None    # a text_panel for displaying .txt files

        self.components_dnd_panel = None  # components drag and drop panel
        self.__main_sizer = self.GetSizer()

        self.tab_id_tab = {0: ID_PROPERTIES_PANEL_OBJECT_TAB,
                           1: ID_PROPERTIES_PANEL_WORLD_TAB,
                           2: ID_PROPERTIES_PANEL_INSPECTOR_TAB,
                           3: ID_PROPERTIES_PANEL_PLUGINS_TAB}

        self.__selected_tab = -1
        self.__tabs = SelectionGroup(self)
        self.__tabs.SetMinSize(wx.Size(-1, 16))
        self.__tabs.SetMaxSize(wx.Size(-1, 16))
        self.__tabs.add_button("Inspector", OBJECT, image_scale=(14, 14))
        self.__tabs.add_button("World", GLOBE, image_scale=(14, 14))
        self.__tabs.add_button("Editor", GEAR, image_scale=(14, 14))
        self.__tabs.add_button("Plugins", PLUGIN, image_scale=(14, 14))
        self.__tabs.set_call_back(self.on_tab_select)

        self.__is_dirty = False
        self.__main_sizer.Add(self.__tabs, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)
        self.__main_sizer.AddSpacer(5)
        self.SetupScrolling(scroll_x=False, scroll_y=True)
        
        return self

    def create_wx_properties(self, ed_properties, parent, save=True):
        """creates and returns a list of wx_properties from ed_property objects
        ed_properties = list of editor property objects"""
        properties = []
        for prop in ed_properties:
            wx_property = self.get_wx_property_object(prop, parent)

            if wx_property:
                properties.append(wx_property)

            if save:
                self.property_name_map[prop.name] = wx_property

        return properties

    def clear_pinned(self, *args):
        print("clear pinned")
        pass

    def get_wx_property_object(self, ed_property, parent):
        ed_property.validate()
        wx_property = None

        if ed_property.is_valid:
            if Property_And_Type.__contains__(ed_property.type_):
                wx_property = Property_And_Type[ed_property.type_]
                wx_property = wx_property(parent, ed_property)

                if wx_property.ed_property.type_ in ["horizontal_layout_group", "foldout_group", "static_box"]:
                    wx_properties = self.create_wx_properties(wx_property.ed_property.properties, wx_property, False)
                    wx_property.set_properties(wx_properties)

                wx_property.create_control()

        return wx_property

    def get_selected_tab(self):
        return self.__selected_tab

    def get_fold_manager(self):
        return self.__fold_manager

    def has_object(self):
        return self.__object is not None

    def layout_auto(self):
        """automatically create inspector based on selected inspector and selected scene object"""
        # get the inspector
        if self.__selected_tab == -1:
            return

        inspector = self.tab_id_tab[self.__selected_tab]
        if inspector in [ID_PROPERTIES_PANEL_WORLD_TAB, ID_PROPERTIES_PANEL_INSPECTOR_TAB, ID_PROPERTIES_PANEL_PLUGINS_TAB]:
            return

        self.__object = self.__properties = self.__label = None

        le = editor.level_editor
        resource_tree = editor.resource_browser
        if len(le.selection.selected_nps) > 0:
            obj = le.selection.selected_nps[0]
            self.__object = obj
            self.__label = obj.get_name()
            self.__properties = obj.getPythonTag(constants.TAG_GAME_OBJECT).get_properties()
            self.layout(self.__object, self.__label, self.__properties)

        elif len(resource_tree.selected_files) > 0:
            path = resource_tree.selected_files[0]
            if le.is_module(path):
                self.__object = le.get_module(path)
                self.__label = self.__object.module_name
                self.__properties = self.__object.get_properties()
                self.layout(self.__object, self.__label, self.__properties)

            elif le.is_text_file(path):
                text = le.get_text_file(path).text
                self.set_text(text)

        else:
            # editor.observer.trigger("DeselectAll")
            txt = "Select an object in scene to view its inspector."
            self.set_text(txt)

    def layout(self, obj=None, name=None, properties=None, is_editor_item=True, reset=True):
        """Layout properties for a python class.
        1. obj = the python class,
        2. name = name of class,
        3. properties = editor properties of this class (see editor.utils.property),
        4. is_editor_item = if this is an editor object e.g. node-path or a user module etc."""

        def get_toggle_property(parent):
            if hasattr(obj, "_PModBase__module_type"):
                if obj.module_type in [constants.RuntimeModule, constants.Component]:
                    # create a toggle property object
                    property_ = EditorProperty.FuncProperty(name="",
                                                            initial_value=obj.get_active_status(),
                                                            setter=obj.set_active,
                                                            getter=obj.get_active_status)
                    #
                    # and wrap it into wx_property object
                    wx_property = self.get_wx_property_object(property_, parent)
                    wx_property.SetBackgroundColour(parent.GetBackgroundColour())

                    wx_property.SetSize((-1, -1))
                    wx_property.SetMinSize((-1, -1))
                    wx_property.SetMaxSize((-1, -1))
                    #
                    return wx_property

            return None

        def get_object_bitmap(obj_):
            obj_type = None
            if isinstance(obj_, PModBase):
                obj_type = obj_.module_type
            elif isinstance(obj_, NodePath):
                obj_type = obj_.getPythonTag(constants.TAG_GAME_OBJECT).ed_id

            return OBJ_TYPE_ICON_MAP[obj_type]

        def get_pin_btn(parent):
            pin_btn = wx_custom.ToggleButton(parent, 0, None, image_path=PIN_ICON, image_scale=(15, 15),
                                             select_func=self.set_pinned, deselect_func=self.clear_pinned,
                                             clear_bg=True)
            return pin_btn

        def get_remove_btn(parent, btn_data):
            remove_btn = wx_custom.BasicButton(parent, 1, None, image_path=REMOVE_ICON,
                                               select_func=self.remove_component, data=btn_data, clear_bg=True)
            remove_btn.SetMinSize(wx.Size(16, 16))
            return remove_btn

        # only create inspector for scene object if inspector_type == ObjectInspector
        inspector_id = self.tab_id_tab[self.__selected_tab]
        if is_editor_item:
            if inspector_id != ID_PROPERTIES_PANEL_OBJECT_TAB:
                return
            
        self.__is_dirty = True
        self.Freeze()
    
        if reset:
            self.reset()
            self.__object = obj
            self.__label = name if name else self.__label
            self.__properties.extend(properties)
            self.__fold_manager = FoldPanelManager(self)
            self.__main_sizer.Add(self.__fold_manager, 0, wx.EXPAND, border=0)
            obj_label = self.__label[0].upper() + self.__label[1:]
        else:
            self.__properties.extend(properties)
            obj_label = name[0].upper() + name[1:]
            
        # add a fold panel for the top object
        fold_panel = self.__fold_manager.add_panel()
            
        # create pin button the first panel only
        if self.__fold_manager.get_panel_count() == 1:
            try:
                fold_panel.create_buttons(
                    label_text=obj_label,
                    toggle_btn=get_toggle_property(fold_panel.header),
                    obj_bitmap_path=get_object_bitmap(obj)[0],
                    obj_bitmap_scale=get_object_bitmap(obj)[1],
                    other_controls=[(get_pin_btn(fold_panel.header))])
            except KeyError:
                fold_panel.create_buttons(
                    label_text=obj_label,
                    toggle_btn=get_toggle_property(fold_panel.header),
                    other_controls=[(get_pin_btn(fold_panel.header))])
        else:
            if obj.module_type == constants.Component:

                fold_panel.create_buttons(
                    label_text=obj_label,
                    toggle_btn=get_toggle_property(fold_panel.header),
                    obj_bitmap_path=get_object_bitmap(obj)[0],
                    obj_bitmap_scale=get_object_bitmap(obj)[1],
                    info_bitmap=INFO_ICON if obj.get_status() == constants.SCRIPT_STATUS_ERROR else None,
                    other_controls=[(get_remove_btn(fold_panel.header, btn_data=(self.__object, obj.path)))]
                )
        #
        properties = self.create_wx_properties(properties, fold_panel)
        fold_panel.set_controls(properties)
        fold_panel.switch_expanded_state(False)
        fold_panel.Show()

        # if object is of type NodePath, then layout properties for its components as well.
        if isinstance(obj, NodePath) and not isinstance(obj, Component):
            obj_data = obj.getPythonTag(constants.TAG_GAME_OBJECT)
            for key in obj_data.components:
                comp = obj_data.components[key].class_instance

                self.layout(comp,
                            comp.module_name,
                            comp.get_properties(),
                            is_editor_item=True,
                            reset=False)

            if not self.components_dnd_panel:
                self.__main_sizer.AddSpacer(15)
                self.components_dnd_panel = BaseInspectorPanel.DragDropCompPanel(self)
                self.__main_sizer.Add(self.components_dnd_panel, 0, wx.EXPAND | wx.LEFT, border=5)

        self.Layout()
        self.__is_dirty = False
        self.Thaw()

    def mark_dirty(self):
        self.__is_dirty = True

    def on_tab_select(self, index, data=None):
        self.__selected_tab = index
        sel_tab = self.tab_id_tab[index]

        if sel_tab == ID_PROPERTIES_PANEL_OBJECT_TAB:
            self.layout_auto()
            return

        if sel_tab == ID_PROPERTIES_PANEL_WORLD_TAB:
            txt = "This section is incomplete, support PandaEditor on Patreon to help speed up its development."
            self.set_text(txt)
            return

        elif sel_tab == ID_PROPERTIES_PANEL_INSPECTOR_TAB:
            self.__object = editor.level_editor.editor_settings
            self.__label = "Editor Settings"
            self.__properties = self.__object.get_properties()
            self.layout(self.__object, self.__label, self.__properties, False)

        elif sel_tab == ID_PROPERTIES_PANEL_PLUGINS_TAB:
            txt = "This section is incomplete, support PandaEditor on Patreon to help speed up its development."
            self.set_text(txt)
            return

    def remove_component(self, idx, data):
        if editor.level_editor.get_ed_state() == GAME_STATE:
            ed_logging.log("Unable to remove component during GAME_STATE")
            return
        
        np = data[0].getPythonTag(constants.TAG_GAME_OBJECT)
        comp_path = data[1]
        np.detach_component(comp_path)
        wx.CallAfter(self.layout_auto)

    def reset(self):
        self.__object = None
        self.__label = None
        self.__properties = []
        self.property_name_map.clear()

        if self.components_dnd_panel:
            self.__main_sizer.Remove(
                len(self.__main_sizer.GetChildren()) - 2)  # remove spacer based on its position index

        # remove other panels
        for item in [self.__text_panel, self.__fold_manager, self.components_dnd_panel]:
            if item:
                self.__main_sizer.Detach(item)
                item.Destroy()

        self.Layout()

    def select_tab(self, idx):
        self.__tabs.select(idx)
        self.on_tab_select(idx)

    def set_text_from_file(self, text_file):
        """set text from a .txt file"""
        with open(text_file, "r", encoding="utf-8") as file:
            readme_text = file.read()
            self.set_text(readme_text)

    def set_text(self, text, reset=True):
        self.Freeze()
        if reset:
            self.reset()

        if type(text) == str:
            self.__text_panel = TextPanel(self, text)
            self.__text_panel.SetMinSize((self.GetSize().x - 40, self.GetSize().y - 40))
            self.__main_sizer.Add(self.__text_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
            self.Layout()

        self.Thaw()

    def set_pinned(self, *args):
        print("pinned")
        pass

    def update(self, force_update_all=False):
        """updates the selected object's properties
        label : new label if None then existing label is used
        force_update_all : """

        if self.__is_dirty:
            return

        for key in self.property_name_map.keys():
            wx_prop = self.property_name_map[key]

            # don't update these
            if wx_prop.ed_property.type_ in ["button"]:
                continue

            if not force_update_all and wx_prop.ed_property.type_ == "choice":
                continue

            # updating wx_prop control value triggers wx.EVT_TEXT, however this should only
            # trigger upon input from user so unbind it first
            wx_prop.unbind_events()

            if wx_prop.ed_property.type_ in ["horizontal_layout_group", "foldout_group", "static_box"]:
                for wx_prop_ in wx_prop.properties:
                    if not wx_prop_.has_focus():
                        wx_prop_.unbind_events()
                        wx_prop_.set_control_value(wx_prop_.ed_property.get_value())
                        wx_prop_.bind_events()
            else:
                # update the control
                if not wx_prop.has_focus():
                    wx_prop.set_control_value(wx_prop.ed_property.get_value())

            # and bind events again
            wx_prop.bind_events()

