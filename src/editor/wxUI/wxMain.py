import wx
import wx.lib.agw.aui as aui

from wx.lib.scrolledpanel import ScrolledPanel
from thirdparty.wxCustom.auiManager import AuiManager
from editor.wxUI.wxMenuBar import WxMenuBar

from editor.wxUI.resourceBrowser import _ResourceBrowser
from editor.wxUI.sceneBrowser import SceneBrowserPanel
from editor.wxUI.inspectorPanel import InspectorPanel
from editor.wxUI.logPanel import LogPanel
from editor.wxUI.auxiliaryPanel import AuxiliaryPanel

from editor.wxUI.wxDialogs import DialogManager
from editor.p3d import wxPanda
from editor.constants import object_manager, obs, ICONS_PATH

# scene events
TB_EVT_NEW = wx.NewId()
TB_EVT_OPEN = wx.NewId()
TB_EVT_SAVE = wx.NewId()
TB_EVT_SAVE_AS = wx.NewId()

TB_EVT_PROJ_OPEN = wx.NewId()
TB_EVT_PROJ_SAVE = wx.NewId()
TB_EVT_APPEND_LIB = wx.NewId()

TB_EVT_PLAY = wx.NewId()
TB_EVT_TOGGLE_LIGHTS = wx.NewId()
TB_EVT_TOGGLE_SOUND = wx.NewId()

PROJ_EVENTS = {
    TB_EVT_NEW: "NewScene",
    TB_EVT_OPEN: "OpenScene",
    TB_EVT_SAVE: "SaveScene",
    TB_EVT_SAVE_AS: "SaveSceneAs",
    TB_EVT_PROJ_OPEN: "OpenProject",
    TB_EVT_PROJ_SAVE: "SaveProject",
    TB_EVT_APPEND_LIB: "AppendLibrary",

    TB_EVT_PLAY: "SwitchEdState",
    TB_EVT_TOGGLE_LIGHTS: "ToggleSceneLights",
    TB_EVT_TOGGLE_SOUND: "ToggleSounds",
}

# resources
ICON_FILE = ICONS_PATH + "\\" + "pandaIcon.ico"
NEW_ICON = ICONS_PATH + "\\" + "fileNew_32.png"
OPEN_ICON = ICONS_PATH + "\\" + "fileOpen_32.png"
SAVE_ICON = ICONS_PATH + "\\" + "fileSave_32.png"
SAVE_AS_ICON = ICONS_PATH + "\\" + "fileSaveAs_32.png"
PROJ_OPEN_ICON = ICONS_PATH + "\\" + "fileOpen_32.png"
PROJ_SAVE_ICON = ICONS_PATH + "\\" + "fileOpen_32.png"
IMPORT_LIBRARY_ICON = ICONS_PATH + "\\" + "importLib_32.png"

PLAY_ICON = ICONS_PATH + "\\" + "playIcon_32x.png"
STOP_ICON = ICONS_PATH + "\\" + "stopIcon_32.png"

ALL_LIGHTS_ON_ICON = ICONS_PATH + "\\" + "lightbulb_32x_on.png"
ALL_LIGHTS_OFF_ICON = ICONS_PATH + "\\" + "lightbulb_32x_off.png"
SOUND_ICON = ICONS_PATH + "\\" + "soundIcon.png"
NO_SOUND_ICON = ICONS_PATH + "\\" + "noSoundIcon.png"

DISABLED_ICON = ICONS_PATH + "\\" + "disabled_icon.png"

DEFAULT_AUI_LAYOUT = "layout2|name=FileMenuToolBar;caption=Toolbar;state=67379964;\
dir=1;layer=10;row=0;pos=0;prop=100000;bestw=135;besth=42;minw=-1;minh=-1;maxw=-1;\
maxh=-1;floatx=-1;floaty=-1;floatw=-1;floath=-1;notebookid=-1;\
transparent=255|name=ProjectMenuToolbar;caption=Toolbar;state=67379964;dir=1;layer=10;\
row=0;pos=137;prop=100000;bestw=95;besth=42;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;\
floaty=-1;floatw=-1;floath=-1;notebookid=-1;transparent=255|name=SceneControlsToolbar;\
caption=Toolbar;state=67379964;dir=1;layer=10;row=0;pos=234;prop=100000;bestw=95;besth=42;\
minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;floaty=-1;floatw=-1;floath=-1;notebookid=-1;\
transparent=255|name=PlayControlsToolbar;caption=Toolbar;state=67379964;dir=1;layer=10;\
row=0;pos=331;prop=100000;bestw=55;besth=42;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;\
floaty=-1;floatw=-1;floath=-1;notebookid=-1;transparent=255|name=EditorViewport;\
caption=EditorView;state=134481916;dir=4;layer=0;row=0;pos=0;prop=100000;bestw=1;besth=1;\
minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=-1;floaty=-1;floatw=-1;floath=-1;notebookid=-1;\
transparent=255|name=ObjectInspectorTab;caption=InspectorTab;state=201590780;dir=4;layer=0;\
row=2;pos=0;prop=100000;bestw=1;besth=20;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=1018;\
floaty=383;floatw=1;floath=20;notebookid=-1;transparent=255|name=ResourceBrowser;\
caption=ResourceBrowser;state=201590780;dir=3;layer=1;row=0;pos=0;prop=43181;\
bestw=16;besth=35;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=509;floaty=657;floatw=576;\
floath=216;notebookid=-1;transparent=255|name=LogTab;caption=LogTab;state=201590780;dir=3;\
layer=1;row=0;pos=1;prop=156817;bestw=118;besth=49;minw=-1;minh=-1;maxw=-1;maxh=-1;floatx=637;\
floaty=555;floatw=118;floath=49;notebookid=-1;\
transparent=255|dock_size(1,10,0)=44|dock_size(4,0,0)=813|dock_size(4,0,2)=335|dock_size(3,1,0)=262|"


class WxFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.panda_app = wx.GetApp()
        object_manager.add_object("WxMain", self)

        self.load_resources()

        icon_file = ICON_FILE
        icon = wx.Icon(icon_file, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        # set menu bar
        self.menu_bar = WxMenuBar(self)
        self.SetMenuBar(self.menu_bar)

        # set status bar
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Welcome to PandaEditor")

        # setup aui manager
        self.aui_manager = AuiManager(self)

        # wx aui toolbars
        self.tb_panes = []  # names of all aui toolbars
        self.build_filemenu_tb()
        self.build_proj_menus_tb()
        self.build_scene_ctrls_tb()
        self.build_play_ctrls_tb()

        # setup dialogue manager
        self.dialogue_manager = DialogManager()

        # create various wx-panels
        self.ed_viewport_panel = wxPanda.Viewport(self, style=wx.BORDER_SUNKEN)  # editor_viewport
        self.inspector_panel = InspectorPanel(self)  # inspector panel
        # self.inspector_panel.set_layout_auto(False)
        self.log_panel = LogPanel(self)  # log panel
        self.resource_browser = _ResourceBrowser(self)
        self.scene_graph_panel = SceneBrowserPanel(self)
        self.auxiliary_panel = AuxiliaryPanel(self)

        self.panel_defs = {
            "SceneBrowser": (self.scene_graph_panel,
                             True,
                             aui.AuiPaneInfo().
                             Name("SceneGraph").
                             Caption("SceneGraph").
                             CloseButton(True).
                             MaximizeButton(False).
                             Direction(4).Layer(0).Row(0).Position(0)),

            # dir=4;layer=0;row=0;pos=0
            "EditorViewport": (self.ed_viewport_panel,
                               True,
                               aui.AuiPaneInfo().
                               Name("EditorViewport").
                               Caption("EditorViewport").
                               CloseButton(False).
                               MaximizeButton(True).
                               Direction(4).Layer(0).Row(1).Position(0)),

            # dir=4;layer=0;row=2;pos=0
            "ObjectInspectorTab": (self.inspector_panel,
                                   True,
                                   aui.AuiPaneInfo().
                                   Name("ObjectInspectorTab").
                                   Caption("InspectorTab").
                                   CloseButton(True).
                                   MaximizeButton(False).
                                   Direction(4).Layer(0).Row(2).Position(0)),

            # dir=3;layer=1;row=0;pos=0
            "ResourceBrowser": (self.resource_browser,
                                True,
                                aui.AuiPaneInfo().
                                Name("ResourceBrowser").
                                Caption("ResourceBrowser").
                                CloseButton(True).
                                MaximizeButton(False).
                                Direction(3).Layer(1).Row(0).Position(1)),

            # dir=3;layer=1;row=0;pos=1
            "LogTab": (self.log_panel,
                       True,
                       aui.AuiPaneInfo().
                       Name("LogTab").
                       Caption("LogTab").
                       CloseButton(True).
                       MaximizeButton(False).
                       Direction(3).Layer(1).Row(0).Position(0)),

            "AuxiliaryPanel": (self.auxiliary_panel,
                               True,
                               aui.AuiPaneInfo().Name("AuxiliaryPanel").
                               Caption("AuxiliaryPanel").
                               CloseButton(True).
                               MaximizeButton(False))
        }

        self.SetMinSize((800, 600))
        self.Maximize(True)
        self.Layout()
        self.Center()

        self.create_default_layout()
        self.aui_manager.Update()

        self.Bind(wx.EVT_SIZE, self.on_event_size)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_evt_left_down)
        self.Bind(wx.EVT_CLOSE, self.on_event_close)

        # some cleanup
        for pane_def in self.panel_defs.values():
            pane_def[2].MinSize(wx.Size(0, 0))

    def create_default_layout(self):
        size = self.GetSize()

        # create a default layout
        for pane_def in self.panel_defs.values():

            if pane_def[2].name == "AuxiliaryPanel":
                self.add_panel_def(name="AuxiliaryPanel", panel_def=pane_def[2])
                continue

            self.aui_manager.AddPane(pane_def[0], pane_def[2])

            if pane_def[2].name == "SceneGraph":
                proportion_x = (20 / 100) * size.x
                proportion_y = (60 / 100) * size.y
                pane_def[2].MinSize1(wx.Size(proportion_x, proportion_y))

            if pane_def[2].name == "EditorViewport":
                proportion_x = (55 / 100) * size.x
                proportion_y = (60 / 100) * size.y
                pane_def[2].MinSize1(wx.Size(proportion_x, proportion_y))

            if pane_def[2].name == "ObjectInspectorTab":
                proportion_x = (25 / 100) * size.x
                proportion_y = (60 / 100) * size.y
                pane_def[2].MinSize1(wx.Size(proportion_x, proportion_y))
                pane_def[2].dock_proportion = 100

            if pane_def[2].name == "ResourceBrowser":
                proportion_y = (30 / 100) * size.y
                pane_def[2].MinSize1(wx.Size(1, proportion_y))
                pane_def[2].dock_proportion = 25

            if pane_def[2].name == "LogTab":
                proportion_y = (30 / 100) * size.y
                pane_def[2].MinSize1(wx.Size(1, proportion_y))
                pane_def[2].dock_proportion = 75

    def load_resources(self):
        self.new_icon = wx.Bitmap(NEW_ICON)
        self.open_icon = wx.Bitmap(OPEN_ICON)
        self.save_icon = wx.Bitmap(SAVE_ICON)
        self.save_as_icon = wx.Bitmap(SAVE_AS_ICON)

        self.proj_open_icon = wx.Bitmap(PROJ_OPEN_ICON)
        self.proj_save_icon = wx.Bitmap(PROJ_SAVE_ICON)
        self.import_lib_icon = wx.Bitmap(IMPORT_LIBRARY_ICON)

        self.play_icon = wx.Bitmap(PLAY_ICON)
        self.stop_icon = wx.Bitmap(STOP_ICON)

        self.lights_on_icon = wx.Bitmap(ALL_LIGHTS_ON_ICON)
        self.lights_off_icon = wx.Bitmap(ALL_LIGHTS_OFF_ICON)
        self.sound_icon = wx.Bitmap(SOUND_ICON)
        self.no_sound_icon = wx.Bitmap(NO_SOUND_ICON)

        self.disabled_icon = wx.Bitmap(DISABLED_ICON)

    def finish_init(self):
        self.on_event_size()

    def build_filemenu_tb(self):
        self.filemenu_tb = aui.AuiToolBar(self)

        new_btn = self.filemenu_tb.AddTool(TB_EVT_NEW, '', self.new_icon,
                                           disabled_bitmap=self.disabled_icon,
                                           kind=wx.ITEM_NORMAL,
                                           short_help_string="NewScene")

        save_btn = self.filemenu_tb.AddTool(TB_EVT_SAVE, '', self.save_icon,
                                            disabled_bitmap=self.disabled_icon,
                                            kind=wx.ITEM_NORMAL,
                                            short_help_string="SaveScene")

        save_as_btn = self.filemenu_tb.AddTool(TB_EVT_SAVE_AS, '', self.save_as_icon,
                                               disabled_bitmap=self.disabled_icon,
                                               kind=wx.ITEM_NORMAL,
                                               short_help_string="SaveSceneAs")

        # add to aui
        self.aui_manager.AddPane(self.filemenu_tb, aui.AuiPaneInfo().Name("FileMenuToolBar").
                                 Caption("Toolbar").ToolbarPane().Top())
        self.tb_panes.append("FileMenuToolBar")

        # events
        self.Bind(wx.EVT_TOOL, self.on_event, new_btn)
        self.Bind(wx.EVT_TOOL, self.on_event, save_btn)
        self.Bind(wx.EVT_TOOL, self.on_event, save_as_btn)

    def build_proj_menus_tb(self):
        self.proj_meuns_tb = aui.AuiToolBar(self)

        open_proj_btn = self.proj_meuns_tb.AddTool(TB_EVT_PROJ_OPEN, '', self.proj_open_icon,
                                                   disabled_bitmap=self.disabled_icon,
                                                   kind=wx.ITEM_NORMAL,
                                                   short_help_string="OpenProject")

        import_lib_btn = self.proj_meuns_tb.AddTool(TB_EVT_APPEND_LIB, '', self.import_lib_icon,
                                                    disabled_bitmap=self.disabled_icon,
                                                    kind=wx.ITEM_NORMAL,
                                                    short_help_string="AppendLibrary")

        # add to aui
        self.aui_manager.AddPane(self.proj_meuns_tb, aui.AuiPaneInfo().Name("ProjectMenuToolbar").
                                 Caption("Toolbar").ToolbarPane().Top())
        self.tb_panes.append("ProjectMenuToolbar")

        self.Bind(wx.EVT_TOOL, self.on_event, open_proj_btn)
        self.Bind(wx.EVT_TOOL, self.on_event, import_lib_btn)

    def build_play_ctrls_tb(self):
        # build
        self.playctrls_tb = aui.AuiToolBar(self)

        self.ply_btn = self.playctrls_tb.AddTool(TB_EVT_PLAY, "", bitmap=self.play_icon,
                                                 disabled_bitmap=self.disabled_icon,
                                                 kind=wx.ITEM_NORMAL,
                                                 short_help_string="StartGame")

        # add to aui
        self.aui_manager.AddPane(self.playctrls_tb, aui.AuiPaneInfo().Name("PlayControlsToolbar").
                                 Caption("Toolbar").ToolbarPane().Top())
        self.tb_panes.append("PlayControlsToolbar")

        # events
        self.Bind(wx.EVT_TOOL, self.on_event, self.ply_btn)

    def build_scene_ctrls_tb(self):
        self.scene_ctrls_tb = aui.AuiToolBar(self)

        self.lights_toggle_btn = self.scene_ctrls_tb.AddTool(TB_EVT_TOGGLE_LIGHTS, "",
                                                             bitmap=self.lights_off_icon,
                                                             disabled_bitmap=self.disabled_icon,
                                                             kind=wx.ITEM_NORMAL,
                                                             short_help_string="ToggleSceneLights")

        self.sounds_on = True
        self.sound_toggle_btn = self.scene_ctrls_tb.AddTool(TB_EVT_TOGGLE_SOUND, "",
                                                            bitmap=self.sound_icon,
                                                            disabled_bitmap=self.disabled_icon,
                                                            kind=wx.ITEM_NORMAL,
                                                            short_help_string="ToggleSound")

        self.aui_manager.AddPane(self.scene_ctrls_tb, aui.AuiPaneInfo().Name("SceneControlsToolbar").
                                 Caption("Toolbar").ToolbarPane().Top())
        self.tb_panes.append("SceneControlsToolbar")

        self.Bind(wx.EVT_TOOL, self.on_event, self.sound_toggle_btn)
        self.Bind(wx.EVT_TOOL, self.on_event, self.lights_toggle_btn)

    def add_panel_def(self, name, panel_def):
        if name not in self.panel_defs.keys():
            self.panel_defs[name] = panel_def

    def add_tab(self, tab):
        if tab in self.panel_defs.keys():
            paneldef = self.panel_defs[tab]
        else:
            print("WxMain --> Unable to add tab {0}, panel is not defined in panel_definitions.".format(tab))
            return

        self.aui_manager.AddPane(paneldef[0], paneldef[2])
        self.aui_manager.ShowPane(paneldef[0], True)

        self.aui_manager.Update()

    def on_pane_close(self, pane):
        self.aui_manager.Update()

    def delete_tab(self, tab):
        """permanently deletes a tab from aui manager's managed tab's list"""
        if tab in self.panel_defs.keys():
            panel_def = self.panel_defs[tab]

            # tell aui manager to remove and detach the paneldef from managed panes
            self.aui_manager.ClosePane(panel_def[2])
            self.aui_manager.DetachPane(panel_def[0])

            # now destroy the wx panel itself
            panel_def[0].Destroy()

            # finally remove from panel_defs repo
            del self.panel_defs[tab]
            print("deleted tab {0}".format(panel_def[0]))
            # sometimes aui manager crashes during Update when window is minimized and
            # or aui manager is not in focus
            try:
                self.aui_manager.Update()
            except:
                pass

    def set_status_bar_text(self, txt: str):
        self.status_bar.SetStatusText(txt)

    def get_save_data(self):
        pass

    def on_event(self, evt):
        if evt.GetId() in PROJ_EVENTS:
            obs.trigger("ProjectEvent", PROJ_EVENTS[evt.GetId()])

        evt.Skip()

    def on_evt_left_down(self, evt):
        print("wx event left down")
        evt.Skip()

    def on_event_size(self, event=None):
        size = self.ed_viewport_panel.GetSize()
        obs.trigger("EventWxSize", size)
        if event is not None:
            event.Skip()

    def on_event_close(self, event):
        obs.trigger("EvtCloseApp", close_wx=False)
        event.Skip()
