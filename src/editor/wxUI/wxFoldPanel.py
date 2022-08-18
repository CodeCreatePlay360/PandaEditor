import wx
import editor.edPreferences as edPreferences
from editor.constants import ICONS_PATH

Panel_Fold_size = 23.0

Bitmap_offset_right = 5
Label_offset_right_0 = 20  # label offset without toggle btn
Label_offset_right_1 = 40  # label offset with toggle btn
Toggle_btn_offset_right = 7
Controls_offset_right = 18

FOLD_OPEN_ICON = ICONS_PATH + "\\" + "foldOpen_16.png"
FOLD_CLOSE_ICON = ICONS_PATH + "\\" + "foldClose_16.png"

Debug_Mode = False  # debug mode add a small separation of 0.2 between two vertical adjacent controls


class WxFoldPanel(wx.Panel):
    def __init__(self, fold_manager, label, toggle_property=None, *args, **kwargs):
        wx.Panel.__init__(self, fold_manager)

        self.SetWindowStyleFlag(wx.BORDER_SIMPLE)
        self.SetBackgroundColour(wx.Colour(edPreferences.Colors.Panel_Dark))

        self.fold_manager = fold_manager
        self.toggle_property = toggle_property
        self.label = label

        # load text resources
        self.font = wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.text_colour = edPreferences.Colors.Bold_Label

        self.fold_open_icon = None
        self.fold_close_icon = None
        self.label_control = None
        # self.create_buttons()

        self.wx_properties = []
        self.expanded = False

        self.x_space = 0
        self.y_space = 0

        self.max_y_space = 0

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_evt_clicked)
        self.Bind(wx.EVT_SIZE, self.on_evt_size)

    def add_control(self, _property):
        self.wx_properties.append(_property)

    def create_buttons(self):
        # set panel open and close icons
        bitmap_image = wx.Image(FOLD_OPEN_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.fold_open_icon = wx.StaticBitmap(self, -1, bitmap_image, (Bitmap_offset_right, 5), size=wx.Size(10, 10))

        bitmap_image = wx.Image(FOLD_CLOSE_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.fold_close_icon = wx.StaticBitmap(self, -1, bitmap_image, (Bitmap_offset_right, 5), size=wx.Size(10, 10))
        self.fold_close_icon.Hide()

        # create toggle property
        if self.toggle_property:
            # self.toggle = wx.CheckBox(self, label="", style=0)
            self.toggle_property.SetSize(60, 20)
            self.toggle_property.SetPosition((Toggle_btn_offset_right, -2))
            self.toggle_property.SetBackgroundColour(self.GetBackgroundColour())

        label_offset = Label_offset_right_0 if not self.toggle_property else Label_offset_right_1
        self.label_control = wx.StaticText(self, label=self.label)
        self.label_control.SetFont(self.font)
        self.label_control.SetForegroundColour(self.text_colour)
        self.label_control.SetPosition(wx.Point(label_offset, 2))

    def set_toggle_property(self, toggle_property):
        self.toggle_property = toggle_property

    def update_controls(self, shown=True):
        panel_height = 0
        self.max_y_space = 0

        x_space = 0
        y_space = 0
        i = 0

        for control in self.wx_properties:
            if control.get_type() == "space":
                x_space += control.get_x()
                y_space += control.get_y()
                self.max_y_space += control.get_y()
                continue

            i += (0 if not Debug_Mode else 1)
            debug_offset = i * 1.02

            control.SetSize(self.GetSize().x - 16, control.GetSize().y)

            control_pos = wx.Point(Controls_offset_right, Panel_Fold_size + panel_height + y_space + debug_offset)
            control.SetPosition(control_pos)

            panel_height += control.GetSize().y

            if shown is True:
                control.Show()
            elif shown is False:
                control.Hide()

    def switch_expanded_state(self, state=None):
        if state:
            self.expanded = state

        if not self.expanded:  # if closed
            self.fold_manager.expand(self)
            self.update_controls(True)
            self.expanded = True

            # change graphics to fold open
            self.fold_open_icon.Show()
            self.fold_close_icon.Hide()

        else:  # if open
            self.update_controls(False)
            self.fold_manager.collapse(self)
            self.expanded = False

            # change graphics to fold close
            self.fold_open_icon.Hide()
            self.fold_close_icon.Show()

    def clear(self):
        for control in self.wx_properties:
            control.Hide()
        self.wx_properties.clear()

    def get_expanded_size(self):
        if len(self.wx_properties) == 0:
            return Panel_Fold_size

        size = 0
        for prop in self.wx_properties:
            if prop.get_type() == "space":
                size += prop.get_y()
            else:
                size += prop.GetSize().y + (0 if not Debug_Mode else 1.02)

        size += 30
        return size

    def on_evt_clicked(self, evt):
        self.switch_expanded_state()
        evt.Skip()

    def on_evt_size(self, evt):
        self.update_controls()
        evt.Skip()


class WxFoldPanelManager(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.SetBackgroundColour(wx.Colour(100, 100, 100, 255))
        self.panels = []

        self.parent = args[0]
        self.size_y = 0

        self.Bind(wx.EVT_SIZE, self.on_event_size)

    def add_panel(self, name="", toggle_property=None, create_buttons=True):
        panel = WxFoldPanel(self, name, toggle_property)
        if create_buttons:
            panel.create_buttons()

        panel.SetSize(self.GetSize().x, Panel_Fold_size)
        if len(self.panels) == 0:
            panel.SetPosition(wx.Point(0, 0))
        else:
            panel.SetPosition(wx.Point(0, Panel_Fold_size * len(self.panels)))

        self.panels.append(panel)
        return panel

    def expand(self, panel):
        self.size_y = 0

        for _panel in self.panels:
            if _panel == panel:
                panel.SetSize(self.GetSize().x, _panel.get_expanded_size())
                self.size_y = panel.GetSize().y
                panel.expanded = True

        self.SetMinSize((self.parent.GetSize().x - 20, self.size_y + 2))
        self.parent.SetupScrolling(scroll_x=False)

    def collapse(self, panel):
        for _panel in self.panels:
            if _panel == panel:
                panel.SetSize(self.GetSize().x, Panel_Fold_size)
                self.size_y = panel.GetSize().y

        self.SetSize((self.GetSize().x, self.size_y + 2))
        self.Layout()

    def refresh(self):
        for panel in self.panels:
            self.collapse(panel)
        for panel in self.panels:
            self.expand(panel)

        self.Layout()

    def reset(self):
        for panel in self.panels:
            panel.Hide()
            panel.clear()
            panel.SetSize(self.GetSize().x, panel.GetSize().y)
        self.panels.clear()

    def on_event_size(self, evt):
        for panel in self.panels:
            panel.SetSize(self.GetSize().x, panel.GetSize().y)
        evt.Skip()
