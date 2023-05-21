import sys
import pathlib
import wx
import editor.edPreferences as edPreferences
from editor.constants import ICONS_PATH

Bitmap_offset_right = 5
Label_offset_right_0 = 20  # label offset without toggle btn
Label_offset_right_1 = 40  # label offset with toggle btn
Toggle_btn_offset_right = 7
Controls_offset_right = 18

FOLD_OPEN_ICON = str(pathlib.Path(ICONS_PATH + "/foldOpen_16.png"))
FOLD_CLOSE_ICON = str(pathlib.Path(ICONS_PATH + "/foldClose_16.png"))


class FoldPanel(wx.Panel):
    def __init__(self, fold_manager, label):
        wx.Panel.__init__(self, fold_manager)
        self.SetBackgroundColour(wx.Colour(edPreferences.Colors.Panel_Dark))

        self.fold_manager = fold_manager

        # label font and color
        self.__label = label
        self.font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.text_colour = edPreferences.Colors.Bold_Label

        self.fd_control = None  # foldout open and close button
        self.label_control = None  # label control

        self.__controls_in_sizer = False
        self.expanded = False  # is expanded ?
        self.wx_properties = []  # list of all controls in this sizer

        self.fd_open_icon = wx.Image(FOLD_OPEN_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.fd_close_icon = wx.Image(FOLD_CLOSE_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap()

        self.v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.v_sizer.Add(self.h_sizer, 0, wx.EXPAND)
        self.SetSizer(self.v_sizer)

        self.Bind(wx.EVT_LEFT_DOWN, self.on_evt_left_down)
        self.Bind(wx.EVT_SIZE, self.on_evt_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, value):
        self.label_control.SetLabel(value)
        self.__label = value

    def add_control(self, _property):
        self.wx_properties.append(_property)

    def set_controls(self, controls: list):
        for prop in self.wx_properties:
            prop.Destroy()
        self.wx_properties.extend(controls)

    def create_buttons(self,
                       toggle_btn=None,
                       info_bitmap_path=None, info_bitmap_args: tuple = (),
                       obj_bitmap_path=None, obj_bitmap_args: tuple = (),
                       other_controls=None):
        """Create buttons for this panel,
        toggle_btn=a toggle button after label control,
        info_bitmap_path=an optional warning on info bitmap path ib case is something is not ok,
        info_bitmap_args=arguments for placing info_bitmap_control in a wx-box-sizer, args[0]=flags, args[1]=border,
        object_bitmap_path=bitmap for this particular object,
        obj_bitmap_args=arguments when placing obj_bitmap_control in a wx-box-sizer, args[0]=flags, args[1]=border,
        other_controls = a list of other controls placed on far right side of panel, should be in format
        [(control, sizer_flags, border),....,]"""

        if other_controls is None:
            other_controls = []
        self.h_sizer.AddSpacer(4)

        # open and close icon bitmaps
        self.fd_control = wx.StaticBitmap(self, -1, self.fd_close_icon, (0, 0))

        # add bitmap controls to sizer
        self.h_sizer.AddSpacer(2)
        border = 3 if sys.platform == "linux" else 2
        self.h_sizer.Add(self.fd_control, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, border=border)
        self.h_sizer.AddSpacer(2)

        # toggle button
        if toggle_btn:
            if sys.platform == "linux":
                self.h_sizer.Add(toggle_btn, 0, wx.EXPAND | wx.TOP, border=1)
                self.h_sizer.AddSpacer(4)
            else:
                self.h_sizer.Add(toggle_btn, 0, wx.EXPAND | wx.TOP, border=1)
                self.h_sizer.AddSpacer(3)
        else:
            self.h_sizer.AddSpacer(2)

        # info bitmap
        if info_bitmap_path:
            img = wx.Image(info_bitmap_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            obj_bitmap = wx.StaticBitmap(self, -1, img, (0, 0))
            flags = info_bitmap_args[0]
            border = info_bitmap_args[1]
            self.h_sizer.Add(obj_bitmap, 0, flags, border=border)
            self.h_sizer.AddSpacer(2)

        # object bitmap
        if obj_bitmap_path:
            bitmap = wx.Image(obj_bitmap_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            obj_bitmap = wx.StaticBitmap(self, -1, bitmap, (0, 0))
            flags = obj_bitmap_args[0]
            border = obj_bitmap_args[1]
            self.h_sizer.Add(obj_bitmap, 0, flags, border=border)
            self.h_sizer.AddSpacer(4)

        # label
        self.label_control = wx.StaticText(self, label=self.__label)
        self.label_control.SetFont(self.font)
        self.label_control.SetForegroundColour(self.text_colour)

        # add label control to sizer
        border = 6 if sys.platform == "linux" else 4
        self.h_sizer.Add(self.label_control, 0, wx.EXPAND | wx.TOP, border=border)

        if len(other_controls) > 0:
            self.h_sizer.AddStretchSpacer()

        for ctrl, flags, border in other_controls:
            self.h_sizer.Add(ctrl, 0, flags, border)

        self.v_sizer.Layout()

    def update_controls(self, show=True):
        self.SetMinSize(wx.Size(-1, -1))

        layout = False
        for i in range(len(self.wx_properties)):
            control = self.wx_properties[i]
            if show:
                if not self.__controls_in_sizer:
                    self.v_sizer.Add(control, 0, wx.EXPAND | wx.LEFT, border=6)
                control.Show()
                layout = True
            else:
                self.v_sizer.Detach(control)
                control.Hide()
                layout = False

        self.SetMinSize(wx.Size(-1, self.GetBestSize().y+1))
        self.__controls_in_sizer = layout

    def switch_expanded_state(self, state=None):
        if state:
            self.expanded = state
        self.Freeze()
        if not self.expanded:
            # if closed, open
            self.update_controls(True)
            self.expanded = True
            self.fold_manager.on_panel_foldout(self)
            # change graphics to fold open
            self.fd_control.SetBitmap(self.fd_open_icon)
        else:
            # if open, close
            self.update_controls(False)
            self.expanded = False
            self.fold_manager.on_panel_foldout(self)
            # change graphics to fold close
            self.fd_control.SetBitmap(self.fd_close_icon)
            self.SetMinSize(wx.Size(-1, -1))
        self.Thaw()

    def clear(self):
        for control in self.wx_properties:
            control.Hide()
        self.wx_properties.clear()

    def on_evt_left_down(self, evt):
        self.switch_expanded_state()
        evt.Skip()

    def on_evt_size(self, evt):
        self.update_controls(self.expanded)
        self.Refresh()
        evt.Skip()

    def on_paint(self, evt):
        pdc = wx.PaintDC(self)
        gc = wx.GCDC(pdc)

        gc.SetPen(wx.Pen(wx.Colour(150, 150, 150, 255), 1))
        gc.SetBrush(wx.Brush(wx.Colour(edPreferences.Colors.Panel_Normal)))
        # gc.DrawRectangle(0+12, 0, self.GetSize().x, self.GetSize().y)

        gc.DrawLine(wx.Point(6, 0), wx.Point(self.GetSize().x, 0))  # top
        gc.DrawLine(wx.Point(6, self.GetSize().y-1), wx.Point(self.GetSize().x, self.GetSize().y-1))  # bottom
        gc.DrawLine(wx.Point(5, 0), wx.Point(5, self.GetSize().y))  # left
        gc.DrawLine(wx.Point(self.GetSize().x, 0), wx.Point(self.GetSize().x, self.GetSize().y))  # right


class FoldPanelManager(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.__parent = args[0]
        self.__panels = []
        self.__sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(self.__sizer)

    def add_panel(self, name=""):
        panel = FoldPanel(self, name)

        if self.panel_count > 0:
            self.__sizer.Add(panel, 0, wx.EXPAND | wx.TOP, border=5)
        else:
            self.__sizer.Add(panel, 0, wx.EXPAND, border=0)

        self.__panels.append(panel)
        return panel

    def on_panel_foldout(self, panel):
        self.__parent.Layout()
        self.PostSizeEventToParent()
        self.Refresh()

    @property
    def panel_count(self):
        return len(self.__panels)

    @property
    def sizer(self):
        return self.__sizer
