import wx
import editor.commands as commands
import editor.constants as constants
from editor.globals import editor

Evt_New_Scene = wx.NewId()
Evt_Open_Scene = wx.NewId()
Evt_Save_Scene = wx.NewId()
Evt_Save_Scene_As = wx.NewId()
Evt_Close_App = wx.NewId()

Evt_Create_Project = wx.NewId()
Evt_Open_Project = wx.NewId()
Evt_Append_Library = wx.NewId()
Evt_Build_Project = wx.NewId()

Evt_Add_Empty_NP = wx.NewId()
Evt_Add_Camera = wx.NewId()
Evt_Add_Sun_Light = wx.NewId()
Evt_Add_Point_Light = wx.NewId()
Evt_Add_Spot_Light = wx.NewId()
Evt_Add_Ambient_Light = wx.NewId()
Evt_Add_Cube = wx.NewId()
Evt_Add_Capsule = wx.NewId()
Evt_Add_Cone = wx.NewId()
Evt_Add_Plane = wx.NewId()

Evt_Add_ViewPort_Panel = wx.NewId()
Evt_Add_Inspector_Panel = wx.NewId()
Evt_Add_Resource_Panel = wx.NewId()
Evt_Add_Scene_Graph_Panel = wx.NewId()
Evt_Add_Console_Panel = wx.NewId()

Evt_Save_UI_Layout = wx.NewId()
Evt_Load_UI_Layout = wx.NewId()

Evt_Toggle_Hotkeys_Text = wx.NewId()
Evt_Undo_Last_Command = wx.NewId()
Evt_Reload_Editor = wx.NewId()

Evt_Frame_Selected = wx.NewId()
Evt_Orbit_Top = wx.NewId()
Evt_Orbit_Left = wx.NewId()
Evt_Orbit_Right = wx.NewId()
Evt_Reset_View = wx.NewId()

Evt_Align_Game_View_To_Ed_View = wx.NewId()

Evt_Open_Discord = wx.NewId()
Evt_Open_Patreon = wx.NewId()
Evt_Open_Discourse = wx.NewId()

EVENT_MAP = {
    # EventID = (EventType, EventName, *args)
    # ----------------------------------------------
    Evt_New_Scene: ("CreateNewSession", None),
    Evt_Open_Scene: ("OpenSession", None),
    Evt_Save_Scene: ("SaveSession", None),
    Evt_Save_Scene_As: ("SaveSessionAs", None),
    Evt_Close_App: ("CloseApp", None),

    # ----------------------------------------------
    Evt_Create_Project: ("CreateNewProject", None),
    Evt_Open_Project: ("OpenProject", None),
    Evt_Append_Library: ("AppendLibrary", None),
    Evt_Build_Project: ("BuildProject", None),

    # ----------------------------------------------
    Evt_Add_Camera: ("AddCamera", None),
    #
    Evt_Add_Cube: ("AddObject", constants.CUBE_PATH),
    Evt_Add_Capsule: ("AddObject", constants.CAPSULE_PATH),
    Evt_Add_Cone: ("AddObject", constants.CONE_PATH),
    Evt_Add_Plane: ("AddObject", constants.PLANE_PATH),
    #
    Evt_Add_Sun_Light: ("AddLight", "__DirectionalLight__"),
    Evt_Add_Point_Light: ("AddLight", "__PointLight__"),
    Evt_Add_Spot_Light: ("AddLight", "__SpotLight__"),
    Evt_Add_Ambient_Light: ("AddLight", "__AmbientLight__"),

    # ----------------------------------------------
    Evt_Add_ViewPort_Panel: ("AddPanel", "ViewPort"),
    Evt_Add_Inspector_Panel: ("AddPanel", "Inspector"),
    Evt_Add_Resource_Panel: ("AddPanel", "ResourceBrowser"),
    Evt_Add_Scene_Graph_Panel: ("AddPanel", "SceneGraph"),
    Evt_Add_Console_Panel: ("AddPanel", "LogPanel"),

    # ----------------------------------------------
    Evt_Save_UI_Layout: ("SaveUILayout", None),
    Evt_Load_UI_Layout: ("LoadUILayout", None),

    # ----------------------------------------------
    Evt_Toggle_Hotkeys_Text: ("EditorEvent", "ToggleHotkeysText", None),
    Evt_Undo_Last_Command: ("EditorEvent", "UndoLastCommand", None),
    Evt_Reload_Editor: ("EditorEvent", "ReloadEditor", None),

    # ----------------------------------------------
    Evt_Frame_Selected: ("ViewportEvent", "FrameSelectedNPs", 0),
    Evt_Orbit_Top: ("ViewportEvent", "FrameSelectedNPs", 2),
    Evt_Orbit_Right: ("ViewportEvent", "FrameSelectedNPs", 1),
    Evt_Orbit_Left: ("ViewportEvent", "FrameSelectedNPs", -1),
    Evt_Reset_View: ("ViewportEvent", "ResetView", None),

    # ----------------------------------------------
    Evt_Align_Game_View_To_Ed_View: ("AlignToEdView", None),

    # ----------------------------------------------
    Evt_Open_Discord: ("OpenSocialMediaLink", "Discord"),
    Evt_Open_Discourse: ("OpenSocialMediaLink", "Discourse"),
    Evt_Open_Patreon: ("OpenSocialMediaLink", "Patreon"),
}

UI_LAYOUT_EVENTS = {
    Evt_Save_UI_Layout: "SaveUILayout"}


class WxMenuBar(wx.MenuBar):
    def __init__(self, wx_main):
        wx.MenuBar.__init__(self)
        self.wx_main = wx_main
        self.ui_layout_menus = {}
        self.ed_plugin_menus = {}

        self.commands = []
        self.user_command_menu_items_id_map = {}
        self.user_command_menus_id_map = {}

        self.build()

        # test = wx.Menu()
        # self.Append(test, "Test")
        # menu_01 = "Math/AddNum"
        # menu_02 = "Math/Subtract"
        # menu_03 = "Math/Vector/Mul"
        # menu_04 = "Math/Vector/Dot"
        # menu_05 = "Math/Vector/Scalar/Dot"
        # menu_06 = "Play/Mode/Level/Player"
        # test_menus = {}

        # 9/10/2022 took me about 4 hours to figure this out (from 10.30pm to 2.30am),
        # ObaidUrRehman.
        # def foo(menu, parent):
        #     menu_ = menu.split("/")
        #
        #     for i in range(len(menu_)):
        #         if i == len(menu_)-1:
        #             item_id = parent.FindItem(menu_[(len(menu_)-2)])
        #             parent_ = test_menus[parent.GetLabel(item_id)]
        #             menu_item = wx.MenuItem(parent, -1, menu_[i])
        #             parent_.Append(menu_item)
        #             test_menus[menu_[i]] = menu_item
        #         else:
        #             if menu_[i] in test_menus.keys():
        #                 continue
        #             if i > 0 and menu_[i-1] in test_menus.keys():
        #                 parent = test_menus[menu_[i-1]]
        #
        #             menu_item = wx.Menu()
        #             parent.Append(-1, menu_[i], menu_item)
        #             test_menus[menu_[i]] = menu_item
        #
        # foo(menu_01, parent=test)
        # foo(menu_02, parent=test)
        # foo(menu_03, parent=test)
        # foo(menu_04, parent=test)
        # foo(menu_05, parent=test)
        # foo(menu_06, parent=test)

        self.Bind(wx.EVT_MENU, self.on_event)

    def build(self):
        def build_menu_bar(menu, items):
            for i in range(len(items)):
                _items = items[i]
                if _items == "":
                    menu.AppendSeparator()
                    continue
                menu_item = wx.MenuItem(menu, _items[0], _items[1])
                # menu_item.SetBitmap(wx.Bitmap('exit.png'))
                menu.Append(menu_item)

        # main application and current scene related menu items
        file_menu = wx.Menu()
        self.Append(file_menu, "File")
        menu_items = [(Evt_New_Scene, "&New Scene\tCtrl+N", None),
                      (Evt_Open_Scene, "&Open\tCtrl+O", None),
                      "",
                      (Evt_Save_Scene, "&Save Scene\tCtrl+S", None),
                      (Evt_Save_Scene_As, "&Save Scene As\tCtrl+Shift+S", None),
                      "",
                      (Evt_Close_App, "&Exit\tCtrl+E", None)]
        build_menu_bar(file_menu, menu_items)

        # project related menus
        proj_menu = wx.Menu()
        self.Append(proj_menu, "Project")
        menu_items = [(Evt_Create_Project, "&Start New Project", None),
                      (Evt_Open_Project, "&Load Project", None),
                      "",
                      (Evt_Append_Library, "&Append Library", None),
                      "",
                      (Evt_Build_Project, "Build", None),
                      ]
        build_menu_bar(proj_menu, menu_items)

        # add objects menus
        object_menu = wx.Menu()
        self.Append(object_menu, "Object")

        # add empty
        menu_items = [(Evt_Add_Empty_NP, "Add Empty", None)]
        build_menu_bar(object_menu, menu_items)

        # camera
        menu_items = [(Evt_Add_Camera, "Add Camera", None)]
        build_menu_bar(object_menu, menu_items)

        # lights
        lights_obj_menu = wx.Menu()
        menu_items = [(Evt_Add_Sun_Light, "SunLight", None),
                      (Evt_Add_Point_Light, "PointLight", None),
                      (Evt_Add_Spot_Light, "SpotLight", None),
                      (Evt_Add_Ambient_Light, "AmbientLight", None)
                      ]
        build_menu_bar(lights_obj_menu, menu_items)
        object_menu.Append(wx.ID_ANY, "Lights", lights_obj_menu)

        # gameobjects
        game_obj_menu = wx.Menu()
        menu_items = [(Evt_Add_Cube, "Cube", None),
                      (Evt_Add_Capsule, "Capsule", None),
                      (Evt_Add_Cone, "Cone", None),
                      (Evt_Add_Plane, "Plane", None)
                      ]
        build_menu_bar(game_obj_menu, menu_items)
        object_menu.Append(wx.ID_ANY, "GameObject", game_obj_menu)

        # panels menus
        panels = wx.Menu()
        self.Append(panels, "Panels")
        menu_items = [(Evt_Add_ViewPort_Panel, "ViewPort", None),
                      (Evt_Add_Inspector_Panel, "Inspector", None),
                      (Evt_Add_Resource_Panel, "ResourceBrowser", None),
                      (Evt_Add_Scene_Graph_Panel, "SceneGraph", None),
                      (Evt_Add_Console_Panel, "LogPanel", None)]
        build_menu_bar(panels, menu_items)

        # editor layout menus
        self.ed_layout_menu = wx.Menu()
        self.Append(self.ed_layout_menu, "Layout")
        menu_items = [(Evt_Save_UI_Layout, "SaveLayout", None), ""]
        build_menu_bar(self.ed_layout_menu, menu_items)

        # menu items related to editor operations
        ed_menu = wx.Menu()
        self.Append(ed_menu, "Editor")
        menu_items = [(Evt_Toggle_Hotkeys_Text, "Toggle Hotkeys Text", None),
                      "",
                      (Evt_Undo_Last_Command, "UndoLastCommand", None),
                      "",
                      (Evt_Reload_Editor, "Reload", None)]
        build_menu_bar(ed_menu, menu_items)

        # editor plugins menus
        self.plugin_menu = wx.Menu()
        self.Append(self.plugin_menu, "Plugins")

        # custom user command menus
        self.user_command_menu = wx.Menu()
        self.Append(self.user_command_menu, "User Commands")
        menu_items = [(Evt_Open_Discord, "Discord", None),
                      (Evt_Open_Discourse, "Panda3d discourse", None),
                      (Evt_Open_Patreon, "Patreon", None)]

        # view menu
        view_menu = wx.Menu()
        self.Append(view_menu, "View")
        menu_items = [(Evt_Frame_Selected, "FrameSelected"),
                      "",
                      (Evt_Orbit_Top, "Orbit Top"),
                      (Evt_Orbit_Right, "Orbit Right"),
                      (Evt_Orbit_Left, "Orbit Left"),
                      "",
                      (Evt_Reset_View, "Reset View")]
        build_menu_bar(view_menu, menu_items)

        #
        game_menu = wx.Menu()
        self.Append(game_menu, "Game")
        menu_items = [(Evt_Align_Game_View_To_Ed_View, "AlignToViewportCam"),
                      ""]
        build_menu_bar(game_menu, menu_items)

        # social media links menu
        social_links = wx.Menu()
        self.Append(social_links, "Social")

        menu_items = [(Evt_Open_Discord, "Discord", None),
                      (Evt_Open_Discourse, "Panda3d discourse", None),
                      (Evt_Open_Patreon, "Patreon", None)]
        build_menu_bar(social_links, menu_items)

    def add_ui_layout_menu(self, name):
        if name not in self.ui_layout_menus.values():
            _id = wx.NewId()
            menu_item = wx.MenuItem(self.ed_layout_menu, _id, name)
            self.ed_layout_menu.Append(menu_item)
            self.ui_layout_menus[_id] = name

    def add_ed_plugin_menu(self, menu_name: str):
        if menu_name not in self.ed_plugin_menus.values():
            id_ = wx.NewId()
            menu_item = wx.MenuItem(self.plugin_menu, id_, menu_name)
            self.plugin_menu.Append(menu_item)
            self.ed_plugin_menus[id_] = menu_name

    def add_user_command_menu(self, command_name: str):
        menu_ = command_name.split("/")

        for i in range(len(menu_)):
            if i == len(menu_) - 1:
                if len(menu_) == 1:
                    parent_ = self.user_command_menu
                else:
                    item_id = self.user_command_menu.FindItem(menu_[(len(menu_) - 2)])
                    parent_ = self.user_command_menus_id_map[self.user_command_menu.GetLabel(item_id)]

                id_ = wx.NewId()
                menu_item = wx.MenuItem(self.user_command_menu, id_, menu_[i])
                parent_.Append(menu_item)
                # self.user_command_menu_items_id_map[id_] = menu_[i]
                self.user_command_menu_items_id_map[id_] = command_name
            else:
                if menu_[i] in self.user_command_menus_id_map.keys():
                    continue
                if i > 0 and menu_[i - 1] in self.user_command_menus_id_map.keys():
                    parent = self.user_command_menus_id_map[menu_[i - 1]]
                else:
                    parent = self.user_command_menu

                menu_item = wx.Menu()
                parent.Append(-1, menu_[i], menu_item)
                self.user_command_menus_id_map[menu_[i]] = menu_item

    def clear_ed_plugin_menus(self):
        for menu in self.ed_plugin_menus.values():
            pos = self.plugin_menu.FindItem(menu)
            if pos >= 0:
                self.plugin_menu.Remove(pos)
        self.ed_plugin_menus.clear()

    def clear_user_command_menus(self):
        for menu in self.user_command_menu_items_id_map.values():
            pos = self.user_command_menu.FindItem(menu)
            if pos >= 0:
                self.user_command_menu.Remove(pos)

        self.user_command_menu_items_id_map.clear()
        self.user_command_menus_id_map.clear()

    def on_event(self, evt):
        if evt.GetId() in EVENT_MAP:
            evt_name = EVENT_MAP[evt.GetId()][0]
            args = EVENT_MAP[evt.GetId()][1:]

            if evt_name == "AddObject":
                editor.command_mgr.do(commands.ObjectAdd(args[0]))
            elif evt_name == "AddLight":
                editor.command_mgr.do(commands.AddLight(args[0]))
            elif evt_name == "AddCamera":
                editor.command_mgr.do(commands.AddCamera())

            elif evt_name == "SaveUILayout":
                self.wx_main.on_save_current_layout()

            elif evt_name == "AddPanel":
                self.wx_main.add_page(args)

            elif evt_name == "ViewportEvent":
                command = args[0]
                args = args[1]
                editor.observer.trigger(evt_name, command, args)

            elif evt_name == "EditorEvent":
                command = args[0]
                args = args[1]
                editor.observer.trigger(evt_name, command, args)
            else:
                editor.observer.trigger(evt_name, args)

        elif evt.GetId() in self.ui_layout_menus.keys():
            self.wx_main.load_layout(self.ui_layout_menus[evt.GetId()])

        elif evt.GetId() in self.ed_plugin_menus.keys():
            editor.observer.trigger("OnPluginMenuEntrySelected", self.ed_plugin_menus[evt.GetId()])

        elif evt.GetId() in self.user_command_menu_items_id_map.keys():
            editor.observer.trigger("OnSelUserCommandMenuEntry", self.user_command_menu_items_id_map[evt.GetId()])

        evt.Skip()
