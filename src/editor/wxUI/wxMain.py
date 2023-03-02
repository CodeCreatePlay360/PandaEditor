import wx
import wx.aui
import wx.lib.agw.aui as aui
import editor.edPreferences as edPreferences

from editor.wxUI.wxMenuBar import WxMenuBar
from editor.wxUI.panels import *
from editor.constants import ICONS_PATH
from editor.globals import editor
from editor.wxUI.custom import BasicButton

from direct.showbase.ShowBase import taskMgr


# resources
REFRESH_ICON = ICONS_PATH + "/StatusBar/arrow_refresh.png"

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
ICON_FILE = ICONS_PATH + "/pandaIcon.ico"
#
NEW_SESSION_ICON = ICONS_PATH + "/fileNew_32.png"
OPEN_ICON = ICONS_PATH + "/fileOpen_32.png"
SAVE_SESSION_ICON = ICONS_PATH + "/fileSave_32.png"
SAVE_SESSION_AS_ICON = ICONS_PATH + "/fileSaveAs_32.png"
#
PROJ_OPEN_ICON = ICONS_PATH + "/fileOpen_32.png"
PROJ_SAVE_ICON = ICONS_PATH + "\\" + "fileOpen_32.png"
IMPORT_LIBRARY_ICON = ICONS_PATH + "/importLib_32.png"
IMPORT_PACKAGE_ICON = ICONS_PATH + "/add_package.png"
OPEN_STORE_ICON = ICONS_PATH + "/shop_network.png"
#
ALL_LIGHTS_ON_ICON = ICONS_PATH + "/lightbulb_32x_on.png"
ALL_LIGHTS_OFF_ICON = ICONS_PATH + "/lightbulb_32x_off.png"
SOUND_ICON = ICONS_PATH + "/soundIcon.png"
NO_SOUND_ICON = ICONS_PATH + "/noSoundIcon.png"
#
ED_REFRESH_ICON = ICONS_PATH + "/Refresh_Icon_32.png."
#
ED_MODE_ICON = ICONS_PATH + "/game_mode.png."
PLAY_ICON = ICONS_PATH + "/playIcon_32x.png"
STOP_ICON = ICONS_PATH + "/stopIcon_32.png"
#
DISABLED_ICON = ICONS_PATH + "/disabled_icon.png"
#
SELECT_ICON = ICONS_PATH + "/hand_point_090.png"
#
# notebook page icons
VIEWPORT_ICON = ICONS_PATH + "/Panel_Icons/image_16x.png"
INSPECTOR_ICON = ICONS_PATH + "/Panel_Icons/gear_16x.png"
CONSOLE_ICON = ICONS_PATH + "/Panel_Icons/monitor_16x.png"
RESOURCE_BROWSER = ICONS_PATH + "/Panel_Icons/folder_16x.png"
SCENE_GRAPH_ICON = ICONS_PATH + "/Panel_Icons/structure_16x.png"

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


class AUINotebook(aui.AuiNotebook):
    class NotebookPageAndIdx:
        def __init__(self, idx, page, label):
            self.idx = idx
            self.page = page
            self.label = label

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
        super().InsertPage(page_idx, page, caption, select=False, bitmap=wx.NullBitmap, disabled_bitmap=wx.NullBitmap,
                           control=None, tooltip="")

    def DeletePage(self, page_idx):
        self.RemovePage(page_idx)

    def RemovePage(self, page_idx):
        try:
            self.__active_pages.remove(self.GetPageText(page_idx))
        except ValueError:
            # print("Unable to remove page {0} at index {1}".format(self.GetPageText(page_idx), page_idx))
            pass
        super().RemovePage(page_idx)

    def add_pages(self, pages):
        for page, name in pages:
            self.AddPage(page, name, True)

    def is_page_active(self, name):
        return self.__active_pages.__contains__(name)


class WxFrame(wx.Frame):
    class StatusPanel(wx.Panel):
        def __init__(self, *args):
            wx.Panel.__init__(self, *args)
            self.SetWindowStyleFlag(wx.SUNKEN_BORDER)
            self.SetBackgroundColour(edPreferences.Colors.Panel_Dark)
            self.SetMaxSize((-1, 20))
            self.parent = args[0]
            #
            self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.SetSizer(self.main_sizer)
            #
            self.refresh_btn = self.create_refresh_btn()
            #
            self.bold_font = wx.Font(8, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_MAX)
            self.bg_tasks_text_ctrl = wx.StaticText(self)
            self.bg_tasks_text_ctrl.SetBackgroundColour(edPreferences.Colors.Panel_Normal)
            self.bg_tasks_text_ctrl.SetForegroundColour(wx.Colour(225, 225, 225, 255))
            self.bg_tasks_text_ctrl.SetFont(self.bold_font)
            self.bg_tasks_text_ctrl.SetLabelText("[PandaEditor]")
            #
            self.selected_item_text_info = wx.StaticText(self)
            self.selected_item_text_info.SetBackgroundColour(edPreferences.Colors.Panel_Normal)
            self.selected_item_text_info.SetForegroundColour(wx.Colour(225, 225, 225, 255))
            self.selected_item_text_info.SetFont(self.bold_font)
            self.selected_item_text_info.SetLabelText("(SelectedItemInfo: no info available)")
            #
            self.main_sizer.Add(self.refresh_btn, 0, wx.EXPAND | wx.RIGHT, border=1)
            self.main_sizer.Add(self.bg_tasks_text_ctrl, 0, wx.EXPAND | wx.RIGHT, border=1)
            self.main_sizer.Add(self.selected_item_text_info, 0, wx.EXPAND, border=0)
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
            self.bg_tasks_text_ctrl.SetLabelText(info)
            self.main_sizer.Layout()

        def write_selected_item_info(self):
            self.main_sizer.Layout()

    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        # set the application icon
        icon_file = ICON_FILE
        icon = wx.Icon(icon_file, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        # main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.panda_app = wx.GetApp()
        self.freeze()
        self.load_resources()

        # set menu bar
        self.menu_bar = WxMenuBar(self)
        self.SetMenuBar(self.menu_bar)
        #
        self.status_panel = WxFrame.StatusPanel(self)

        # notebook
        self.notebook = AUINotebook(self)
        self.saved_layouts = {}  # saved perspectives for aui notebook

        self.ed_viewport_panel = Viewport(self)
        self.inspector_panel = InspectorPanel(self)
        self.console_panel = LogPanel(self)
        self.resource_browser = ResourceBrowser(self)
        self.scene_graph_panel = SceneBrowserPanel(self)
        # page icons

        self.panels = [(self.ed_viewport_panel, "ViewPort"),
                       (self.inspector_panel, "Inspector"),
                       (self.console_panel, "ConsolePanel"),
                       (self.resource_browser, "ResourceBrowser"),
                       (self.scene_graph_panel, "SceneGraph")]

        self.notebook.add_pages(self.panels)  # add panels to notebook
        #
        self.notebook.SetPageBitmap(0, wx.Bitmap(VIEWPORT_ICON))
        self.notebook.SetPageBitmap(1, wx.Bitmap(INSPECTOR_ICON))
        self.notebook.SetPageBitmap(2, wx.Bitmap(CONSOLE_ICON))
        self.notebook.SetPageBitmap(3, wx.Bitmap(RESOURCE_BROWSER))
        self.notebook.SetPageBitmap(4, wx.Bitmap(SCENE_GRAPH_ICON))
        #
        # toolbar
        # create aui toolbars
        self.build_file_menu_tb(wx.BORDER_DOUBLE, wx.aui.AUI_TB_GRIPPER)
        self.build_proj_menus_tb(wx.BORDER_DOUBLE, wx.aui.AUI_TB_GRIPPER)
        self.build_scene_ctrls_tb(wx.BORDER_DOUBLE, wx.aui.AUI_TB_GRIPPER)
        self.build_ed_ctrls_tb(wx.BORDER_DOUBLE, wx.aui.AUI_TB_GRIPPER)
        self.build_play_ctrls_tb(wx.BORDER_DOUBLE, wx.aui.AUI_TB_GRIPPER)
        #
        # toolbar sizer
        self.toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #
        self.toolbar_sizer.Add(self.file_menu_tb, 0, wx.RIGHT, 1)
        self.toolbar_sizer.Add(self.proj_meuns_tb, 0, wx.RIGHT, 1)
        self.toolbar_sizer.Add(self.scene_ctrls_tb, 0, wx.RIGHT, 1)
        self.toolbar_sizer.Add(self.ed_ctrls_tb, 0, wx.RIGHT, 1)
        self.toolbar_sizer.Add(self.playctrls_tb, 0, wx.RIGHT, 1)
        #
        self.notebook.LoadPerspective(xx)
        self.save_layout("Default")
        #
        self.main_sizer.Add(self.toolbar_sizer, 0, wx.EXPAND)
        self.main_sizer.Add(self.notebook, 1, wx.EXPAND)
        self.main_sizer.Add(self.status_panel, 1, wx.EXPAND)

        self.Bind(wx.EVT_CLOSE, self.on_event_close)

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
        self.proj_save_icon = wx.Bitmap(PROJ_SAVE_ICON)
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

    def build_file_menu_tb(self, win_style, agw_style):
        self.file_menu_tb = aui.AuiToolBar(self)
        self.file_menu_tb.SetWindowStyle(win_style)
        self.file_menu_tb.SetAGWWindowStyleFlag(agw_style)

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

        self.file_menu_tb.Realize()
        self.file_menu_tb.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, new_btn)
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, save_btn)
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, save_as_btn)

    def build_proj_menus_tb(self, win_style, agw_style):
        self.proj_meuns_tb = aui.AuiToolBar(self)
        self.proj_meuns_tb.SetWindowStyle(win_style)
        self.proj_meuns_tb.SetAGWWindowStyleFlag(agw_style)

        open_proj_btn = self.proj_meuns_tb.AddTool(Evt_Open_Project,
                                                   '',
                                                   self.proj_open_icon,
                                                   disabled_bitmap=self.proj_open_icon,
                                                   kind=wx.ITEM_NORMAL,
                                                   short_help_string="OpenProject")

        import_lib_btn = self.proj_meuns_tb.AddTool(Evt_Append_Library,
                                                    '',
                                                    self.import_lib_icon,
                                                    disabled_bitmap=self.import_lib_icon,
                                                    kind=wx.ITEM_NORMAL,
                                                    short_help_string="AppendLibrary")

        import_package_btn = self.proj_meuns_tb.AddTool(wx.NewId(),
                                                        '',
                                                        self.import_package_icon,
                                                        disabled_bitmap=self.import_package_icon,
                                                        kind=wx.ITEM_NORMAL,
                                                        short_help_string="ImportP3dPackage")

        open_store_btn = self.proj_meuns_tb.AddTool(wx.NewId(),
                                                    '',
                                                    self.open_store_icon,
                                                    disabled_bitmap=self.open_store_icon,
                                                    kind=wx.ITEM_NORMAL,
                                                    short_help_string="PandaStore")

        self.proj_meuns_tb.Realize()
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, open_proj_btn)
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, import_lib_btn)

    def build_scene_ctrls_tb(self, win_style, agw_style):
        self.scene_ctrls_tb = aui.AuiToolBar(self)
        self.scene_ctrls_tb.SetWindowStyle(win_style)
        self.scene_ctrls_tb.SetAGWWindowStyleFlag(agw_style)

        self.lights_toggle_btn = self.scene_ctrls_tb.AddToggleTool(Evt_Toggle_Scene_Lights,
                                                                   bitmap=self.lights_off_icon,
                                                                   disabled_bitmap=self.lights_off_icon,
                                                                   short_help_string="ToggleSceneLights",
                                                                   toggle=True)

        self.sounds_on = True
        self.sound_toggle_btn = self.scene_ctrls_tb.AddToggleTool(Evt_Toggle_Sounds,
                                                                  bitmap=self.sound_icon,
                                                                  disabled_bitmap=self.sound_icon,
                                                                  short_help_string="ToggleSound",
                                                                  toggle=True)

        self.scene_ctrls_tb.Realize()
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, self.sound_toggle_btn)
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, self.lights_toggle_btn)

    def build_ed_ctrls_tb(self, win_style, agw_style):
        self.ed_ctrls_tb = aui.AuiToolBar(self)
        self.ed_ctrls_tb.SetWindowStyle(win_style)
        self.ed_ctrls_tb.SetAGWWindowStyleFlag(agw_style)

        self.refresh_btn = self.ed_ctrls_tb.AddTool(Evt_Refresh,
                                                    "",
                                                    bitmap=self.ed_refresh_icon,
                                                    disabled_bitmap=self.ed_refresh_icon,
                                                    kind=wx.ITEM_NORMAL,
                                                    short_help_string="RefreshIcon")

        self.ed_ctrls_tb.Realize()
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, self.refresh_btn)

    def build_play_ctrls_tb(self, win_style, agw_style):
        self.playctrls_tb = aui.AuiToolBar(self)
        self.playctrls_tb.SetWindowStyle(win_style)
        self.playctrls_tb.SetAGWWindowStyleFlag(agw_style)

        self.ed_viewport_mode_btn = self.playctrls_tb.AddToggleTool(Evt_Ed_Viewport_style,
                                                                    bitmap=self.ed_mode_icon,
                                                                    disabled_bitmap=self.ed_mode_icon,
                                                                    short_help_string="MaximizeGameViewPortOnPlay",
                                                                    toggle=True)

        self.ply_btn = self.playctrls_tb.AddToggleTool(Evt_Play,
                                                       bitmap=self.play_icon,
                                                       disabled_bitmap=self.play_icon,
                                                       short_help_string="StartGame",
                                                       toggle=True)

        self.playctrls_tb.Realize()
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, self.ed_viewport_mode_btn)
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, self.ply_btn)

    def on_save_current_layout(self):
        dial = wx.TextEntryDialog(None, "Enter layout name", "Layout", "")
        if dial.ShowModal() and dial.GetValue() != "" and dial.GetValue() not in self.saved_layouts.keys():
            name = dial.GetValue()
            self.save_layout(name)

    def save_layout(self, name):
        data = []
        for i in range(self.notebook.GetPageCount()):
            save_obj = AUINotebook.NotebookPageAndIdx(idx=i,
                                                      page=self.notebook.GetPage(i),
                                                      label=self.notebook.GetPageText(i))
            data.append(save_obj)

        self.saved_layouts[name] = (data, self.notebook.SavePerspective())
        self.menu_bar.add_ui_layout_menu(name)
        self.saved_layouts.keys()

    def load_layout(self, layout):
        # check if layout exists
        self.freeze()
        if self.saved_layouts.__contains__(layout):
            for i in range(len(self.panels)):
                self.notebook.RemovePage(0)

            saved_data = self.saved_layouts[layout][0]
            for i in range(len(saved_data)):
                self.notebook.InsertPage(saved_data[i].idx, saved_data[i].page, saved_data[i].label)

            self.notebook.LoadPerspective(self.saved_layouts[layout][1])  # finally, load perspective
            self.notebook.Refresh()
            self.notebook.Update()
            self.save_layout(layout)  # update the layout
        self.thaw()

    def add_page(self, page: str):
        for item in self.panels:
            if item[1] == page:
                if not self.notebook.is_page_active(item[1]):
                    self.notebook.AddPage(item[0], item[1], False)
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

        for item in self.panels:
            panel = item[0]
            if not panel.IsFrozen():
                panel.Freeze()

    def thaw(self):
        for item in self.panels:
            panel = item[0]
            if panel.IsFrozen():
                panel.Thaw()
