import wx
import wx.lib.agw.aui as aui

from editor.wxUI.wxMenuBar import WxMenuBar
from editor.wxUI.panels import *
from editor.wxUI.wxDialogs import DialogManager
from editor.constants import object_manager, obs, ICONS_PATH

# scene events
Evt_Open_Project = wx.NewId()
Evt_New_Scene = wx.NewId()
Evt_Open_Scene = wx.NewId()
Evt_Save_Scene = wx.NewId()
Evt_Save_Scene_As = wx.NewId()
Evt_Append_Library = wx.NewId()

Evt_Refresh = wx.NewId()

Evt_Ed_Viewport_style = wx.NewId()
Evt_Play = wx.NewId()
Evt_Toggle_Scene_Lights = wx.NewId()
Evt_Toggle_Sounds = wx.NewId()

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
ICON_FILE = ICONS_PATH + "\\" + "pandaIcon.ico"
NEW_SESSION_ICON = ICONS_PATH + "\\" + "fileNew_32.png"
OPEN_ICON = ICONS_PATH + "\\" + "fileOpen_32.png"
SAVE_SESSION_ICON = ICONS_PATH + "\\" + "fileSave_32.png"
SAVE_SESSION_AS_ICON = ICONS_PATH + "\\" + "fileSaveAs_32.png"
PROJ_OPEN_ICON = ICONS_PATH + "\\" + "fileOpen_32.png"
PROJ_SAVE_ICON = ICONS_PATH + "\\" + "fileOpen_32.png"
IMPORT_LIBRARY_ICON = ICONS_PATH + "\\" + "importLib_32.png"
IMPORT_PACKAGE_ICON = ICONS_PATH + "\\" + "add_package.png"
OPEN_STORE_ICON = ICONS_PATH + "\\" + "shop_network.png"

ED_REFRESH_ICON = ICONS_PATH + "\\" + "Refresh_Icon_32.png."

ED_MODE_ICON = ICONS_PATH + "\\" + "game_mode.png."
PLAY_ICON = ICONS_PATH + "\\" + "playIcon_32x.png"
STOP_ICON = ICONS_PATH + "\\" + "stopIcon_32.png"

ALL_LIGHTS_ON_ICON = ICONS_PATH + "\\" + "lightbulb_32x_on.png"
ALL_LIGHTS_OFF_ICON = ICONS_PATH + "\\" + "lightbulb_32x_off.png"
SOUND_ICON = ICONS_PATH + "\\" + "soundIcon.png"
NO_SOUND_ICON = ICONS_PATH + "\\" + "noSoundIcon.png"

DISABLED_ICON = ICONS_PATH + "\\" + "disabled_icon.png"

SELECT_ICON = ICONS_PATH + "\\" + "hand_point_090.png"

xx = "panel631603ca0000000000000002=+0|panel631603d60000000c00000003=+1|panel631603de0000001400000004=+4" \
     "|panel631603e60000001c00000006=+2|panel631603ec0000002200000006=+3@layout2|name=dummy;caption=;state" \
     "=67372030;dir=3;layer=0;row=0;pos=0;prop=100000;bestw=180;besth=180;minw=180;minh=180;maxw=-1;maxh=-1" \
     ";floatx=-1;floaty=-1;floatw=-1;floath=-1;notebookid=-1;transparent=255|name" \
     "=panel631603ca0000000000000002;caption=;state=67372028;dir=5;layer=0;row=0;pos=0;prop=100000;bestw=0" \
     ";besth=0;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;floaty=-1;floatw=-1;floath=-1;notebookid=-1" \
     ";transparent=255|name=panel631603d60000000c00000003;caption=;state=67372028;dir=2;layer=0;row=1;pos=0" \
     ";prop=100000;bestw=392;besth=237;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;floaty=-1;floatw=-1;floath" \
     "=-1;notebookid=-1;transparent=255|name=panel631603de0000001400000004;caption=;state=67372028;dir=4" \
     ";layer=0;row=1;pos=0;prop=100000;bestw=180;besth=180;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;floaty" \
     "=-1;floatw=-1;floath=-1;notebookid=-1;transparent=255|name=panel631603e60000001c00000006;caption=;state" \
     "=67372028;dir=3;layer=0;row=1;pos=0;prop=70984;bestw=180;besth=180;minw=-1;minh=-1;maxw=-1;maxh=-1" \
     ";floatx=-1;floaty=-1;floatw=-1;floath=-1;notebookid=-1;transparent=255|name" \
     "=panel631603ec0000002200000006;caption=;state=67372028;dir=3;layer=0;row=1;pos=1;prop=129015;bestw=180" \
     ";besth=180;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;floaty=-1;floatw=-1;floath=-1;notebookid=-1" \
     ";transparent=255|dock_size(5,0,0)=10|dock_size(2,0,1)=332|dock_size(4,0,1)=182|dock_size(3,0,1)=228|"


class AUINotebook(aui.AuiNotebook):
    """
    AUI Notebook class
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        aui.AuiNotebook.__init__(self, parent=parent)
        self.default_style = aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_TAB_EXTERNAL_MOVE | wx.NO_BORDER
        self.SetWindowStyleFlag(self.default_style)

    def add_pages(self, pages):
        for page, name in pages:
            self.AddPage(page, name, False)


class WxFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        object_manager.add_object("WxMain", self)

        # set the application icon
        icon_file = ICON_FILE
        icon = wx.Icon(icon_file, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.panda_app = wx.GetApp()
        self.freeze()
        self.load_resources()

        # set menu bar
        self.menu_bar = WxMenuBar(self)
        self.SetMenuBar(self.menu_bar)

        # create a status bar
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Welcome to PandaEditor")

        # create the notebook
        self.notebook = AUINotebook(self)
        self.saved_layouts = {}  # saved perspectives for aui notebook

        # create aui toolbars
        self.build_file_menu_tb()
        self.build_proj_menus_tb()
        self.build_scene_ctrls_tb()
        self.build_ed_ctrls_tb()
        self.build_play_ctrls_tb()

        self.dialogue_manager = DialogManager()

        self.ed_viewport_panel = Viewport(self)
        self.inspector_panel = InspectorPanel(self)
        self.log_panel = LogPanel(self.notebook)
        self.resource_browser = ResourceBrowser(self)
        self.scene_graph_panel = SceneBrowserPanel(self)

        self.pages = [(self.ed_viewport_panel, "ViewPort"),
                      (self.inspector_panel, "Inspector"),
                      (self.log_panel, "LogPanel"),
                      (self.resource_browser, "ResourceBrowser"),
                      (self.scene_graph_panel, "SceneGraph")]

        # add panels to notebook
        self.notebook.add_pages(self.pages)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.main_sizer)

        self.toolbar_sizer.Add(self.file_menu_tb, 0)
        self.toolbar_sizer.Add(self.proj_meuns_tb, 0)
        self.toolbar_sizer.Add(self.scene_ctrls_tb, 0)
        self.toolbar_sizer.Add(self.ed_ctrls_tb, 0)
        self.toolbar_sizer.Add(self.playctrls_tb, 0)

        self.main_sizer.Add(self.toolbar_sizer, 0, wx.EXPAND)
        self.main_sizer.Add(self.notebook, 1, wx.EXPAND)

        self.notebook.LoadPerspective(xx)
        perspective = self.notebook.SavePerspective()
        self.saved_layouts["Default"] = perspective
        self.menu_bar.add_layout_menu("Default")
        self.Maximize(True)

        self.Bind(wx.EVT_SIZE, self.on_evt_resize)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_evt_left_down)
        self.Bind(wx.EVT_CLOSE, self.on_event_close)

    def do_after(self):
        for panel, name in self.pages:
            panel.Bind(wx.EVT_SIZE, self.on_evt_resize)
        self.Show()
        self.thaw()

    def load_resources(self):
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

        self.select_icon = wx.Cursor(wx.Image(SELECT_ICON))

    def build_file_menu_tb(self):
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

        self.file_menu_tb.Realize()
        self.file_menu_tb.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, new_btn)
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, save_btn)
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, save_as_btn)

    def build_proj_menus_tb(self):
        self.proj_meuns_tb = aui.AuiToolBar(self)

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

    def build_scene_ctrls_tb(self):
        self.scene_ctrls_tb = aui.AuiToolBar(self)

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

    def build_ed_ctrls_tb(self):
        self.ed_ctrls_tb = aui.AuiToolBar(self)

        self.refresh_btn = self.ed_ctrls_tb.AddTool(Evt_Refresh,
                                                    "",
                                                    bitmap=self.ed_refresh_icon,
                                                    disabled_bitmap=self.ed_refresh_icon,
                                                    kind=wx.ITEM_NORMAL,
                                                    short_help_string="RefreshIcon")

        self.ed_ctrls_tb.Realize()
        self.Bind(wx.EVT_TOOL, self.on_evt_toolbar, self.refresh_btn)

    def build_play_ctrls_tb(self):
        self.playctrls_tb = aui.AuiToolBar(self)

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

    def save_current_layout(self, name=None):
        dial = wx.TextEntryDialog(None, "Enter layout name", "Layout", "")
        if dial.ShowModal() and dial.GetValue() != "" and dial.GetValue() not in self.saved_layouts.keys():
            name = dial.GetValue()
            self.saved_layouts[name] = self.notebook.SavePerspective()
            self.menu_bar.add_layout_menu(name)

    def load_layout(self, layout):
        # check if layout exists
        # close all notebook pages
        # finally, load the layout
        pass

    def add_page(self, page):
        print(page)

    def delete_page(self, page):
        """permanently deletes a panel and removes it from notebook"""
        pass

    def set_status_bar_text(self, txt: str):
        self.status_bar.SetStatusText(txt)

    def on_evt_toolbar(self, evt):
        if evt.GetId() in Event_Map:
            evt_name = Event_Map[evt.GetId()][0]
            obs.trigger(evt_name)
        evt.Skip()

    def on_evt_left_down(self, evt):
        evt.Skip()

    def on_evt_resize(self, event):
        obs.trigger("ResizeEvent")
        event.Skip()

    def on_evt_page_close(self, page):
        pass

    def on_event_close(self, event):
        obs.trigger("CloseApp", close_wx=False)
        event.Skip()

    def freeze(self):
        if not self.IsFrozen():
            self.Freeze()

    def thaw(self):
        if self.IsFrozen():
            self.Thaw()
