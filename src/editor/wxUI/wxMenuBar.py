import wx
import editor.commands as commands
import editor.constants as constants

Evt_Create_Project = wx.NewId()
Evt_Open_Project = wx.NewId()
Evt_New_Scene = wx.NewId()
Evt_Open_Scene = wx.NewId()
Evt_Save_Scene = wx.NewId()
Evt_Save_Scene_As = wx.NewId()
Evt_Append_Library = wx.NewId()
Evt_Build_Project = wx.NewId()

Evt_Add_Inspector_Panel = wx.NewId()
Evt_Add_Resource_Panel = wx.NewId()
Evt_Add_Scene_Graph_Panel = wx.NewId()
Evt_Add_Console_Panel = wx.NewId()

Evt_Save_UI_Layout = wx.NewId()
Evt_Load_UI_Layout = wx.NewId()
Evt_Reload_Editor = wx.NewId()

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

Evt_Open_Discord = wx.NewId()
Evt_Open_Patreon = wx.NewId()
Evt_Open_Discourse = wx.NewId()

Evt_Close_App = wx.NewId()

EVENT_MAP = {
    # EventID = (EventName, *args)
    Evt_Create_Project: ("CreateNewProject", None),
    Evt_Open_Project: ("OpenProject", None),
    Evt_New_Scene: ("CreateNewSession", None),
    Evt_Open_Scene: ("OpenSession", None),
    Evt_Save_Scene: ("SaveSession", None),
    Evt_Save_Scene_As: ("SaveSessionAs", None),
    Evt_Append_Library: ("AppendLibrary", None),
    Evt_Build_Project: ("BuildProject", None),

    Evt_Add_Capsule: ("AddObject", constants.CAPSULE_PATH),
    Evt_Add_Cone: ("AddObject", constants.CONE_PATH),
    Evt_Add_Plane: ("AddObject", constants.PLANE_PATH),
    Evt_Add_Cube: ("AddObject", constants.CUBE_PATH),

    Evt_Add_Sun_Light: ("AddLight", "DirectionalLight"),
    Evt_Add_Point_Light: ("AddLight", "PointLight"),
    Evt_Add_Spot_Light: ("AddLight", "SpotLight"),
    Evt_Add_Ambient_Light: ("AddLight", "AmbientLight"),

    Evt_Add_Camera: ("AddCamera", None),

    Evt_Add_Inspector_Panel: ("AddPanel", "ObjectInspectorPanel"),
    Evt_Add_Resource_Panel: ("AddPanel", "ResourceBrowserPanel"),
    Evt_Add_Scene_Graph_Panel: ("AddPanel", "SceneBrowserPanel"),
    Evt_Add_Console_Panel: ("AddPanel", "ConsolePanel"),

    Evt_Save_UI_Layout: ("SaveUILayout", None),
    Evt_Load_UI_Layout: ("LoadUILayout", None),

    Evt_Open_Discord: ("OpenSocialMediaLink", "Discord"),
    Evt_Open_Discourse: ("OpenSocialMediaLink", "Discourse"),
    Evt_Open_Patreon: ("OpenSocialMediaLink", "Patreon"),

    Evt_Close_App: ("CloseApp", None)
}



UI_LAYOUT_EVENTS = {
    Evt_Save_UI_Layout: "SaveUILayout"
}


class WxMenuBar(wx.MenuBar):
    def __init__(self, wx_main):
        wx.MenuBar.__init__(self)
        self.wx_main = wx_main
        self.user_layout_menus = {}
        self.ed_plugins_menus = {}

        self.build()

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

        menu_items = [(Evt_Add_Inspector_Panel, "Inspector", None),
                      (Evt_Add_Resource_Panel, "ResourceBrowser", None),
                      (Evt_Add_Scene_Graph_Panel, "SceneGraph", None),
                      (Evt_Add_Console_Panel, "ConsolePanel", None)]
        build_menu_bar(panels, menu_items)

        # editor layout menus
        self.ed_layout_menu = wx.Menu()
        self.Append(self.ed_layout_menu, "Layout")

        menu_items = [(Evt_Save_UI_Layout, "SaveLayout", None), ""]
        build_menu_bar(self.ed_layout_menu, menu_items)

        # menu items related to editor operations
        ed_menu = wx.Menu()
        self.Append(ed_menu, "Editor")

        menu_items = [(Evt_Reload_Editor, "Reload", None)]
        build_menu_bar(ed_menu, menu_items)

        # editor plugins menus
        self.ed_plugin_menus = wx.Menu()
        self.Append(self.ed_plugin_menus, "Plugins")

        # custom user command menus
        self.user_command_menus = wx.Menu()
        self.Append(self.user_command_menus, "Commands")

        # social media links menu
        social_links = wx.Menu()
        self.Append(social_links, "Social")

        menu_items = [(Evt_Open_Discord, "Discord", None),
                      (Evt_Open_Discourse, "Panda3d discourse", None),
                      (Evt_Open_Patreon, "Patreon", None)]
        build_menu_bar(social_links, menu_items)

    def add_layout_menu(self, name):
        if name not in self.user_layout_menus.values():
            _id = wx.NewId()
            menu_item = wx.MenuItem(self.ed_layout_menu, _id, name)
            self.ed_layout_menu.Append(menu_item)
            self.user_layout_menus[_id] = name

    def add_plugin_menu(self, menu_name: str):
        if menu_name not in self.ed_plugins_menus.values():
            _id = wx.NewId()
            menu_item = wx.MenuItem(self.ed_plugin_menus, _id, menu_name)
            self.ed_plugin_menus.Append(menu_item)
            self.ed_plugins_menus[_id] = menu_name

    def add_user_command_menu(self, menu_name: str):
        pass

    def clear_plugin_menus(self):
        pass

    def clear_command_menus(self):
        pass

    def on_event(self, evt):
        if evt.GetId() in EVENT_MAP:
            evt_name = EVENT_MAP[evt.GetId()][0]
            args = EVENT_MAP[evt.GetId()][1]

            if evt_name == "AddObject":
                constants.command_manager.do(commands.ObjectAdd(constants.p3d_app, args))
            elif evt_name == "AddLight":
                constants.command_manager.do(commands.AddLight(constants.p3d_app, args))
            elif evt_name == "AddCamera":
                constants.command_manager.do(commands.AddCamera(constants.p3d_app))
            elif evt_name == "AddPanel":
                constants.obs.trigger("LoadPanel", args)
            else:
                constants.obs.trigger(evt_name, args)

        elif evt.GetId() in self.ed_plugins_menus.keys():
            constants.obs.trigger("OnPluginMenuEntrySelected", self.ed_plugins_menus[evt.GetId()])

        elif evt.GetId() in self.user_layout_menus.keys():
            constants.obs.trigger("LoadUserLayout", self.user_layout_menus[evt.GetId()])

        evt.Skip()
