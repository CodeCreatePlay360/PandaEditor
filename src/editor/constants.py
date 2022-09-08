import webbrowser
import panda3d.core as p3d_core
import wx
import editor.nodes as ed_nodepaths

from thirdparty.event.observable import Observable
from editor.utils.exceptionHandler import try_execute, try_execute_1
from panda3d.core import BitMask32

EDITOR_STATE = 0
GAME_STATE = 1

Viewport_Mode_Editor = 0
Viewport_Mode_Game = 1

EditorPlugin = "EditorPlugin"
RuntimeModule = "RuntimeModule"
TAG_PICKABLE = "PICKABLE"

MAX_COMMANDS_COUNT = 20

ED_GEO_MASK = BitMask32.bit(0)
GAME_GEO_MASK = BitMask32.bit(1)

# supported extensions -------------------------------------------------
MODEL_EXTENSIONS = ["fbx", "obj", "egg", "bam", "pz", "gltf"]
TEXTURE_EXTENSIONS = []

# various paths --------------------------------------------------------
# icons
FILE_EXTENSIONS_ICONS_PATH = "src/editor/resources/icons/fileExtensions"
ICONS_PATH = "src/editor/resources/icons"

REFRESH_ICON = ICONS_PATH + "//" + "arrow_refresh.png"
MAGNIFYING_GLASS_ICON = ICONS_PATH + "//" + "magnifyingGlassIcon.png"
SEARCH_CANCEL_ICON = ICONS_PATH + "//" + "cancel.png"

# project
DEFAULT_PROJECT_PATH = "src/Default Project"

# models
MODELS_PATH = "src/editor/resources"

POINT_LIGHT_MODEL = "models/Pointlight.egg.pz"
DIR_LIGHT_MODEL = "models/Dirlight.egg"
SPOT_LIGHT_MODEL = "models/Spotlight.egg.pz"
AMBIENT_LIGHT_MODEL = "models/AmbientLight.obj"

CAMERA_MODEL = "models/camera.egg.pz"

CUBE_PATH = "models/cube.fbx"
CAPSULE_PATH = "models/capsule.fbx"
CONE_PATH = "models/cone.fbx"
PLANE_PATH = "models/plane.fbx"

# np_types
# lights
POINT_LIGHT = "__PointLight__"
DIRECTIONAL_LIGHT = "__DirectionalLight__"
SPOT_LIGHT = "__SpotLight__"
AMBIENT_LIGHT = "__AmbientLight__"
# camera
CAMERA_NODEPATH = "__CameraNodePath__"
# models / actors
NODEPATH = "__NodePath__"
ACTOR_NODEPATH = "__ActorNodePath__"


LIGHT_MAP = {POINT_LIGHT: (p3d_core.PointLight, ed_nodepaths.EdPointLight, POINT_LIGHT_MODEL),
             SPOT_LIGHT: (p3d_core.Spotlight, ed_nodepaths.EdSpotLight, SPOT_LIGHT_MODEL),
             DIRECTIONAL_LIGHT: (p3d_core.DirectionalLight, ed_nodepaths.EdDirectionalLight, DIR_LIGHT_MODEL),
             AMBIENT_LIGHT: (p3d_core.AmbientLight, ed_nodepaths.EdAmbientLight, AMBIENT_LIGHT_MODEL)}

NODE_TYPE_MAP = {DIRECTIONAL_LIGHT: ed_nodepaths.EdDirectionalLight,
                 POINT_LIGHT: ed_nodepaths.EdPointLight,
                 SPOT_LIGHT: ed_nodepaths.EdSpotLight,
                 AMBIENT_LIGHT: ed_nodepaths.EdAmbientLight,
                 CAMERA_NODEPATH: ed_nodepaths.CameraNodePath,
                 NODEPATH: ed_nodepaths.BaseNodePath,
                 ACTOR_NODEPATH: None}


obs = Observable()  # the event manager object


class ObjectManager:
    def __init__(self):
        self.object_dictionary = {}

    def add_object(self, name, obj):
        if not self.object_dictionary.__contains__(name):
            self.object_dictionary[name] = obj

    def remove_object(self, name):
        if self.object_dictionary.__contains__(name):
            self.object_dictionary.pop(name)

    def get(self, name):
        if self.object_dictionary.__contains__(name):
            return self.object_dictionary[name]

        return None

    def remove_all_objects(self):
        self.object_dictionary.clear()


object_manager = ObjectManager()


class LevelEditorEventHandler:
    """handles all events coming from level editor"""

    @staticmethod
    @obs.on("XFormTask")
    def on_xform_task(force_update_all=False):
        """updates properties panel according to currently selected object"""
        pp = object_manager.get("InspectorPanel")
        if pp.has_object():
            pp.update_properties_panel(force_update_all=force_update_all)


# ---------------------------------------- ** ---------------------------------------- #
# Events mostly related to project

@obs.on("CreateNewProject")
def create_new_project(*args):
    print("create new project")


@obs.on("OpenProject")
def open_project(*args):
    print("open project")


@obs.on("BuildProject")
def build_project(*args):
    print("build project")


@obs.on("CreateNewSession")
def create_new_session(*args):
    le = object_manager.get("LevelEditor")

    if le.ed_state is GAME_STATE:
        print("Exit game mode to create a new scene..!")
        return

    dlg = wx.MessageDialog(parent=None,
                           message="Confirm create new session ?",
                           caption="NewSession",
                           style=wx.YES | wx.NO | wx.ICON_QUESTION)
    res = dlg.ShowModal()
    if res == wx.ID_YES:
        le = object_manager.get("LevelEditor")
        le.create_new_scene()


@obs.on("OpenSession")
def open_session(*args):
    print("open session")


@obs.on("SaveSession")
def save_session(*args):
    print("save session")


@obs.on("SaveSessionAs")
def save_session_as(*args):
    print("save session as")


@obs.on("AppendLibrary")
def append_library(*args):
    le = object_manager.get("LevelEditor")
    resource_tree = object_manager.get("ResourceTree")

    if le.ed_state is GAME_STATE:
        print("Exit game mode to append new library..!")
        return

    dir_dialog = wx.DirDialog(None, style=wx.DD_DEFAULT_STYLE)

    if dir_dialog.ShowModal() == wx.ID_OK:
        path = dir_dialog.GetPath()
        dlg = wx.TextEntryDialog(object_manager.get("WxMain"), 'LibraryName', 'Set Library Name', value="")
        if dlg.ShowModal() == wx.ID_OK:
            name = dlg.GetValue()

            if name != "":
                resource_tree.append_library(name, path)


@obs.on("CreateAsset")
def create_asset(asset_type, path):
    def indent_file(_file, spaces):
        # add indentation by adding empty spaces
        for i in range(spaces):
            _file.write(" ")

    def write_p3d_module(base_module, base_class, new_class_name):
        with open(path, "w") as file_:
            file_.write("import math\n")
            file_.write("import panda3d.core as p3d_core\n")
            file_.write("from editor.core.{0} import {1}\n\n\n".format(base_module, base_class))

            # class header and init method
            file_.write("class {0}({1}):".format(new_class_name, base_class))
            file_.write("\n")
            indent_file(file_, 4)
            file_.write("def __init__(self, *args, **kwargs):\n")

            indent_file(file_, 8)
            file_.write(base_class + ".__init__(self, *args, **kwargs)\n")

            indent_file(file_, 8)
            file_.write("# __init__ should not contain anything except for variable declaration...!\n\n")

            # write start method
            indent_file(file_, 4)
            file_.write("def on_start(self):\n")
            indent_file(file_, 8)
            file_.write("# this method is called only once\n")
            indent_file(file_, 8)
            file_.write("pass\n\n")

            # write update method
            indent_file(file_, 4)
            file_.write("def on_update(self):\n")
            indent_file(file_, 8)
            file_.write("# this method is called every frame\n")
            indent_file(file_, 8)
            file_.write("pass\n\n")

    def write_py_module(class_name, base_class):
        with open(path, "w") as file_:
            file_.write("import math\n\n\n")

            # class header and init method
            file_.write("class {0}({1}):".format(class_name, base_class))
            file_.write("\n")
            indent_file(file_, 4)
            file_.write("def __init__(self, *args, **kwargs):\n")

            indent_file(file_, 8)
            file_.write("pass\n")

    if asset_type == "p3d_user_mod":
        base_mod_name = "runtimeModule"
        base_class_name = "RuntimeModule"
        path += ".py"

    elif asset_type == "p3d_ed_tool":
        base_mod_name = "editorPlugin"
        base_class_name = "EditorPlugin"
        path += ".py"

    elif asset_type == "txt_file":
        path += ".txt"
        with open(path, "w") as txt_file:
            txt_file.write("pass\n")
        return

    else:
        base_mod_name = "object"
        base_class_name = "object"
        path += ".py"
    # ------------------------------------------ #

    cls_name = path.split(".")[0]
    cls_name = cls_name.split("/")[-1]
    cls_name = cls_name[0].upper() + cls_name[1:]  # capitalize class name

    # write_to_file(base_module, base_cls, new_cls_name)
    if base_mod_name == "object":
        try_execute(write_py_module, cls_name, base_class_name)
    else:
        try_execute(write_p3d_module, base_mod_name, base_class_name, cls_name)


@obs.on("OnSceneStart")
def on_scene_start():
    """should be called after a new scene is created"""
    wx_main = object_manager.get("WxMain")
    inspector = object_manager.get("InspectorPanel")
    scene_graph = object_manager.get("SceneGraph")
    resource_tree = object_manager.get("ResourceTree")
    level_editor = object_manager.get("LevelEditor")

    wx_main.freeze()

    # set a default active object for inspector
    inspector.inspector_type_btns.select_button(0)
    cube = level_editor.active_scene.render.find("**/cube.fbx").getPythonTag(TAG_PICKABLE)
    inspector.set_object(cube, cube.get_name(), cube.get_properties())

    scene_graph.ExpandAll()  # expand scene graph
    resource_tree.schedule_dir_watcher()  # start the project directory watcher

    wx_main.thaw()


@obs.on("OnSceneClean")
def on_scene_clean(scene):
    """is called just before the scene is about to be cleaned"""
    pass

# ---------------------------------------- ** ---------------------------------------- #
# Events related to LevelEditor


@obs.on("OnAddNPs")
def on_add_nps(nps):
    app = object_manager.get("P3dApp")
    wx_main = object_manager.get("WxMain")
    scene_graph = object_manager.get("SceneGraph")
    inspector = object_manager.get("InspectorPanel")
    resource_tiles = object_manager.get("ResourceTilesPanel")

    wx_main.freeze()

    app.level_editor.deselect_all()
    resource_tiles.deselect_all()

    app.level_editor.set_selected(nps)

    for np in nps:
        scene_graph.add(np)
    scene_graph.select(nps)
    inspector.layout_auto()

    wx_main.thaw()


@obs.on("OnRemoveNPs")
def on_remove_nps(nps):
    app = object_manager.get("P3dApp")
    scene_graph = object_manager.get("SceneGraph")
    inspector = object_manager.get("InspectorPanel")

    app.level_editor.deselect_all()
    scene_graph.on_remove(nps)
    inspector.layout_auto()


@obs.on("OnDeselectAllNPs")
def on_deselect_all_nps():
    object_manager.get("SceneGraph").UnselectAll()
    inspector = object_manager.get("InspectorPanel")
    inspector.layout_auto()


@obs.on("SwitchEdState")
def switch_ed_state(state=None):
    le = object_manager.get("LevelEditor")
    wx_main = object_manager.get("WxMain")

    if state is None:
        ed_state = le.ed_state  # 0 = editor, 1 = game_state
        if ed_state == 0:
            le.switch_state(1)
        elif ed_state == 1:
            le.switch_state(0)
    else:
        ed_state = state
        le.switch_state(ed_state)

    # change graphics
    if le.ed_state == 1:
        wx_main.ply_btn.SetBitmap(wx_main.stop_icon)
        wx_main.playctrls_tb.ToggleTool(wx_main.ply_btn.GetId(), True)
    elif le.ed_state == 0:
        wx_main.ply_btn.SetBitmap(wx_main.play_icon)
        wx_main.playctrls_tb.ToggleTool(wx_main.ply_btn.GetId(), False)

    wx_main.playctrls_tb.Realize()


@obs.on("OnEnableEditorState")
def on_enable_ed_state():
    scene_graph = object_manager.get("SceneGraph")
    scene_graph.rebuild()

    pp = object_manager.get("InspectorPanel")
    if pp.has_object():
        pp.update_properties_panel(force_update_all=False)


@obs.on("OnEnableGameState")
def on_enable_ed_state():
    pass


@obs.on("ToggleSceneLights")
def toggle_lights(value=None):
    le = object_manager.get("LevelEditor")
    wx_main = object_manager.get("WxMain")

    current_status = le.toggle_scene_lights()

    # change graphics
    if current_status:
        wx_main.lights_toggle_btn.SetBitmap(wx_main.lights_on_icon)
        wx_main.scene_ctrls_tb.ToggleTool(wx_main.lights_toggle_btn.GetId(), True)
    elif not current_status:
        wx_main.lights_toggle_btn.SetBitmap(wx_main.lights_off_icon)
        wx_main.scene_ctrls_tb.ToggleTool(wx_main.lights_toggle_btn.GetId(), False)

    wx_main.scene_ctrls_tb.Realize()


@obs.on("PluginFailed")
def plugin_execution_failed(plugin):
    le = object_manager.get("LevelEditor")
    le.unload_editor_plugin(plugin)


@obs.on("CleanUnusedLoadedNPs")
def clean_unused_loaded_nps(nps_to_remove):
    # TODO explanation
    object_manager.get("LevelEditor").remove_nps(nps_to_remove, permanent=True)


# ---------------------------------------- Wx EVENTs ---------------------------------------- #
# events emitted by wx-widgets
@obs.on("EditorReload")
def reload_editor(*args):
    le = object_manager.get("LevelEditor")
    wx_main = object_manager.get("WxMain")
    inspector = object_manager.get("InspectorPanel")
    resource_tree = object_manager.get("ResourceTree")
    tiles_panel = object_manager.get("ResourceTilesPanel")
    scene_graph = object_manager.get("SceneGraph")

    # save states of panels
    resource_tree.save_state()
    tiles_panel.save_state()
    scene_graph.save_state()

    obs.trigger("DeselectAll")

    wx_main.freeze()

    # rebuild resources tree AND reload all the resources
    resource_tree.create_or_rebuild_tree(le.project.project_path, rebuild_event=False)
    #
    le.load_all_mods(resource_tree.resources["py"])
    le.load_text_files(resource_tree.resources["txt"])
    # -----------------------------------------------------

    # reload scene graph
    scene_graph.rebuild()
    # scene_graph.UnselectAll()

    # brings things back to their pre-reload state
    resource_tree.reload_state()
    resource_tree.Refresh()
    tiles_panel.reload_state()
    scene_graph.reload_state()

    # layout the inspector
    inspector.layout_auto()

    wx_main.thaw()


@obs.on("SwitchEdViewportStyle")
def switch_ed_viewport_style():
    """toggles between minimized and maximized game viewport"""
    le = object_manager.get("LevelEditor")
    le.switch_ed_viewport_style()


@obs.on("OnResourceItemSelected")
def on_resource_item_selected(selections):
    """event called when an item (some project folder) is selected in resource browser"""
    resource_browser = object_manager.get("ResourceBrowser")
    wx_main = object_manager.get("WxMain")
    resource_tiles = object_manager.get("ResourceTilesPanel")

    wx_main.freeze()
    resource_tiles.set_from_selections(selections)
    wx_main.thaw()


@obs.on("OnResourceTileSelected")
def on_resource_tile_selected(file_path):
    def on_module_selected(module):
        inspector_panel.set_object(module, module.name, module.get_properties())

    def on_txt_file_selected(txt_file):
        inspector_panel.set_text(txt_file.text)

    le = object_manager.get("LevelEditor")
    inspector_panel = object_manager.get("InspectorPanel")
    wx_main = object_manager.get("WxMain")

    wx_main.freeze()
    le.deselect_all()  # this also triggers "OnDeselectAllNPs" event

    if le.is_module(file_path):
        on_module_selected(le.get_module(file_path))

    elif le.is_text_file(file_path):
        on_txt_file_selected(le.get_text_file(file_path))

    else:
        inspector_panel.reset()

    wx_main.thaw()


@obs.on("DeselectAll")
def deselect_all():
    le = object_manager.get("LevelEditor")
    resource_tiles = object_manager.get("ResourceTilesPanel")
    inspector = object_manager.get("InspectorPanel")
    scene_graph = object_manager.get("SceneGraph")

    if len(le.selection.selected_nps) > 0:
        le.deselect_all()

    scene_graph.UnselectAll()
    resource_tiles.deselect_all()
    inspector.reset()


@obs.on("PropertyModified")
def property_modified(property_):
    """is called after a wx-property is modified from inspector,
    call any post property modify event here"""
    le = object_manager.get("LevelEditor")
    le.update_gizmo()

    if property_.label in ["Near-Far", "Field Of View", "FilmSize"]:
        object_manager.get("P3dApp").show_base.update_aspect_ratio()


@obs.on("UpdateInspector")
def update_inspector(*args):
    # TODO WHERE is this coming from .... ?
    print("constants.UpdateInspector")
    pp = object_manager.get("")
    pr = object_manager.get("ProjectBrowser")
    le = object_manager.get("LevelEditor")

    if len(args) > 0:
        np = args[0]
    elif len(le.selection.selected_nps) > 0:
        np = le.selection.selected_nps[0]
        np = np.getPythonTag(TAG_PICKABLE)
    else:
        return

    pp.layout_object_properties(np, np.get_name(), np.get_properties())


@obs.on("ResizeEvent")
def resize_event(*args):
    """emitted when window is resized, can be called manually as well"""
    level_editor = object_manager.get("LevelEditor")
    show_base = object_manager.get("P3dApp").show_base

    # this event also gets called before initialization of level editor, so make sure it's not None
    if level_editor and show_base:
        show_base.update_aspect_ratio()
        for module in level_editor.user_modules:
            module.on_resize_event()


@obs.on("OnPluginMenuEntrySelected")
def on_plugin_menu_entry_selected(plugin_name):
    print(plugin_name)


@obs.on("OpenSocialMediaLink")
def open_social_media_link(link: str):
    if link == "Patreon":
        webbrowser.open("https://www.patreon.com/PandaEditor_", new=2)

    elif link == "Panda3dDiscourse":
        webbrowser.open("https://discourse.panda3d.org/t/pandaeditor-alpha-release/28408", new=2)

    elif link == "Discord":
        webbrowser.open("https://discord.gg/QU2y6q7G9F", new=2)


@obs.on("CloseApp")
def exit_app(close_wx=True):
    if close_wx:
        object_manager.get("WxMain").Close()
    object_manager.get("P3dApp").quit()
