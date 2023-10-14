import sys, os
import wx

path = os.path.dirname(os.getcwd())
sys.path.append(path)

from splitwindow import SplitWindow, VERTICAL_SPLIT, HORIZONTAL_SPLIT

FOLDER_ICON = "folder_16x.png"


class SceneBrowser(SplitWindow):
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self.SetBackgroundColour(wx.Colour(100, 100, 200, 255))
        return self


class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Split Window Test")
        self.Maximize(True)
        
        self.base_panel = SplitWindow("BasePanel", None, self, None)
        
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.__sizer.Add(self.base_panel, 1, wx.EXPAND)
        self.SetSizer(self.__sizer)
        
        wx.CallAfter(self.initialize_windows)
        
    def initialize_windows(self):        
        top_pnl, btm_pnl = self.base_panel.split(direction=HORIZONTAL_SPLIT)
        
        scene_browser = SceneBrowser("Scene Browser", FOLDER_ICON, top_pnl.get_splitter(), top_pnl)

        scene_browser, right_pnl = top_pnl.split(direction=VERTICAL_SPLIT, 
                                                 panel_01=scene_browser,
                                                 label_01="Scene Browser")
                                          
        viewport, properties_pnl =  right_pnl.split(direction=VERTICAL_SPLIT, 
                                                    label_01="Viewport",
                                                    label_02="Properties Panel")
        
        console_pnl, resource_pnl = btm_pnl.split(direction=VERTICAL_SPLIT, 
                                                  label_01="Console Panel",
                                                  label_02="Resource Browser")
                                                  
        
        # create headers for all panels except base panels
        scene_browser.create_header()
        viewport.create_header()
        properties_pnl.create_header()
        console_pnl.create_header()
        resource_pnl.create_header()
        
        # update sizes
        x, y = self.base_panel.GetSize()
        self.base_panel.get_splitter().SetSashPosition(y/1.5)
        top_pnl.get_splitter().SetSashPosition(x/6)
        right_pnl.get_splitter().SetSashPosition(x/1.65)
        btm_pnl.get_splitter().SetSashPosition(x/3)
        
        self.Layout()


# Run the program
if __name__ == "__main__":    
    app = wx.App(False)
    frame = Frame()
    frame.Show()
    app.MainLoop()
        