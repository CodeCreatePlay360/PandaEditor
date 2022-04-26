import wx
import editor.wxUI.wxCustomProperties as wxProperty

from wx.lib.scrolledpanel import ScrolledPanel
from panda3d.core import Vec2, Vec3, LColor, LPoint3f, LVecBase3f
from editor.wxUI.wxFoldPanel import WxFoldPanelManager
from editor.colourPalette import ColourPalette as Colours


class TextPanel(wx.Panel):
    def __init__(self, parent, text, *args):
        wx.Panel.__init__(self, parent, *args)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        bold_font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        text_colour = wx.Colour(255, 255, 255, 255)

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

        self.SetBackgroundColour(Colours.NORMAL_GREY)
        self.SetWindowStyleFlag(wx.BORDER_SUNKEN)

        self.wxMain = parent

        self.property_and_type = {
            int: wxProperty.IntProperty,  # -1
            float: wxProperty.FloatProperty,  # -2
            str: wxProperty.StringProperty,  # -3
            bool: wxProperty.BoolProperty,  # -4

            # list: wxProperty.ContainerProperty,  # -5

            Vec3: wxProperty.Vector3Property,  # -6
            Vec2: wxProperty.Vector2Property,  # -7
            LColor: wxProperty.ColorProperty,  # -8

            LPoint3f: wxProperty.Vector3Property,
            LVecBase3f: wxProperty.Vector3Property,

            "label": wxProperty.LabelProperty,  # -9
            "choice": wxProperty.EnumProperty,  # -10
            "button": wxProperty.ButtonProperty,  # -11
            "slider": wxProperty.SliderProperty,  # -12
            "space": wxProperty.EmptySpace,  # -13

            "static_box": wxProperty.StaticBox,  # -14
        }

        self.property_and_name = {}
        self.selected_object = None

        self.fold_manager = None  # a FoldPanelManager for laying out variables of a python module
        self.text_panel = None  # a text_panel for displaying .txt files

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.Bind(wx.EVT_SIZE, self.on_event_size)

    def enable(self):
        print("base inspector panel enabled")
        """on enable is called as soon as this panel is added in editor"""
        if self.selected_object is not None:
            self.layout_object_properties(self.selected_object)

    def disable(self):
        print("base inspector panel disable")
        """on disable is called as soon as this panel is closed in editor"""
        pass

    def remove(self):
        print("base inspector panel removed")
        """on remove is called as soon as this panel is removed permanently"""
        pass

    def has_object(self):
        if self.selected_object is not None:
            return True
        return False

    def layout_object_properties(self, obj, name, properties):
        self.reset()

        self.selected_object = obj

        name = name[0].upper() + name[1:]

        self.fold_manager = WxFoldPanelManager(self)
        self.sizer.Add(self.fold_manager, 0, wx.EXPAND)

        fold_panel = self.fold_manager.add_panel(name)
        fold_panel.Hide()

        for prop in properties:
            prop.validate()
            if prop.is_valid:
                # get wx property object
                wx_property = self.get_wx_prop_object(prop, fold_panel)
                if wx_property:
                    # and add it to fold panel
                    fold_panel.add_control(wx_property)
            else:
                print("{0} property validation failed".format(prop.name))

        fold_panel.update_controls()
        self.fold_manager.expand(fold_panel)

        fold_panel.Show()

    def get_wx_prop_object(self, _property, parent):
        wx_property = None

        if self.property_and_type.__contains__(_property.get_type()):
            wx_property = self.property_and_type[_property.get_type()]
            wx_property = wx_property(parent, _property, h_offset=6)

            # wx_property.
            wx_property.create_control()
            wx_property.on_control_created()

            self.property_and_name[_property.get_name()] = wx_property

        return wx_property

    def update_properties_panel(self, force_update_all=False):
        for key in self.property_and_name.keys():
            wx_prop = self.property_and_name[key]

            if wx_prop.property.get_type() in ["button"]:
                continue

            if not force_update_all and wx_prop.property.get_type() is "choice":
                continue

            wx_prop.set_control_value(wx_prop.property.get_value())

    def set_text(self, text_file):
        self.reset()

        with open(text_file, "r", encoding="utf-8") as file:
            readme_text = file.read()

        self.text_panel = TextPanel(self, readme_text)
        self.text_panel.SetMinSize((self.GetSize().x - 40, self.GetSize().y - 40))

        self.sizer.Add(self.text_panel, 1, wx.EXPAND | wx.ALL, border=10)
        self.Layout()

    def refresh(self, obj=None):
        self.layout_object_properties(self.selected_object)

    def reset(self):
        self.selected_object = None
        self.property_and_name.clear()

        if self.fold_manager is not None:
            self.fold_manager.reset()
            self.fold_manager.Destroy()
            self.fold_manager = None

        if self.text_panel is not None:
            self.text_panel.Destroy()
            self.text_panel = None

        self.sizer.Clear()
        self.Layout()

    def on_event_size(self, evt):
        if self.fold_manager is not None:
            self.fold_manager.SetMinSize((self.GetSize().x - 20, self.fold_manager.get_size_y()))

        if self.text_panel is not None:
            self.text_panel.SetMinSize((self.GetSize().x - 40, self.GetSize().y - 40))

        evt.Skip()
