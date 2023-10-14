import os
import wx
from re import match
from wx.lib.scrolledpanel import ScrolledPanel
from editor.constants import ICONS_PATH

# constants
VERTICAL_SPLIT = 0
HORIZONTAL_SPLIT = 1

CLOSE_ICON = os.path.join(ICONS_PATH, "panel icons/close.png")


class SplitWindow:    
    def __new__(cls, label, icon, parent, base_pnl, scrolled=False, *args, **kwargs):
        """.........DOCUMENTATION NEEDS TO BE DONE........."""
        cls_properties = {
            name: getattr(cls, name) for name in dir(cls) if not match("__.*__", name)
        }
        
        if scrolled:
            self = type(cls.__name__, (ScrolledPanel,), cls_properties)(parent, *args, **kwargs)
        else:
            self = type(cls.__name__, (wx.Panel,), cls_properties)(parent, *args, **kwargs)
        
        self.__label = label
        self.__icon = icon
        self.__base_pnl = base_pnl
        
        self.__main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__main_sizer)
        
        self.__header = None
        self.__splitter = wx.SplitterWindow(self)
        
        return self
        
    def create_header(self):        
        self.__header = wx.Window(self)
        self.__header.SetBackgroundColour(wx.Colour(202, 202, 202, 255))
        self.__header.SetMaxSize(wx.Size(-1, 20))
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__header.SetSizer(header_sizer)
        # panel icon
        if self.__icon:
            xx = wx.Image(self.__icon, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            image_ctrl = wx.StaticBitmap(self.__header, wx.ID_ANY, xx)
            header_sizer.Add(image_ctrl, 0, wx.ALIGN_CENTRE | wx.LEFT, border=3)
        # window label
        self.__label_ctrl = wx.StaticText(self.__header)
        self.__label_ctrl.SetLabel(self.__label)
        header_sizer.Add(self.__label_ctrl, 1, wx.LEFT | wx.ALIGN_CENTRE, border=6)
        # close icon
        xx = wx.Image(CLOSE_ICON, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        image_ctrl = wx.StaticBitmap(self.__header, wx.ID_ANY, xx)
        header_sizer.Add(image_ctrl, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, border=6)
        # add header to main sizer
        self.__main_sizer.Add(self.__header, 0, wx.EXPAND)
        
    def split(self, direction=0, 
              panel_01=None, label_01="panel_01",
              panel_02=None, label_02="panel_02"): 

        self.__pnl_01 = SplitWindow(label_01, None, self.__splitter, self) if panel_01 is None else panel_01
        self.__pnl_02 = SplitWindow(label_02, None, self.__splitter, self) if panel_02 is None else panel_02

        if direction == VERTICAL_SPLIT:
            self.__splitter.SplitVertically(self.__pnl_01, self.__pnl_02)
        else:
            self.__splitter.SplitHorizontally(self.__pnl_01, self.__pnl_02)
                
        self.__main_sizer.Add(self.__splitter, 1, wx.EXPAND)
        return (self.__pnl_01, self.__pnl_02)
            
    def get_base_panel(self):
        return self.__base_pnl
    
    def get_header(self):
        return self.__header
    
    def get_label(self):
        return self.__label
            
    def get_panels(self):
        return [self.__pnl_01, self.__pnl_02]
    
    def get_splitter(self):
        return self.__splitter
    
    def on_close(self, evt):
        pass
