import wx
from editor.constants import obs, CUBE_PATH, CAPSULE_PATH, PLANE_PATH, CONE_PATH

EVT_SET_PROJECT = wx.NewId()
EVT_OPEN_PROJECT = wx.NewId()
EVT_NEW = wx.NewId()
EVT_OPEN = wx.NewId()
EVT_SAVE = wx.NewId()
EVT_SAVE_AS = wx.NewId()
EVT_APPEND_LIBRARY = wx.NewId()

EVT_ADD_EDITOR_TAB = wx.NewId()
EVT_ADD_INSPECTOR_TAB = wx.NewId()
EVT_ADD_RESOURCES_TAB = wx.NewId()
EVT_ADD_SCENE_GRAPH_TAB = wx.NewId()
EVT_ADD_LOG_TAB = wx.NewId()
EVT_ADD_AUXILIARY_TAB = wx.NewId()

EVT_UI_SAVE_LAYOUT = wx.NewId()

EVT_CLEAR_EDITOR_DATA = wx.NewId()
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
    EVT_ADD_AUXILIARY_TAB: "AuxiliaryPanel"
}

UI_LAYOUT_EVENTS = {
    EVT_UI_SAVE_LAYOUT: "SaveUILayout"
}

OBJECT_EVENTS = {
    EVT_ADD_CAPSULE: CAPSULE_PATH,
    EVT_ADD_CONE: CONE_PATH,
    EVT_ADD_PLANE: PLANE_PATH,
    EVT_ADD_CUBE: CUBE_PATH
}

LIGHT_EVENTS = {
    EVT_ADD_SUN_LIGHT: "DirectionalLight",
    EVT_ADD_POINT_LIGHT: "PointLight",
    EVT_ADD_SPOT_LIGHT: "Spotlight",
    EVT_ADD_AMBIENT_LIGHT: "Area"
}

PROJ_EVENTS = {
    EVT_SET_PROJECT: "SetProject",
    EVT_OPEN_PROJECT: "OpenProject",
    EVT_NEW: "NewScene",
    EVT_OPEN: "OpenScene",
    EVT_SAVE: "SaveScene",
    EVT_SAVE_AS: "SaveSceneAs",
    EVT_APPEND_LIBRARY: "AppendLibrary",
    # EVT_QUIT: "CloseApplication",
}


class WxMenuBar(wx.MenuBar):
    def __init__(self, wx_main):
        wx.MenuBar.__init__(self)
        self.wx_main = wx_main
        self.user_layout_menus = {}

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

        # file_menu
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

        # project_menu
        proj_menu = wx.Menu()
        self.Append(proj_menu, "Project")
        menu_items = [(EVT_SET_PROJECT, "&Start New Project", None),
                      (EVT_OPEN_PROJECT, "&Load Project", None),
                      (EVT_APPEND_LIBRARY, "&Append Library", None),
                      ]
        build_menu_bar(proj_menu, menu_items)

        # add objects section
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

        # panels        
        tabs_menu = wx.Menu()
        self.Append(tabs_menu, "Tabs")

        menu_items = [(EVT_ADD_INSPECTOR_TAB, "InspectorTab", None),
                      (EVT_ADD_RESOURCES_TAB, "ResourceBrowser", None),
                      (EVT_ADD_SCENE_GRAPH_TAB, "SceneGraph", None),
                      (EVT_ADD_LOG_TAB, "LogTab", None),
                      (EVT_ADD_AUXILIARY_TAB, "AuxiliaryPanel", None)]
        build_menu_bar(tabs_menu, menu_items)

        # editor layout        
        self.ed_layout_menu = wx.Menu()
        self.Append(self.ed_layout_menu, "Layout")

        menu_items = [(EVT_UI_SAVE_LAYOUT, "SaveLayout", None)]
        build_menu_bar(self.ed_layout_menu, menu_items)

        # general editor events        
        ed_menu = wx.Menu()
        self.Append(ed_menu, "Editor")

        menu_items = [(EVT_CLEAR_EDITOR_DATA, "ClearEdData", None),
                      (RELOAD_EDITOR_DATA, "Reload", None), ]
        build_menu_bar(ed_menu, menu_items)

    def add_layout_menu(self, name):
        if name not in self.user_layout_menus.values():
            _id = wx.NewId()
            menu_item = wx.MenuItem(self.ed_layout_menu, _id, name)
            self.ed_layout_menu.Append(menu_item)

            self.user_layout_menus[_id] = name

    def clear_layout_menus(self):
        pass

    def on_event(self, evt):
        if evt.GetId() in PROJ_EVENTS:
            obs.trigger("ProjectEvent", PROJ_EVENTS[evt.GetId()])

        elif evt.GetId() in UI_TAB_EVENTS:
            obs.trigger("EventAddTab", UI_TAB_EVENTS[evt.GetId()])

        elif evt.GetId() in UI_LAYOUT_EVENTS:
            obs.trigger("UILayoutEvent", UI_LAYOUT_EVENTS[evt.GetId()])

        elif evt.GetId() in LIGHT_EVENTS:
            obs.trigger("AddLight", LIGHT_EVENTS[evt.GetId()])

        elif evt.GetId() is EVT_ADD_CAMERA:
            obs.trigger("AddCamera")

        elif evt.GetId() in OBJECT_EVENTS:
            obs.trigger("AddObject", OBJECT_EVENTS[evt.GetId()])

        elif evt.GetId() in self.user_layout_menus.keys():
            obs.trigger("LoadUserLayout", self.user_layout_menus[evt.GetId()])

        elif evt.GetId() == EVT_CLOSE_APP:
            obs.trigger("EvtCloseApp")

        evt.Skip()
