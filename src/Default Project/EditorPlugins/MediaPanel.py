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
        self._panel.Bind(wx.EVT_SIZE, self.on_size_event)

    def create_image_panel(self):
        self.img = wx.Image(100, 100)
        self.imageCtrl = wx.StaticBitmap(self._panel, wx.ID_ANY, wx.Image.ConvertToBitmap(self.img))

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
        self.imageCtrl.SetPosition((0, 0))

        # self.img = wx.Image(self.img_path, wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        img_width = self.img.GetSize().x
        img_height = self.img.GetSize().y

        max_width = self.imageCtrl.GetSize().x
        max_height = self.imageCtrl.GetSize().y

        ratio = min(max_width/img_width, max_height/img_height)
        new_width = img_width * ratio
        new_height = img_height * ratio

        if new_height < 1:
            new_height = 1

        if new_width < 1:
            new_width = 1

        img = self.img.Scale(new_width, new_height)
        self.imageCtrl.SetBitmap(wx.Bitmap(img))

    def on_size_event(self, evt):
        if self.imageCtrl and self.img and self.img_path:
            self.scale_image()
        evt.Skip()
