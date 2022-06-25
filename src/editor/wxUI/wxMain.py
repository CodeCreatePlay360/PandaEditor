import wx
import wx.lib.agw.aui as aui

from editor.wxUI.wxMenuBar import WxMenuBar
from editor.wxUI.resourceBrowser import ResourceBrowser
from editor.wxUI.sceneBrowser import SceneBrowserPanel
from editor.wxUI.inspectorPanel import InspectorPanel
from editor.wxUI.logPanel import LogPanel
from editor.wxUI.auxiliaryPanel import AuxiliaryPanel
from editor.wxUI.wxDialogs import DialogManager
from editor.p3d import wxPanda
from editor.constants import object_manager, obs, ICONS_PATH
from thirdparty.wxCustom.auiManager import AuiManager

# scene events
Evt_Open_Project = wx.NewId()
Evt_New_Scene = wx.NewId()
Evt_Open_Scene = wx.NewId()
Evt_Save_Scene = wx.NewId()
Evt_Save_Scene_As = wx.NewId()
Evt_Append_Library = wx.NewId()

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

PLAY_ICON = ICONS_PATH + "\\" + "playIcon_32x.png"
STOP_ICON = ICONS_PATH + "\\" + "stopIcon_32.png"

ALL_LIGHTS_ON_ICON = ICONS_PATH + "\\" + "lightbulb_32x_on.png"
ALL_LIGHTS_OFF_ICON = ICONS_PATH + "\\" + "lightbulb_32x_off.png"
SOUND_ICON = ICONS_PATH + "\\" + "soundIcon.png"
NO_SOUND_ICON = ICONS_PATH + "\\" + "noSoundIcon.png"

DISABLED_ICON = ICONS_PATH + "\\" + "disabled_icon.png"


class WxFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.panda_app = wx.GetApp()
        object_manager.add_object("WxMain", self)

        self.load_resources()

        # TODO change this to use resource globals
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

        self.dialogue_manager = DialogManager()

        self.ed_viewport_panel = wxPanda.Viewport(self, style=wx.BORDER_SUNKEN)  # editor_viewport
        self.inspector_panel = InspectorPanel(self)
        self.log_panel = LogPanel(self)  # log panel
        self.resource_browser = ResourceBrowser(self)
        self.scene_graph_panel = SceneBrowserPanel(self)
        # self.auxiliary_panel = AuxiliaryPanel(self)

        # default panel definitions
        self.panel_defs = {
            "SceneBrowserPanel": (self.scene_graph_panel,
                                  True,
                                  aui.AuiPaneInfo().
                                  Name("SceneGraphPanel").
                                  Caption("SceneGraph").
                                  CloseButton(True).
                                  MaximizeButton(False).
                                  Direction(4).Layer(0).Row(0).Position(0)),

            # dir=4;layer=0;row=0;pos=0
            "EditorViewportPanel": (self.ed_viewport_panel,
                                    True,
                                    aui.AuiPaneInfo().
                                    Name("EditorViewportPanel").
                                    Caption("EditorViewport").
                                    CloseButton(False).
                                    MaximizeButton(True).
                                    Direction(4).Layer(0).Row(2).Position(0)),

            # dir=4;layer=0;row=2;pos=0
            "ObjectInspectorPanel": (self.inspector_panel,
                                     True,
                                     aui.AuiPaneInfo().
                                     Name("ObjectInspectorPanel").
                                     Caption("Object Inspector").
                                     CloseButton(True).
                                     MaximizeButton(False).
                                     Direction(4).Layer(0).Row(3).Position(0)),

            # dir=3;layer=1;row=0;pos=0
            "ResourceBrowserPanel": (self.resource_browser,
                                     True,
                                     aui.AuiPaneInfo().
                                     Name("ResourceBrowserPanel").
                                     Caption("ResourceBrowser").
                                     CloseButton(True).
                                     MaximizeButton(False).
                                     Direction(3).Layer(1).Row(0).Position(1)),

            # dir=3;layer=1;row=0;pos=1
            "ConsolePanel": (self.log_panel,
                             True,
                             aui.AuiPaneInfo().
                             Name("ConsolePanel").
                             Caption("Console").
                             CloseButton(True).
                             MaximizeButton(False).
                             Direction(3).Layer(1).Row(0).Position(0)),
        }

        # user defined panel definitions for editor plugins
        self.user_panel_defs = {}

        self.SetMinSize((800, 600))
        self.Maximize(True)
        self.Layout()
        self.Center()

        self.create_default_layout()
        self.aui_manager.Update()

        self.Bind(wx.EVT_SIZE, self.resize_event)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_evt_left_down)
        self.Bind(wx.EVT_CLOSE, self.on_event_close)

        # some cleanup
        for pane_def in self.panel_defs.values():
            pane_def[2].MinSize(wx.Size(0, 0))

    def create_default_layout(self):
        size = self.GetSize()

        # create a default layout
        for pane_def in self.panel_defs.values():

            self.aui_manager.AddPane(pane_def[0], pane_def[2])

            if pane_def[2].name == "SceneGraphPanel":
                proportion_x = (15 / 100) * size.x
                proportion_y = (60 / 100) * size.y
                pane_def[2].MinSize1(wx.Size(proportion_x, proportion_y))

            if pane_def[2].name == "EditorViewportPanel":
                proportion_x = (60 / 100) * size.x
                proportion_y = (60 / 100) * size.y
                pane_def[2].MinSize1(wx.Size(proportion_x, proportion_y))

            if pane_def[2].name == "ObjectInspectorPanel":
                proportion_x = (25 / 100) * size.x
                proportion_y = (60 / 100) * size.y
                pane_def[2].MinSize1(wx.Size(proportion_x, proportion_y))
                pane_def[2].dock_proportion = 100

            if pane_def[2].name == "ResourceBrowserPanel":
                proportion_y = (30 / 100) * size.y
                pane_def[2].MinSize1(wx.Size(1, proportion_y))
                pane_def[2].dock_proportion = 65

            if pane_def[2].name == "ConsolePanel":
                proportion_y = (30 / 100) * size.y
                pane_def[2].MinSize1(wx.Size(1, proportion_y))
                pane_def[2].dock_proportion = 35

    def load_resources(self):
        self.new_session_icon = wx.Bitmap(NEW_SESSION_ICON)
        # self.open_icon = wx.Bitmap(OPEN_ICON)
        self.save_session_icon = wx.Bitmap(SAVE_SESSION_ICON)
        self.save_session_as_icon = wx.Bitmap(SAVE_SESSION_AS_ICON)

        self.proj_open_icon = wx.Bitmap(PROJ_OPEN_ICON)
        self.proj_save_icon = wx.Bitmap(PROJ_SAVE_ICON)
        self.import_lib_icon = wx.Bitmap(IMPORT_LIBRARY_ICON)
        self.import_package_icon = wx.Bitmap(IMPORT_PACKAGE_ICON)
        self.open_store_icon = wx.Bitmap(OPEN_STORE_ICON)

        self.play_icon = wx.Bitmap(PLAY_ICON)
        self.stop_icon = wx.Bitmap(STOP_ICON)

        self.lights_on_icon = wx.Bitmap(ALL_LIGHTS_ON_ICON)
        self.lights_off_icon = wx.Bitmap(ALL_LIGHTS_OFF_ICON)
        self.sound_icon = wx.Bitmap(SOUND_ICON)
        self.no_sound_icon = wx.Bitmap(NO_SOUND_ICON)

    def build_filemenu_tb(self):
        self.filemenu_tb = aui.AuiToolBar(self)

        new_btn = self.filemenu_tb.AddTool(Evt_New_Scene,
                                           '',
                                           self.new_session_icon,
                                           disabled_bitmap=self.new_session_icon,
                                           kind=wx.ITEM_NORMAL,
                                           short_help_string="NewScene")

        save_btn = self.filemenu_tb.AddTool(Evt_Save_Scene,
                                            '',
                                            self.save_session_icon,
                                            disabled_bitmap=self.save_session_icon,
                                            kind=wx.ITEM_NORMAL,
                                            short_help_string="SaveScene")

        save_as_btn = self.filemenu_tb.AddTool(Evt_Save_Scene_As,
                                               '',
                                               self.save_session_as_icon,
                                               disabled_bitmap=self.save_session_as_icon,
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
                                                    short_help_string="ImportP3dPackage")

        # add to aui
        self.aui_manager.AddPane(self.proj_meuns_tb, aui.AuiPaneInfo().Name("ProjectMenuToolbar").
                                 Caption("Toolbar").ToolbarPane().Top())
        self.tb_panes.append("ProjectMenuToolbar")

        self.Bind(wx.EVT_TOOL, self.on_event, open_proj_btn)
        self.Bind(wx.EVT_TOOL, self.on_event, import_lib_btn)

    def build_play_ctrls_tb(self):
        self.playctrls_tb = aui.AuiToolBar(self)

        self.ply_btn = self.playctrls_tb.AddTool(Evt_Play,
                                                 "",
                                                 bitmap=self.play_icon,
                                                 disabled_bitmap=self.play_icon,
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

        self.lights_toggle_btn = self.scene_ctrls_tb.AddTool(Evt_Toggle_Scene_Lights,
                                                             "",
                                                             bitmap=self.lights_off_icon,
                                                             disabled_bitmap=self.lights_off_icon,
                                                             kind=wx.ITEM_NORMAL,
                                                             short_help_string="ToggleSceneLights")

        self.sounds_on = True
        self.sound_toggle_btn = self.scene_ctrls_tb.AddTool(Evt_Toggle_Sounds,
                                                            "",
                                                            bitmap=self.sound_icon,
                                                            disabled_bitmap=self.sound_icon,
                                                            kind=wx.ITEM_NORMAL,
                                                            short_help_string="ToggleSound")

        self.aui_manager.AddPane(self.scene_ctrls_tb, aui.AuiPaneInfo().Name("SceneControlsToolbar").
                                 Caption("Toolbar").ToolbarPane().Top())
        self.tb_panes.append("SceneControlsToolbar")

        self.Bind(wx.EVT_TOOL, self.on_event, self.sound_toggle_btn)
        self.Bind(wx.EVT_TOOL, self.on_event, self.lights_toggle_btn)

    def add_panel_def(self, name: str):
        if name in self.user_panel_defs.keys():
            # if an entry already exists than return that entry
            return self.user_panel_defs[name][0]
        else:
            # add a new entry
            panel = AuxiliaryPanel(self)
            panel_def = (panel, True,
                         aui.AuiPaneInfo().
                         Name(name).
                         Caption(name).
                         CloseButton(True).
                         MaximizeButton(False))

            self.user_panel_defs[name] = panel_def
            return panel_def[0]

    def add_panel(self, panel):
        if panel in self.user_panel_defs.keys():
            panel_def = self.user_panel_defs[panel]

        elif panel in self.panel_defs.keys():
            panel_def = self.panel_defs[panel]

        else:
            print("[WxMain] Unable to add panel {0}, Panel not found in panel_definitions.".format(panel))
            return

        self.aui_manager.AddPane(panel_def[0], panel_def[2])
        self.aui_manager.ShowPane(panel_def[0], True)
        self.aui_manager.Update()

    def clear_panel_contents(self, panel):
        for key in self.user_panel_defs.keys():
            panel_def = self.user_panel_defs[key]
            if panel_def[0] is panel:
                # delete all sizer(s) / children of this panel
                for child in panel.GetChildren():
                    child.Destroy()

    def on_pane_close(self, pane):
        self.aui_manager.Update()

    def delete_panel(self, panel):
        """permanently deletes a panel from aui manager's managed panels list, only user created panel definitions
        can be deleted"""

        if panel in self.user_panel_defs.keys():
            panel_def = self.user_panel_defs[panel]

            # tell aui manager to remove and detach the panel_def from managed panes
            self.aui_manager.ClosePane(panel_def[2])
            self.aui_manager.DetachPane(panel_def[0])

            # now destroy the wx panel itself
            panel_def[0].Destroy()

            # finally remove from panel_defs repo
            del self.user_panel_defs[panel]
            # print("[WxMain] Panel {0} deleted".format(panel_def[0]))

            # sometimes aui manager crashes during Update when window is minimized or if it is not in focus
            try:
                self.aui_manager.Update()
            except:
                pass

    def set_status_bar_text(self, txt: str):
        self.status_bar.SetStatusText(txt)

    def on_event(self, evt):
        if evt.GetId() in Event_Map:
            evt_name = Event_Map[evt.GetId()][0]
            obs.trigger(evt_name)
        evt.Skip()

    def on_evt_left_down(self, evt):
        evt.Skip()

    def resize_event(self, event):
        event.Skip()

    def on_event_close(self, event):
        obs.trigger("CloseApp", close_wx=False)
        event.Skip()
