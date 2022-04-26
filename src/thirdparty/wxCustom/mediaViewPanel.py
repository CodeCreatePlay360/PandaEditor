import wx
from wxCustom.wxCustomPanel import WxScrolledPanel, WxPanel
from constants import *


class MediaViewPanel(WxPanel):
    SELF = None

    def __init__(self, parent, label, style, color):
        WxPanel.__init__(self, parent, label, style, color)
        self.image = None
        self.image_ctrl = None
        self.max_size = -1
        MediaViewPanel.SELF = self
        self.Bind(wx.EVT_SIZE, self.on_evt_resize)

    def finish_init(self):
        self.create_layout()
        self.base_panel.SetSize(self.GetClientSize())
        self.image_ctrl = wx.StaticBitmap(self.base_panel)
        self.base_panel_sizer.Add(self.image_ctrl, 1, wx.EXPAND)

    @staticmethod
    @obs.on("image tile selected")
    def set_image_(image):
        MediaViewerPanel.SELF.image = image
        MediaViewerPanel.SELF.update_image()

    def clear_media(self):
        self.image = None
        if self.image_ctrl is not None:
            self.image_ctrl.Destroy()
            self.image_ctrl = wx.StaticBitmap(self.base_panel)
        self.Layout()

    def update_image(self):
        if self.image is None:
            return

        self.base_panel.SetSize(self.GetClientSize())
        """ Update the currently shown photo """
        image = wx.Image(self.image, type=wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        width = image.GetWidth()
        height = image.GetHeight()

        if width > height:
            self.max_size = self.base_panel.GetClientSize().x
        else:
            self.max_size = self.base_panel.GetClientSize().y

        if width > height:
            new_width = self.max_size
            new_height = self.max_size * (height / width)
        else:
            new_height = self.max_size
            new_width = self.max_size * (width / height)
        image = image.Scale(new_width, new_height)
        self.image_ctrl.SetBitmap(wx.Bitmap(image))

        self.Layout()

    def on_evt_resize(self, evt):
        super().on_evt_resize(evt)
        try:
            self.update_image()
        except AttributeError as e:
            print("error occurred, details:", e)
        evt.Skip()