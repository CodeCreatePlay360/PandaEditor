import pathlib
import sys
import wx
import wx.aui
import wx.lib.agw.aui as aui

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

# auiNotebook events
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
ICON_FILE = str(pathlib.Path(ICONS_PATH + "/pandaIcon.ico"))
#
NEW_SESSION_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/fileNew_32.png"))
OPEN_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/fileOpen_32.png"))
SAVE_SESSION_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/fileSave_32.png"))
SAVE_SESSION_AS_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/fileSaveAs_32.png"))
#
PROJ_OPEN_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/fileOpen_32.png"))
IMPORT_LIBRARY_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/package_link.png"))
IMPORT_PACKAGE_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/add_package.png"))
OPEN_STORE_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/shop_network.png"))
#
ALL_LIGHTS_ON_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/lightbulb_32x_on.png"))
ALL_LIGHTS_OFF_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/lightbulb_32x_off.png"))
SOUND_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/soundIcon.png"))
NO_SOUND_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/noSoundIcon.png"))
#
ED_REFRESH_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/Refresh_Icon_32.png"))
#
ED_MODE_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/game_mode.png"))
PLAY_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/playIcon_32x.png"))
STOP_ICON = str(pathlib.Path(ICONS_PATH + "/ToolBar/stopIcon_32.png"))
#
DISABLED_ICON = str(pathlib.Path(ICONS_PATH + "/disabled_icon.png"))
#
SELECT_ICON = str(pathlib.Path(ICONS_PATH + "/hand_point_090.png"))
#
# notebook page icons
VIEWPORT_ICON = str(pathlib.Path(ICONS_PATH + "/NP_Pages/image_16x.png"))
INSPECTOR_ICON = str(pathlib.Path(ICONS_PATH + "/NP_Pages/gear_16x.png"))
CONSOLE_ICON = str(pathlib.Path(ICONS_PATH + "/NP_Pages/monitor_16x.png"))
RESOURCE_BROWSER = str(pathlib.Path(ICONS_PATH + "/NP_Pages/folder_16x.png"))
SCENE_GRAPH_ICON = str(pathlib.Path(ICONS_PATH + "/NP_Pages/structure_16x.png"))
#
# status bar
REFRESH_ICON = str(pathlib.Path(ICONS_PATH + "/StatusBar/arrow_refresh.png"))

# default layout for notebook tabs
xx = "panel631603ca0000000000000002=+0|panel631603d60000000c00000003=+1|panel631603de0000001400000004=+4|" \
     "panel631603e60000001c00000006=+2|panel631603ec0000002200000006=+3@layout2|" \
     "name=dummy;caption=;state=67372030;dir=3;layer=0;row=0;pos=0;prop=100000;bestw=180;besth=180;minw=180;" \
     "minh=180;maxw=-1;maxh=-1;floatx=-1;floaty=-1;floatw=-1;floath=-1;notebookid=-1;transparent=255|" \
     "name=panel631603ca0000000000000002;caption=;state=67372028;dir=5;layer=0;row=0;pos=0;prop=100000;bestw=0;" \
     "besth=0;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;floaty=-1;floatw=-1;floath=-1;notebookid=-1;" \
     "transparent=255|name=panel631603d60000000c00000003;caption=;state=67372028;dir=2;layer=0;row=1;pos=0;" \
     "prop=100000;bestw=392;besth=237;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;floaty=-1;floatw=-1;floath=-1;" \
     "notebookid=-1;transparent=255|name=panel631603de0000001400000004;caption=;state=67372028;dir=4;layer=0;" \
     "row=1;pos=0;prop=100000;bestw=180;besth=180;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;floaty=-1;floatw=-1;" \
     "floath=-1;notebookid=-1;transparent=255|name=panel631603e60000001c00000006;caption=;state=67372028;dir=3;" \
     "layer=0;row=1;pos=0;prop=70984;bestw=180;besth=180;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;floaty=-1;" \
     "floatw=-1;floath=-1;notebookid=-1;transparent=255|name=panel631603ec0000002200000006;caption=;" \
     "state=67372028;dir=3;layer=0;row=1;pos=1;prop=129015;bestw=180;besth=180;minw=-1;minh=-1;maxw=-1;maxh=-1;" \
     "floatx=-1;floaty=-1;floatw=-1;floath=-1;notebookid=-1;transparent=255|dock_size(5,0,0)=10|" \
     "dock_size(2,0,1)=332|dock_size(4,0,1)=182|dock_size(3,0,1)=228|"


class WxAUINotebook(wx.aui.AuiNotebook):
    class NotebookPageAndIdx:
        def __init__(self, idx, page, label):
            self.idx = idx
            self.page = page
            self.label = label

    def __init__(self, parent):
        wx.aui.AuiNotebook.__init__(self, parent=parent)
        self.__parent = parent
        self.__active_pages = []  # keep track of all active pages

    def AddPage(self, page, caption, select=False):
        super().AddPage(page, caption, select=False)
        self.__active_pages.append(caption)

    def DeletePage(self, page_idx):
        if self.GetPageText(page_idx) == "Viewport":
            return False

        self.RemovePage(page_idx)
        return True

    def RemovePage(self, page_idx):
        self.__active_pages.remove(self.GetPageText(page_idx))
        super().RemovePage(page_idx)

    def DoGetBestSize(self):
        return wx.Size(self.__parent.GetSize().x, -1)

    def add_pages(self, pages):
        for page, name, bitmap in pages:
            self.AddPage(page, name, True)

    def is_page_active(self, name):
        return self.__active_pages.__contains__(name)

    @property
    def active_pages(self):
        return self.__active_pages


class AUINotebook(aui.AuiNotebook):
    class NotebookPageAndIdx:
        def __init__(self, idx, page, label, bitmap):
            self.idx = idx
            self.page = page
            self.label = label
            self.bitmap = bitmap

    def __init__(self, parent):
        aui.AuiNotebook.__init__(self, parent=parent)
        self.__active_pages = []  # keep track of all active pages

    def AddPage(self, page, caption, select=False, bitmap=wx.NullBitmap, disabled_bitmap=wx.NullBitmap, control=None,
                tooltip=""):
        super().AddPage(page, caption, select=False, bitmap=wx.NullBitmap, disabled_bitmap=wx.NullBitmap, control=None,
                        tooltip="")

    def InsertPage(self, page_idx, page, caption, select=False, bitmap=wx.NullBitmap, disabled_bitmap=wx.NullBitmap,
                   control=None, tooltip=""):
        self.__active_pages.append(caption)
        super().InsertPage(page_idx, page, caption, select=False, bitmap=bitmap, disabled_bitmap=wx.NullBitmap,
                           control=None, tooltip="")

    def DeletePage(self, page_idx):
        if self.GetPageText(page_idx) == "Viewport":
            return False

        self.RemovePage(page_idx)
        return True

    def RemovePage(self, page_idx):
        self.__active_pages.remove(self.GetPageText(page_idx))
        super().RemovePage(page_idx)

    def add_pages(self, pages):
        for page, name, bitmap, in pages:
            self.AddPage(page, name, True)

    def is_page_active(self, name):
        return self.__active_pages.__contains__(name)

    @property
    def active_pages(self):
        return self.__active_pages


class WxFrame(wx.Frame):
    USING_SPLITTER = False

    class StatusPanel(wx.Panel):
        class InfoPanel(wx.Window):
            def __init__(self, *args, **kwargs):
                wx.Window.__init__(self, *args, **kwargs)
                self.SetBackgroundColour(editor.ui_config.color_map("Panel_Normal"))

                font = wx.Font(8, editor.ui_config.ed_font, wx.NORMAL, wx.NORMAL)

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

        # set the application icon
        icon_file = ICON_FILE
        icon = wx.Icon(icon_file, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.panda_app = wx.GetApp()
        self.freeze()
        self.load_resources()
        #
        # set menu bar
        self.__menu_bar = MenuBar(self)
        self.SetMenuBar(self.__menu_bar)
        #
        self.status_panel = WxFrame.StatusPanel(self)
        #
        self.ed_viewport_panel = Viewport(self)
        self.inspector_panel = InspectorPanel(self)
        self.console_panel = LogPanel(self)
        self.resource_browser = ResourceBrowser(self)
        self.scene_graph_panel = SceneBrowserPanel(self)

        self.__panels = [(self.ed_viewport_panel, "Viewport", wx.Bitmap(VIEWPORT_ICON)),
                         (self.inspector_panel, "Inspector", wx.Bitmap(INSPECTOR_ICON)),
                         (self.console_panel, "ConsolePanel", wx.Bitmap(CONSOLE_ICON)),
                         (self.resource_browser, "ResourceBrowser", wx.Bitmap(RESOURCE_BROWSER)),
                         (self.scene_graph_panel, "SceneGraph", wx.Bitmap(SCENE_GRAPH_ICON))]

        if sys.platform == "linux":
            self.USING_SPLITTER = True

        # notebook
        self.__main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__main_sizer)

        self.__notebook = WxAUINotebook(self) if self.USING_SPLITTER else AUINotebook(self)  # aui nb has issues on linux
        self.__notebook.add_pages(self.__panels)  # add panels to notebook

        self.__notebook.SetPageBitmap(0, self.__panels[0][2])
        self.__notebook.SetPageBitmap(1, self.__panels[1][2])
        self.__notebook.SetPageBitmap(2, self.__panels[2][2])
        self.__notebook.SetPageBitmap(3, self.__panels[3][2])
        self.__notebook.SetPageBitmap(4, self.__panels[4][2])

        self.saved_layouts = {}  # saved perspectives for aui notebook
        # create aui toolbars
        self.file_menu_tb = self.create_toolbar()
        self.file_menu_tb.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.file_menu_tb.Realize()
        # toolbar sizer
        self.toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.toolbar_sizer.Add(self.file_menu_tb, 0, border=0)

        if not self.USING_SPLITTER:
            self.__notebook.LoadPerspective(xx)
            self.save_layout("Default")
        else:
            pass

        self.__main_sizer.Add(self.toolbar_sizer, 0, wx.EXPAND)
        self.__main_sizer.Add(self.__notebook, 1, wx.EXPAND)
        self.__main_sizer.Add(self.status_panel, 1, wx.EXPAND)

        self.Bind(wx.EVT_CLOSE, self.on_event_close)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, evt):
        # Workaround, sometimes aui notebook brakes after window in minimized,
        # this check restores the layout
        # for panel in self.__panels:
        #     if panel[0].GetSize().y == 0:
        #         self.load_layout("Default")
        evt.Skip()

    def do_after(self):
        self.Maximize(True)
        self.thaw()
        self.Layout()
        self.Show()

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
        if sys.platform == "linux":
            print("Not supported on linux")
            return

        data = []
        for i in range(self.__notebook.GetPageCount()):
            save_obj = AUINotebook.NotebookPageAndIdx(idx=i,
                                                      page=self.__notebook.GetPage(i),
                                                      label=self.__notebook.GetPageText(i),
                                                      bitmap=self.__notebook.GetPageBitmap(i))
            data.append(save_obj)

        self.saved_layouts[name] = (data, self.__notebook.SavePerspective())
        self.__menu_bar.add_ui_layout_menu(name)
        self.saved_layouts.keys()

    def load_layout(self, layout):
        if sys.platform == "linux":
            print("Not supported on linux")
            return

        # check if layout exists
        self.Freeze()
        if self.saved_layouts.__contains__(layout):
            for i in range(len(self.__notebook.active_pages)):
                self.__notebook.RemovePage(0)

            saved_data = self.saved_layouts[layout][0]
            for i in range(len(saved_data)):
                self.__notebook.InsertPage(saved_data[i].idx, saved_data[i].page, saved_data[i].label, bitmap=saved_data[i].bitmap)

            self.__notebook.LoadPerspective(self.saved_layouts[layout][1])  # finally, load perspective
            self.__notebook.Refresh()
        self.Thaw()

    def add_page(self, page: str):
        for item in self.__panels:
            if item[1] == page:
                if not self.__notebook.is_page_active(item[1]):
                    self.__notebook.AddPage(item[0], item[1])
                    # update page bitmap
                    for i in range(len(self.__panels)):
                        if self.__panels[i][1] == page:
                            idx = self.__notebook.GetPageIndex(item[0])
                            self.__notebook.SetPageBitmap(idx, self.__panels[i][2])
                else:
                    print("Page {0} already exists".format(item[1]))

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

    def freeze(self):
        if not hasattr(self, "panels"):
            return

        for item in self.__panels:
            panel = item[0]
            if panel != self.ed_viewport_panel and not panel.IsFrozen():
                panel.Freeze()

    def thaw(self):
        for item in self.__panels:
            panel = item[0]
            if panel.IsFrozen():
                panel.Thaw()

    @property
    def menu_bar(self):
        return self.__menu_bar
