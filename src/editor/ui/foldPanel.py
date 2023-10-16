import pathlib
import wx
from editor.constants import ICONS_PATH
from editor.globals import editor

# resources
FOLD_OPEN_ICON = str(pathlib.Path(ICONS_PATH + "/folding panel/foldOpen.png"))
FOLD_CLOSE_ICON = str(pathlib.Path(ICONS_PATH + "/folding panel/foldClose.png"))

# some constants
Bitmap_offset_right = 5
Label_offset_right_0 = 20  # label offset without toggle btn
Label_offset_right_1 = 40  # label offset with toggle btn
Toggle_btn_offset_right = 7
Controls_offset_right = 18


class FoldPanel(wx.Panel):
    class HeaderPanel(wx.Window):
        def __init__(self, *args, **kwargs):
            wx.Window.__init__(self, *args, **kwargs)
            self.__parent = args[0]

            self.SetBackgroundColour(editor.ui_config.color_map("Panel_Normal"))
            self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.SetSizer(self.__sizer)

            self.open_bitmap = None
            self.close_bitmap = None
            self.__open_close_bitmap = wx.StaticBitmap(self)
            self.__sizer.Add(self.__open_close_bitmap, 0, wx.ALIGN_CENTER_VERTICAL, border=0)
            self.__sizer.AddSpacer(3)

            self.Bind(wx.EVT_LEFT_DOWN, self.on_evt_left_down)

            self.SetMinSize(wx.Size(-1, 18))
            self.SetMaxSize(wx.Size(-1, 18))

        def set_data(self, label: str, open_bitmap, close_bitmap, toggle_btn=None,
                     obj_bitmap=None, obj_bitmap_scale: tuple = None,
                     info_bitmap=None, info_bitmap_scale: tuple = None,
                     other_btns=None):

            # label control
            label_control = wx.StaticText(self)
            label_control.SetForegroundColour(editor.ui_config.color_map("Text_Secondary"))

            font = wx.Font(8, editor.ui_config.font, wx.NORMAL, wx.BOLD)
            label_control.SetFont(font)
            label_control.SetLabelText(label)

            # open close icons
            self.open_bitmap = wx.Image(open_bitmap, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            self.close_bitmap = wx.Image(close_bitmap, wx.BITMAP_TYPE_ANY).ConvertToBitmap()

            # create layout
            if toggle_btn:
                self.__sizer.Add(toggle_btn, 0, wx.ALIGN_CENTRE_VERTICAL)
                self.__sizer.AddSpacer(3)

            if info_bitmap:
                image = wx.Image(info_bitmap, wx.BITMAP_TYPE_ANY)
                if info_bitmap_scale:
                    image = image.Scale(width=info_bitmap_scale[0], height=info_bitmap_scale[1])
                info_bitmap = wx.StaticBitmap(self, 0, image.ConvertToBitmap(), (0, 0))

                self.__sizer.Add(info_bitmap, 0, wx.ALIGN_CENTER_VERTICAL, border=0)
                self.__sizer.AddSpacer(3)

            if obj_bitmap:
                image = wx.Image(obj_bitmap, wx.BITMAP_TYPE_ANY)
                if obj_bitmap_scale:
                    image = image.Scale(width=obj_bitmap_scale[0], height=obj_bitmap_scale[1])
                obj_bitmap = wx.StaticBitmap(self, -1, image.ConvertToBitmap(), (0, 0))

                self.__sizer.Add(obj_bitmap, 0, wx.ALIGN_CENTER_VERTICAL, border=0)
                self.__sizer.AddSpacer(4)

            self.__sizer.Add(label_control, 0, wx.ALIGN_CENTRE_VERTICAL)
            self.__sizer.AddStretchSpacer()

            for btn in other_btns:
                self.__sizer.Add(btn, 0, wx.ALIGN_CENTRE_VERTICAL)

            if len(other_btns) > 0:
                self.__sizer.AddSpacer(1)

        def on_open(self, open_icon_path):
            img = wx.Image(open_icon_path, wx.BITMAP_TYPE_ANY)
            img = img.Scale(15, 15)
            self.__open_close_bitmap.SetBitmap(img.ConvertToBitmap())

        def on_close(self, close_icon_path):
            img = wx.Image(close_icon_path, wx.BITMAP_TYPE_ANY)
            img = img.Scale(15, 15)
            self.__open_close_bitmap.SetBitmap(img.ConvertToBitmap())

        def on_evt_left_down(self, evt):
            self.__parent.switch_expanded_state()
            evt.Skip()

    def __init__(self, fold_manager):
        wx.Panel.__init__(self, fold_manager)
        self.SetBackgroundColour(editor.ui_config.color_map("Panel_Dark"))
        self.fold_manager = fold_manager

        self.__controls_in_sizer = False
        self.__expanded = False  # is expanded ?
        self.__wx_properties = []  # list of all controls in this sizer

        self.__v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__v_sizer)

        self.header = FoldPanel.HeaderPanel(self)
        self.__v_sizer.Add(self.header, 1, wx.EXPAND | wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.RESERVE_SPACE_EVEN_IF_HIDDEN, 1)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.__has_end_spacer = False

    def get_properties(self):
        return self.__wx_properties

    def set_controls(self, wx_properties: list):
        for prop in self.__wx_properties:
            prop.Destroy()
        self.__wx_properties.clear()
        self.__wx_properties = wx_properties

    def create_buttons(self, label_text,
                       obj_bitmap_path=None, obj_bitmap_scale=None,
                       info_bitmap=None, info_bitmap_scale=None,
                       toggle_btn=None,
                       other_controls=None):

        self.header.set_data(label=label_text, open_bitmap=FOLD_OPEN_ICON, close_bitmap=FOLD_CLOSE_ICON,
                             toggle_btn=toggle_btn, obj_bitmap=obj_bitmap_path, obj_bitmap_scale=obj_bitmap_scale,
                             info_bitmap=info_bitmap, info_bitmap_scale=info_bitmap_scale,
                             other_btns=other_controls)

    def update_controls(self, show=True):
        # self.SetMinSize(wx.Size(-1, -1))

        for i in range(len(self.__wx_properties)):
            control = self.__wx_properties[i]
            if show:
                if not self.__controls_in_sizer:
                    self.__v_sizer.Add(control, 0, wx.EXPAND | wx.LEFT, border=5)

                    if i == len(self.__wx_properties) - 1:
                        self.__v_sizer.AddSpacer(1)
                        self.__has_end_spacer = True

                control.Show()
            else:
                self.__v_sizer.Detach(control)
                control.Hide()

                if self.__has_end_spacer:
                    count = self.__v_sizer.GetItemCount()
                    self.__v_sizer.Remove(count - 1)
                    self.__has_end_spacer = False

        # self.SetMinSize(wx.Size(-1, self.GetBestSize().y))
        self.__controls_in_sizer = show

    def switch_expanded_state(self, state=None):
        if state:
            self.__expanded = state
        self.Freeze()
        if not self.__expanded:
            # if closed, open
            self.update_controls(True)
            self.__expanded = True
            self.fold_manager.on_panel_foldout(self)
            # change graphics to fold open
            self.header.on_open(FOLD_OPEN_ICON)
        else:
            # if open, close
            self.update_controls(False)
            self.__expanded = False
            self.fold_manager.on_panel_foldout(self)
            # change graphics to fold close
            self.header.on_close(FOLD_CLOSE_ICON)

        self.Thaw()

    def clear(self):
        for control in self.__wx_properties:
            control.Hide()
        self.__wx_properties.clear()

    def on_paint(self, evt):
        pdc = wx.PaintDC(self)
        gc = wx.GCDC(pdc)

        gc.SetPen(wx.Pen(wx.Colour(150, 150, 150, 255), 1))
        gc.DrawLine(wx.Point(0, 0), wx.Point(self.GetSize().x, 0))  # top
        gc.DrawLine(wx.Point(0, self.GetBestSize().y - 1),
                    wx.Point(self.GetSize().x, self.GetBestSize().y - 1))  # bottom
        gc.DrawLine(wx.Point(0, 0), wx.Point(0, self.GetSize().y))  # left
        gc.DrawLine(wx.Point(self.GetSize().x, 0), wx.Point(self.GetSize().x, self.GetSize().y))  # right


class FoldPanelManager(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.__panels = []
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)

    def add_panel(self):
        panel = FoldPanel(self)

        if self.get_panel_count() > 0:
            self.__sizer.AddSpacer(4)

        self.__sizer.Add(panel, 0, wx.EXPAND | wx.LEFT, border=5)
        self.__panels.append(panel)
        return panel

    def on_panel_foldout(self, panel):
        self.GetParent().Layout()
        self.PostSizeEventToParent()
        self.Refresh()

    def get_panels(self):
        return self.__panels

    def get_panel_count(self):
        return len(self.__panels)

