import wx
from editor.colourPalette import ColourPalette as Colours
from editor.constants import ICONS_PATH


PANEL_FOLD_SIZE = 24.0
LEFT_PADDING = 8

FOLD_OPEN_ICON = ICONS_PATH + "\\" + "foldOpen_16.png"
FOLD_CLOSE_ICON = ICONS_PATH + "\\" + "foldClose_16.png"


class WxFoldPanel(wx.Panel):
    def __init__(self, fold_manager, label, *args, **kwargs):
        wx.Panel.__init__(self, fold_manager)
        
        self.SetWindowStyleFlag(wx.BORDER_SIMPLE)
        self.SetBackgroundColour(wx.Colour(Colours.DARK_GREY))
        
        self.fold_manager = fold_manager
        
        # load text resources
        self.font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.text_colour = wx.Colour(255, 255, 255, 255)
        
        # load fold open and close icons resources
        bitmap_image = wx.Image(FOLD_OPEN_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.fold_open_icon = wx.StaticBitmap(self, -1, bitmap_image, (8, 3))
        
        bitmap_image = wx.Image(FOLD_CLOSE_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.fold_close_icon = wx.StaticBitmap(self, -1, bitmap_image, (6, 3))
        self.fold_close_icon.Hide()
        
        self.label = wx.StaticText(self, label=label)
        self.label.SetFont(self.font)
        self.label.SetForegroundColour(self.text_colour)
        self.label.SetPosition(wx.Point(LEFT_PADDING+18, 3))
        
        self.controls = []
        self.excluded_controls = []
        self.expanded = False
        
        self.x_space = 0
        self.y_space = 0

        self.max_y_space = 0
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.on_evt_clicked)
        self.Bind(wx.EVT_SIZE, self.on_evt_size)
        
    def add_control(self, _property):
        self.controls.append(_property)

    def update_controls(self, shown=True):
        panel_height = 0
        self.max_y_space = 0

        x_space = 0
        y_space = 0

        for control in self.controls:
            if control.get_type() == "space":
                x_space += control.get_x()
                y_space += control.get_y()
                self.max_y_space += control.get_y()
                continue

            control.SetSize(self.GetSize().x-16, control.GetSize().y)
            control.SetPosition(wx.Point(LEFT_PADDING, panel_height + PANEL_FOLD_SIZE + y_space))
            panel_height += control.GetSize().y

            if shown is True:
                control.Show()
            elif shown is False:
                control.Hide()

    def switch_expanded_state(self, state=None):
        if state is None:
            self.expanded = self.expanded
        else:
            self.expanded = state

        if not self.expanded:
            # if fold panel is closed
            if len(self.controls) > 0:
                self.fold_manager.expand(self)
                self.update_controls(True)

            self.expanded = True
            # change graphics to fold open
            self.fold_open_icon.Show()
            self.fold_close_icon.Hide()
        else:
            # else if it's open
            self.update_controls(False)
            self.fold_manager.collapse(self)
            self.expanded = False
            # change graphics to fold close
            self.fold_open_icon.Hide()
            self.fold_close_icon.Show()

    def clear(self):
        for control in self.controls:
            control.Hide()
        self.controls.clear()

    def get_expanded_size(self):
        if len(self.controls) == 0:
            return 0

        size = 0
        for ctrl in self.controls:
            if ctrl in self.excluded_controls or ctrl.get_type() == "space":
                continue
            size += ctrl.GetSize().y

        size += self.max_y_space
        return size + 5

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

    def add_panel(self, name=""):
        panel = WxFoldPanel(self, name)
        # panel.SetBackgroundColour(wx.Colour(50, 50, 50, 255))
        panel.SetSize(self.GetSize().x, PANEL_FOLD_SIZE)
        if len(self.panels) == 0:
            panel.SetPosition(wx.Point(0, 0))
        else:
            panel.SetPosition(wx.Point(0, PANEL_FOLD_SIZE*len(self.panels)))

        self.panels.append(panel)
        return panel

    def expand(self, panel):
        x = False
        self.size_y = 0
        
        for _panel in self.panels:
            if _panel == panel:
                panel.SetSize(self.GetSize().x, _panel.get_expanded_size()+24)
                self.size_y = panel.GetSize().y
                panel.expanded = True
                x = True
                continue
            
            if x is True:
                _panel.SetPosition(wx.Point(0, _panel.GetPosition().y+50.0-PANEL_FOLD_SIZE))
                
        self.SetMinSize((self.parent.GetSize().x-20, self.size_y))
        self.parent.SetupScrolling(scroll_x=False)

    def get_size_y(self):
        return self.size_y

    def collapse(self, panel):
        x = False
        for _panel in self.panels:
            if _panel == panel:
                panel.SetSize(self.GetSize().x, PANEL_FOLD_SIZE)
                x = True
                continue
            if x is True:
                _panel.SetPosition(wx.Point(0, _panel.GetPosition().y-PANEL_FOLD_SIZE-2))
                
        self.Layout()
        # self.Refresh()

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
