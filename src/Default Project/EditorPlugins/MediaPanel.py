import os
import wx
import math
import panda3d.core as p3d_core

from editor.core.editorPlugin import EditorPlugin


class MediaPanel(EditorPlugin):
    def __init__(self, *args, **kwargs):
        EditorPlugin.__init__(self, *args, **kwargs)
        # __init__ should not contain anything except for variable declaration...!

        self.imageCtrl = None
        self.img = None
        self.sizer = None
        self.img_path = None

        self.request_unique_panel("MediaPanel")

    def on_start(self):
        # this method is called only once
        self.create_ui()

    def on_update(self):
        # this method is called evert frame
        if self._globals.selected_resource_item:
            self.set_image(self._globals.selected_resource_item)

    def create_ui(self):
        self.create_image_panel()

    def create_image_panel(self):
        img = wx.Image(240, 240)
        self.imageCtrl = wx.StaticBitmap(self._panel, wx.ID_ANY, wx.Image.ConvertToBitmap(img))

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.imageCtrl, 0, wx.ALL | wx.EXPAND, 5)

        self._panel.SetSizer(self.sizer)
        self._panel.Layout()

    def set_image(self, filepath):
        # make sure to only call this function once
        if self.img_path == filepath:
            return
        else:
            self.img_path = filepath

        path, ext = os.path.splitext(filepath)

        if ext in [".jpg", ".png"]:
            self.img = wx.Image(filepath, wx.BITMAP_TYPE_ANY)
            self.scale_image()

    def scale_image(self):
        """scale the image preserving the aspect ratio"""

        if self._panel.GetSize().x < 5 or self._panel.GetSize().y < 5:
            return

        self.imageCtrl.SetSize((self._panel.GetSize().x, self._panel.GetSize().y))

        # scale the image, preserving the aspect ratio
        image_width = self.img.GetWidth()
        image_height = self.img.GetHeight()

        if image_width > image_height:
            new_width = self.imageCtrl.GetSize().x
            new_height = self.imageCtrl.GetSize().y * image_height / image_width
        else:
            new_height = self.imageCtrl.GetSize().y
            new_width = self.imageCtrl.GetSize().x * image_width / image_height

        img = self.img.Scale(new_width, new_height)
        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self._panel.Refresh()

    def on_resize_event(self):
        if self.imageCtrl and self.img:
            self.scale_image()
