import wx
import editor.commands as commands
import editor.constants as constants

# from editor.constants import CUBE_PATH, CAPSULE_PATH, PLANE_PATH, CONE_PATH, obs, command_manager, p3d_app


EVT_SET_PROJECT = wx.NewId()
EVT_OPEN_PROJECT = wx.NewId()
EVT_NEW = wx.NewId()
EVT_OPEN = wx.NewId()
EVT_SAVE = wx.NewId()
EVT_SAVE_AS = wx.NewId()
EVT_APPEND_LIBRARY = wx.NewId()
EVT_BUILD = wx.NewId()

EVT_ADD_EDITOR_TAB = wx.NewId()
EVT_ADD_INSPECTOR_TAB = wx.NewId()
EVT_ADD_RESOURCES_TAB = wx.NewId()
EVT_ADD_SCENE_GRAPH_TAB = wx.NewId()
EVT_ADD_LOG_TAB = wx.NewId()

EVT_UI_SAVE_LAYOUT = wx.NewId()

RELOAD_EDITOR_DATA = wx.NewId()

EVT_ADD_EMPTY_NP = wx.NewId()
EVT_ADD_CAMERA = wx.NewId()
EVT_ADD_SUN_LIGHT = wx.NewId()
EVT_ADD_POINT_LIGHT = wx.NewId()
EVT_ADD_SPOT_LIGHT = wx.NewId()
EVT_ADD_AMBIENT_LIGHT = wx.NewId()

EVT_ADD_CUBE = wx.NewId()
EVT_ADD_CAPSULE = wx.NewId()
EVT_ADD_CONE = wx.NewId()
EVT_ADD_PLANE = wx.NewId()

EVT_CLOSE_APP = wx.NewId()

UI_TAB_EVENTS = {
    EVT_ADD_EDITOR_TAB: "EditorViewport",
    EVT_ADD_INSPECTOR_TAB: "ObjectInspectorTab",
    EVT_ADD_RESOURCES_TAB: "ResourceBrowser",
    EVT_ADD_SCENE_GRAPH_TAB: "SceneBrowser",
    EVT_ADD_LOG_TAB: "LogTab",
}

UI_LAYOUT_EVENTS = {
    EVT_UI_SAVE_LAYOUT: "SaveUILayout"
}

OBJECT_EVENTS = {
    EVT_ADD_CAPSULE: constants.CAPSULE_PATH,
    EVT_ADD_CONE: constants.CONE_PATH,
    EVT_ADD_PLANE: constants.PLANE_PATH,
    EVT_ADD_CUBE: constants.CUBE_PATH
}

LIGHT_EVENTS = {
    EVT_ADD_SUN_LIGHT: "DirectionalLight",
    EVT_ADD_POINT_LIGHT: "PointLight",
    EVT_ADD_SPOT_LIGHT: "SpotLight",
    EVT_ADD_AMBIENT_LIGHT: "AmbientLight"
}

PROJ_EVENTS = {
    EVT_SET_PROJECT: "SetProject",
    EVT_OPEN_PROJECT: "OpenProject",
    EVT_NEW: "NewScene",
    EVT_OPEN: "OpenScene",
    EVT_SAVE: "SaveScene",
    EVT_SAVE_AS: "SaveSceneAs",
    EVT_APPEND_LIBRARY: "AppendLibrary",
    EVT_BUILD: "Build",
    # EVT_QUIT: "CloseApplication",
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
        menu_items = [(EVT_NEW, "&New Scene\tCtrl+N", None),
                      (EVT_OPEN, "&Open\tCtrl+O", None),
                      "",
                      (EVT_SAVE, "&Save Scene\tCtrl+S", None),
                      (EVT_SAVE_AS, "&Save Scene As\tCtrl+Shift+S", None),
                      "",
                      (EVT_CLOSE_APP, "&Exit\tCtrl+E", None)]
        build_menu_bar(file_menu, menu_items)

        # project related menus
        proj_menu = wx.Menu()
        self.Append(proj_menu, "Project")
        menu_items = [(EVT_SET_PROJECT, "&Start New Project", None),
                      (EVT_OPEN_PROJECT, "&Load Project", None),
                      "",
                      (EVT_APPEND_LIBRARY, "&Append Library", None),
                      "",
                      (EVT_BUILD, "Build", None),
                      ]
        build_menu_bar(proj_menu, menu_items)

        # add objects menus
        object_menu = wx.Menu()
        self.Append(object_menu, "Object")

        # add empty
        menu_items = [(EVT_ADD_EMPTY_NP, "Add Empty", None)]
        build_menu_bar(object_menu, menu_items)

        # camera
        menu_items = [(EVT_ADD_CAMERA, "Add Camera", None)]
        build_menu_bar(object_menu, menu_items)

        # lights
        lights_obj_menu = wx.Menu()
        menu_items = [(EVT_ADD_SUN_LIGHT, "SunLight", None),
                      (EVT_ADD_POINT_LIGHT, "PointLight", None),
                      (EVT_ADD_SPOT_LIGHT, "SpotLight", None),
                      (EVT_ADD_AMBIENT_LIGHT, "AmbientLight", None)
                      ]
        build_menu_bar(lights_obj_menu, menu_items)
        object_menu.Append(wx.ID_ANY, "Lights", lights_obj_menu)

        # gameobjects
        game_obj_menu = wx.Menu()
        menu_items = [(EVT_ADD_CUBE, "Cube", None),
                      (EVT_ADD_CAPSULE, "Capsule", None),
                      (EVT_ADD_CONE, "Cone", None),
                      (EVT_ADD_PLANE, "Plane", None)
                      ]
        build_menu_bar(game_obj_menu, menu_items)
        object_menu.Append(wx.ID_ANY, "GameObject", game_obj_menu)

        # panels menus
        tabs_menu = wx.Menu()
        self.Append(tabs_menu, "Panels")

        menu_items = [(EVT_ADD_INSPECTOR_TAB, "Inspector", None),
                      (EVT_ADD_RESOURCES_TAB, "ResourceBrowser", None),
                      (EVT_ADD_SCENE_GRAPH_TAB, "SceneGraph", None),
                      (EVT_ADD_LOG_TAB, "ConsolePanel", None)]
        build_menu_bar(tabs_menu, menu_items)

        # editor layout menus
        self.ed_layout_menu = wx.Menu()
        self.Append(self.ed_layout_menu, "Layout")

        menu_items = [(EVT_UI_SAVE_LAYOUT, "SaveLayout", None)]
        build_menu_bar(self.ed_layout_menu, menu_items)

        # menu items related to editor operations
        ed_menu = wx.Menu()
        self.Append(ed_menu, "Editor")

        menu_items = [(RELOAD_EDITOR_DATA, "Reload", None)]
        build_menu_bar(ed_menu, menu_items)

        # editor plugins menus
        self.ed_plugins_menu = wx.Menu()
        self.Append(self.ed_plugins_menu, "Plugins")

    def add_layout_menu(self, name):
        if name not in self.user_layout_menus.values():
            _id = wx.NewId()
            menu_item = wx.MenuItem(self.ed_layout_menu, _id, name)
            self.ed_layout_menu.Append(menu_item)
            self.user_layout_menus[_id] = name

    def add_plugins_menu(self, menu_name: str):
        if menu_name not in self.ed_plugins_menus.values():
            _id = wx.NewId()
            menu_item = wx.MenuItem(self.ed_plugins_menu, _id, menu_name)
            self.ed_plugins_menu.Append(menu_item)
            self.ed_plugins_menus[_id] = menu_name

    def add_custom_command_menu(self, menu_name: str):
        pass

    def clear_layout_menus(self):
        pass

    def clear_plugin_menus(self):
        pass

    def on_event(self, evt):
        if evt.GetId() in PROJ_EVENTS:
            constants.obs.trigger("ProjectEvent", PROJ_EVENTS[evt.GetId()])

        elif evt.GetId() in UI_TAB_EVENTS:
            constants.obs.trigger("EventAddTab", UI_TAB_EVENTS[evt.GetId()])

        elif evt.GetId() in UI_LAYOUT_EVENTS:
            constants.obs.trigger("UILayoutEvent", UI_LAYOUT_EVENTS[evt.GetId()])

        elif evt.GetId() in LIGHT_EVENTS:
            constants.command_manager.do(commands.AddLight(constants.p3d_app, LIGHT_EVENTS[evt.GetId()]))
            # constants.obs.trigger("AddLight", LIGHT_EVENTS[evt.GetId()])

        elif evt.GetId() is EVT_ADD_CAMERA:
            constants.command_manager.do(commands.AddCamera(constants.p3d_app))
            # constants.obs.trigger("AddCamera")

        elif evt.GetId() in OBJECT_EVENTS:
            constants.command_manager.do(commands.ObjectAdd(constants.p3d_app, OBJECT_EVENTS[evt.GetId()]))
            # obs.trigger("AddObject", OBJECT_EVENTS[evt.GetId()])

        elif evt.GetId() in self.user_layout_menus.keys():
            constants.obs.trigger("LoadUserLayout", self.user_layout_menus[evt.GetId()])

        elif evt.GetId() in self.ed_plugins_menus.keys():
            constants.obs.trigger("LoadEdPluginPanel", self.ed_plugins_menus[evt.GetId()])

        elif evt.GetId() == EVT_CLOSE_APP:
            constants.obs.trigger("EvtCloseApp")

        evt.Skip()
