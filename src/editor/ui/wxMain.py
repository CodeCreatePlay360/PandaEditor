import pathlib
import sys
import wx
import wx.aui
import wx.lib.agw.aui as aui
import editor.ui.splitwindow as splitwindow

from direct.showbase.ShowBase import taskMgr
from editor.ui.menuBar import MenuBar
from editor.ui.panels import *
from editor.ui.custom import BasicButton
from editor.constants import ICONS_PATH
from editor.globals import editor


# scene events
Evt_Open_Project = wx.NewId()
Evt_New_Scene = wx.NewId()
Evt_Open_Scene = wx.NewId()
Evt_Save_Scene = wx.NewId()
Evt_Save_Scene_As = wx.NewId()
Evt_Append_Library = wx.NewId()

# editor events
Evt_Refresh = wx.NewId()

# toolbar events
Evt_Ed_Viewport_style = wx.NewId()
Evt_Play = wx.NewId()
Evt_Toggle_Scene_Lights = wx.NewId()
Evt_Toggle_Sounds = wx.NewId()

# ui panel events
EVT_CLOSE_PAGE = wx.NewId()

Event_Map = {
    Evt_Open_Project: ("OpenProject", None),
    Evt_New_Scene: ("CreateNewSession", None),
    Evt_Open_Scene: ("OpenSession", None),
    Evt_Save_Scene: ("SaveSession", None),
    Evt_Save_Scene_As: ("SaveSessionAs", None),
    Evt_Append_Library: ("AppendLibrary", None),

    Evt_Refresh: ("ReloadEditor", None),

    Evt_Ed_Viewport_style: ("SwitchEdViewportStyle", None),
    Evt_Play: ("SwitchEdState", None),
    Evt_Toggle_Scene_Lights: ("ToggleSceneLights", None),
    Evt_Toggle_Sounds: ("ToggleSounds", None)
}

# resources
# panda editor icon file
ICON_FILE = str(pathlib.Path(ICONS_PATH + "/pandaIcon.ico"))
#
# status bar icons
NEW_SESSION_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/fileNew_32.png"))
OPEN_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/fileOpen_32.png"))
SAVE_SESSION_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/fileSave_32.png"))
SAVE_SESSION_AS_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/fileSaveAs_32.png"))
#
PROJ_OPEN_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/fileOpen_32.png"))
IMPORT_LIBRARY_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/package_link.png"))
IMPORT_PACKAGE_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/add_package.png"))
OPEN_STORE_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/shop_network.png"))
#
ALL_LIGHTS_ON_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/lightbulb_32x_on.png"))
ALL_LIGHTS_OFF_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/lightbulb_32x_off.png"))
SOUND_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/soundIcon.png"))
NO_SOUND_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/noSoundIcon.png"))
#
ED_REFRESH_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/Refresh_Icon_32.png"))
#
ED_MODE_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/game_mode.png"))
PLAY_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/playIcon_32x.png"))
STOP_ICON = str(pathlib.Path(ICONS_PATH + "/tool bar/stopIcon_32.png"))
#
# notebook page icons
VIEWPORT_ICON = str(pathlib.Path(ICONS_PATH + "/panel icons/image_16x.png"))
INSPECTOR_ICON = str(pathlib.Path(ICONS_PATH + "/panel icons/gear_16x.png"))
CONSOLE_ICON = str(pathlib.Path(ICONS_PATH + "/panel icons/monitor_16x.png"))
RESOURCE_BROWSER = str(pathlib.Path(ICONS_PATH + "/panel icons/folder_16x.png"))
SCENE_GRAPH_ICON = str(pathlib.Path(ICONS_PATH + "/panel icons/structure_16x.png"))
#
# status bar icons
REFRESH_ICON = str(pathlib.Path(ICONS_PATH + "/status bar/arrow_refresh.png"))
#
# other icons
DISABLED_ICON = str(pathlib.Path(ICONS_PATH + "/disabled_icon.png"))
SELECT_ICON = str(pathlib.Path(ICONS_PATH + "/hand_point_090.png"))


class WxFrame(wx.Frame):
    class StatusPanel(wx.Panel):
        class InfoPanel(wx.Window):
            def __init__(self, *args, **kwargs):
                wx.Window.__init__(self, *args, **kwargs)
                self.SetBackgroundColour(editor.ui_config.color_map("Panel_Normal"))

                font = wx.Font(8, editor.ui_config.font, wx.NORMAL, wx.NORMAL)

                self.bg_tasks_text_ctrl = wx.StaticText(self)
                self.bg_tasks_text_ctrl.SetBackgroundColour(editor.ui_config.color_map("Panel_Normal"))
                self.bg_tasks_text_ctrl.SetForegroundColour(wx.Colour(225, 225, 225, 255))
                self.bg_tasks_text_ctrl.SetFont(font)
                self.bg_tasks_text_ctrl.SetLabelText("[PandaEditor]")
                #
                self.selected_item_text_info = wx.StaticText(self)
                self.selected_item_text_info.SetBackgroundColour(editor.ui_config.color_map("Panel_Normal"))
                self.selected_item_text_info.SetForegroundColour(wx.Colour(225, 225, 225, 255))
                self.selected_item_text_info.SetFont(font)
                self.selected_item_text_info.SetLabelText("(Selected item info: no info available)")

                sizer = wx.BoxSizer(wx.HORIZONTAL)
                self.SetSizer(sizer)

                border = 2 if sys.platform == "linux" else 1
                sizer.Add(self.bg_tasks_text_ctrl, 0, wx.EXPAND | wx.TOP, border=border)
                sizer.AddSpacer(2)
                sizer.Add(self.selected_item_text_info, 0, wx.EXPAND | wx.TOP, border=border)

        def __init__(self, *args):
            wx.Panel.__init__(self, *args)
            # self.SetWindowStyleFlag(wx.SUNKEN_BORDER)
            self.SetBackgroundColour(editor.ui_config.color_map("Panel_Dark"))
            self.SetMaxSize((-1, 16))
            self.parent = args[0]
            #
            self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.SetSizer(self.main_sizer)
            #
            self.refresh_btn = self.create_refresh_btn()
            #
            self.info_panel = WxFrame.StatusPanel.InfoPanel(self)
            #
            self.main_sizer.Add(self.refresh_btn, 0, wx.EXPAND | wx.RIGHT, border=1)
            self.main_sizer.Add(self.info_panel, 0, border=0)
            self.main_sizer.Layout()

        def create_refresh_btn(self):
            refresh_btn = BasicButton(self,
                                      0,
                                      label_text=None,
                                      image_path=REFRESH_ICON,
                                      image_flags=wx.EXPAND | wx.RIGHT,
                                      image_border=3)
            refresh_btn.SetWindowStyleFlag(wx.BORDER_SIMPLE)
            return refresh_btn

        def write_tasks_info(self, count):
            # bg running tasks info
            info = "(Background running tasks count = {0})".format(len(taskMgr.getAllTasks()))
            self.info_panel.bg_tasks_text_ctrl.SetLabelText(info)
            self.main_sizer.Layout()

        def write_selected_item_info(self):
            self.main_sizer.Layout()

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.panda_app = wx.GetApp()
        
        # set the application icon
        icon_file = ICON_FILE
        icon = wx.Icon(icon_file, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.load_resources()
        #
        # menu bar
        self.__menu_bar = MenuBar(self)
        self.SetMenuBar(self.__menu_bar)
        #
        self.status_panel = WxFrame.StatusPanel(self)
        # main sizer
        self.__main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__main_sizer)
        
        # initialize the different UI windows
        self.__base_panel = splitwindow.SplitWindow("BasePanel", None, self, None)
        
        top_pnl, btm_pnl = self.__base_panel.split(direction=splitwindow.HORIZONTAL_SPLIT)
        scenegraph = SceneBrowserPanel("Scene Browser", SCENE_GRAPH_ICON, top_pnl.get_splitter(), top_pnl)

        scenegraph_, right_pnl = top_pnl.split(direction=splitwindow.VERTICAL_SPLIT, 
                                                 panel_01=scenegraph,
                                                 label_01="Scene Browser")  
        
        self.ed_viewport_panel = Viewport("Viewport", VIEWPORT_ICON, right_pnl.get_splitter(), right_pnl)
        self.inspector_panel = InspectorPanel("Properties Panel", INSPECTOR_ICON, right_pnl.get_splitter(), right_pnl, scrolled=True)
        viewport, properties_pnl =  right_pnl.split(direction=splitwindow.VERTICAL_SPLIT, 
                                                    label_01="Viewport",
                                                    panel_01=self.ed_viewport_panel,
                                                    label_02="Properties Panel",
                                                    panel_02=self.inspector_panel)
                                                    
        self.console_panel = LogPanel("Console", CONSOLE_ICON, btm_pnl.get_splitter(), btm_pnl)
        self.resource_browser = ResourceBrowser("Resource Browser", RESOURCE_BROWSER, btm_pnl.get_splitter(), btm_pnl)
        console_pnl, resource_pnl = btm_pnl.split(direction=splitwindow.VERTICAL_SPLIT, 
                                                  label_01="Console Panel",
                                                  panel_01=self.console_panel,
                                                  label_02="Resource Browser",
                                                  panel_02=self.resource_browser)
                                                  
        self.scenegraph = scenegraph_
                                                  
        self.__base_panel_top = top_pnl
        self.__base_panel_right = right_pnl
        self.__base_panel_btm_pnl = btm_pnl
        self.saved_layouts = {}  # saved UI layouts
        
        
        # create aui toolbars
        self.file_menu_tb = self.create_toolbar()
        self.file_menu_tb.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.file_menu_tb.Realize()
        # toolbar sizer
        self.toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.toolbar_sizer.Add(self.file_menu_tb, 0, border=0)

        self.__main_sizer.Add(self.toolbar_sizer, 0, wx.EXPAND)
        self.__main_sizer.Add(self.__base_panel, 1, wx.EXPAND)
        self.__main_sizer.Add(self.status_panel, 1, wx.EXPAND)
        
        self.Bind(wx.EVT_CLOSE, self.on_event_close)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, evt):
        evt.Skip()

    def do_after(self):
        self.Maximize(True)
        self.Layout()
        self.Show()
        
        x, y = self.__base_panel.GetSize()
        self.__base_panel.get_splitter().SetSashPosition(y/1.5)
        self.__base_panel_top.get_splitter().SetSashPosition(x/6)
        self.__base_panel_right.get_splitter().SetSashPosition(x/1.65)
        self.__base_panel_btm_pnl.get_splitter().SetSashPosition(x/3)

    def load_resources(self):
        # toolbar
        self.new_session_icon = wx.Bitmap(NEW_SESSION_ICON)
        self.save_session_icon = wx.Bitmap(SAVE_SESSION_ICON)
        self.save_session_as_icon = wx.Bitmap(SAVE_SESSION_AS_ICON)

        self.proj_open_icon = wx.Bitmap(PROJ_OPEN_ICON)
        self.import_lib_icon = wx.Bitmap(IMPORT_LIBRARY_ICON)
        self.import_package_icon = wx.Bitmap(IMPORT_PACKAGE_ICON)
        self.open_store_icon = wx.Bitmap(OPEN_STORE_ICON)

        self.ed_refresh_icon = wx.Bitmap(ED_REFRESH_ICON)

        self.ed_mode_icon = wx.Bitmap(ED_MODE_ICON)
        self.play_icon = wx.Bitmap(PLAY_ICON)
        self.stop_icon = wx.Bitmap(STOP_ICON)

        self.lights_on_icon = wx.Bitmap(ALL_LIGHTS_ON_ICON)
        self.lights_off_icon = wx.Bitmap(ALL_LIGHTS_OFF_ICON)
        self.sound_icon = wx.Bitmap(SOUND_ICON)
        self.no_sound_icon = wx.Bitmap(NO_SOUND_ICON)

        # other
        self.select_icon = wx.Cursor(wx.Image(SELECT_ICON))

    def create_toolbar(self):
        self.file_menu_tb = aui.AuiToolBar(self)

        new_btn = self.file_menu_tb.AddTool(Evt_New_Scene,
                                            '',
                                            self.new_session_icon,
                                            disabled_bitmap=self.new_session_icon,
                                            kind=wx.ITEM_NORMAL,
                                            short_help_string="NewScene")

        save_btn = self.file_menu_tb.AddTool(Evt_Save_Scene,
                                             '',
                                             self.save_session_icon,
                                             disabled_bitmap=self.save_session_icon,
                                             kind=wx.ITEM_NORMAL,
                                             short_help_string="SaveScene")

        save_as_btn = self.file_menu_tb.AddTool(Evt_Save_Scene_As,
                                                '',
                                                self.save_session_as_icon,
                                                disabled_bitmap=self.save_session_as_icon,
                                                kind=wx.ITEM_NORMAL,
                                                short_help_string="SaveSceneAs")

        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, new_btn)
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, save_btn)
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, save_as_btn)

        self.file_menu_tb.AddSeparator()
        # -------------------------------------------------------------------------------------

        open_proj_btn = self.file_menu_tb.AddTool(Evt_Open_Project,
                                                  '',
                                                  self.proj_open_icon,
                                                  disabled_bitmap=self.proj_open_icon,
                                                  kind=wx.ITEM_NORMAL,
                                                  short_help_string="Open Project")

        import_lib_btn = self.file_menu_tb.AddTool(Evt_Append_Library,
                                                   '',
                                                   self.import_lib_icon,
                                                   disabled_bitmap=self.import_lib_icon,
                                                   kind=wx.ITEM_NORMAL,
                                                   short_help_string="Append Library")

        import_package_btn = self.file_menu_tb.AddTool(wx.NewId(),
                                                       '',
                                                       self.import_package_icon,
                                                       disabled_bitmap=self.import_package_icon,
                                                       kind=wx.ITEM_NORMAL,
                                                       short_help_string="Import P3d Package")

        open_store_btn = self.file_menu_tb.AddTool(wx.NewId(),
                                                   '',
                                                   self.open_store_icon,
                                                   disabled_bitmap=self.open_store_icon,
                                                   kind=wx.ITEM_NORMAL,
                                                   short_help_string="PandaStore")

        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, open_proj_btn)
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, import_lib_btn)

        self.file_menu_tb.AddSeparator()
        # -------------------------------------------------------------------------------------

        self.lights_toggle_btn = self.file_menu_tb.AddToggleTool(Evt_Toggle_Scene_Lights,
                                                                 bitmap=self.lights_off_icon,
                                                                 disabled_bitmap=self.lights_off_icon,
                                                                 short_help_string="Toggle Scene Lights",
                                                                 toggle=True)

        self.sounds_on = True
        self.sound_toggle_btn = self.file_menu_tb.AddToggleTool(Evt_Toggle_Sounds,
                                                                bitmap=self.sound_icon,
                                                                disabled_bitmap=self.sound_icon,
                                                                short_help_string="Toggle Sound",
                                                                toggle=True)

        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, self.sound_toggle_btn)
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, self.lights_toggle_btn)

        self.file_menu_tb.AddSeparator()
        # -------------------------------------------------------------------------------------

        self.refresh_btn = self.file_menu_tb.AddTool(Evt_Refresh,
                                                     "",
                                                     bitmap=self.ed_refresh_icon,
                                                     disabled_bitmap=self.ed_refresh_icon,
                                                     kind=wx.ITEM_NORMAL,
                                                     short_help_string="Refresh Editor")

        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, self.refresh_btn)

        self.file_menu_tb.AddSeparator()
        # -------------------------------------------------------------------------------------

        self.ed_viewport_mode_btn = self.file_menu_tb.AddToggleTool(Evt_Ed_Viewport_style,
                                                                    bitmap=self.ed_mode_icon,
                                                                    disabled_bitmap=self.ed_mode_icon,
                                                                    short_help_string="Maximize Game ViewPort On Play",
                                                                    toggle=True)

        self.ply_btn = self.file_menu_tb.AddToggleTool(Evt_Play,
                                                       bitmap=self.play_icon,
                                                       disabled_bitmap=self.play_icon,
                                                       short_help_string="Start Game",
                                                       toggle=True)

        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, self.ed_viewport_mode_btn)
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, self.ply_btn)

        return self.file_menu_tb

    def on_save_current_layout(self):
        dial = wx.TextEntryDialog(None, "Enter layout name", "Layout", "")
        if dial.ShowModal() and dial.GetValue() != "" and dial.GetValue() not in self.saved_layouts.keys():
            name = dial.GetValue()
            self.save_layout(name)

    def save_layout(self, name):
        self.saved_layouts[name] = "--> SOME LAYOUT DATA HERE <--"
        self.__menu_bar.add_ui_layout_menu(name)
        self.saved_layouts.keys()

    def load_layout(self, layout):
        # check if layout exists
        self.Freeze()
        if self.saved_layouts.__contains__(layout):
            print("--> LOAD UI LAYOUT <--")
        self.Thaw()

    def on_evt_toolbar(self, evt):
        if evt.GetId() in Event_Map:
            evt_name = Event_Map[evt.GetId()][0]
            editor.observer.trigger(evt_name)
        evt.Skip()

    def on_evt_left_down(self, evt):
        evt.Skip()

    def on_event_close(self, event):
        editor.observer.trigger("CloseApp", close_wx=False)
        event.Skip()

    @property
    def menu_bar(self):
        return self.__menu_bar
