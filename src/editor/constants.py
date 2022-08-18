import webbrowser
import wx
import editor.commands as commands

from thirdparty.event.observable import Observable
from editor.utils.exceptionHandler import try_execute, try_execute_1
from panda3d.core import BitMask32
from editor.commandManager import CommandManager
from wx.aui import AUI_BUTTON_STATE_NORMAL, AUI_BUTTON_STATE_PRESSED

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


command_manager = CommandManager()
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
            pp.update_properties_panel(force_update_all)


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


@obs.on("OnRemoveLibrary")
def remove_library(lib_path):
    """event called to remove a library"""
    pass


@obs.on("CreateAsset")
def create_asset(asset_type, path):
    def indent_file(_file, spaces):
        # add indentation by adding empty spaces
        for i in range(spaces):
            _file.write(" ")

    def write_p3d_module(mod_name, base_class, class_name, _is_ed_plugin=False):
        with open(path, "w") as file_:
            file_.write("import math\n")
            file_.write("import panda3d.core as p3d_core\n")
            file_.write("from editor.core.{0} import {1}\n\n\n".format(mod_name, base_class))

            # class header and init method
            file_.write("class {0}({1}):".format(class_name, base_class))
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
            file_.write("# this method is called evert frame\n")
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

    # choose a base class depending on _type
    is_ed_plugin = False

    if asset_type == "p3d_user_mod":
        module_name = "runtimeModule"
        base_cls = "RuntimeModule"
        path += ".py"

    elif asset_type == "p3d_ed_tool":
        module_name = "editorPlugin"
        base_cls = "EditorPlugin"
        path += ".py"
        is_ed_plugin = True

    elif asset_type == "txt_file":
        path += ".txt"
        with open(path, "w") as txt_file:
            txt_file.write("pass\n")
        return

    else:
        module_name = "object"
        base_cls = "object"
        path += ".py"
    # ------------------------------------------ #

    cls_name = path.split(".")[0]
    cls_name = cls_name.split("/")[-1]
    cls_name = cls_name[0].upper() + cls_name[1:]  # capitalize class name

    # write_to_file(module_name, base_cls, cls_name)
    if module_name == "object":
        try_execute(write_py_module, cls_name, base_cls)
    else:
        try_execute(write_p3d_module, module_name, base_cls, cls_name, is_ed_plugin)


@obs.on("OnSceneStart")
def on_scene_start():
    """should be called after a new scene is created"""
    scene_graph = object_manager.get("SceneGraph")
    le = object_manager.get("LevelEditor")
    scene_graph.init(le.active_scene.render)


@obs.on("OnAddObjects(s)")
def on_add_objects(objects: list):
    """should be called after adding new node_paths in scene graph"""
    scene_graph = object_manager.get("SceneGraph")
    scene_graph.add_np(objects)


# ---------------------------------------- ** ---------------------------------------- #
# Events related to LevelEditor
@obs.on("EditorUpdate")
def update(*args):
    pass


@obs.on("OnLevelEditorFinishInit")
def on_level_editor_finish_init():
    inspector = object_manager.get("InspectorPanel")
    scene_graph = object_manager.get("SceneGraph")
    resource_tree = object_manager.get("ResourceTree")

    # set current inspector to world,
    # manually select the world button on selection grid as well.
    inspector.selection_grid.select_button(1)

    # expand scene graph
    scene_graph.ExpandAll()

    # start the project directory watcher
    resource_tree.schedule_dir_watcher()


@obs.on("SwitchEdState")
def switch_ed_state(state=None):
    # print("switch ed state", state)

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
    elif le.ed_state == 0:
        wx_main.ply_btn.SetBitmap(wx_main.play_icon)

    wx_main.aui_manager.Update()


@obs.on("OnEnableEditorState")
def on_enable_ed_state():
    scene_graph = object_manager.get("SceneGraph")
    le = object_manager.get("LevelEditor")

    scene_graph.save_state()
    scene_graph.rebuild(le.active_scene.render)  # update SceneGraphPanel panel
    scene_graph.reload_state()

    # x_form task updates inspector panel according to current selection
    LevelEditorEventHandler.on_xform_task()


@obs.on("RenameNPs")
def rename_nps(np):
    def on_ok(new_name: str):
        if old_name != new_name:
            command_manager.do(commands.RenameNPs(object_manager.get("P3dApp"), np, old_name, new_name))

    old_name = np.get_name()

    dm = object_manager.get("WxMain").dialogue_manager
    dm.create_dialog("TextEntryDialog",
                     "Rename Item",
                     dm,
                     descriptor_text="RenameSelection",
                     ok_call=on_ok,
                     initial_text=old_name)


@obs.on("OnRenameNPs")
def on_rename_nps(np, new_name):
    scene_graph = object_manager.get("SceneGraph")
    scene_graph.on_item_rename(np, new_name)
    LevelEditorEventHandler.update_properties_panel()


@obs.on("ReparentNPs")
def reparent_nps(src_np, target_np):
    """re-parents target_np to src_np via LevelEditor.reparent_np"""
    command_manager.do(commands.ReparentNPs(object_manager.get("P3dApp"), src_np, target_np))


@obs.on("OnReparentNPs")
def on_reparent_nps(src_np, target_np):
    """executed after a re-parent operation in scene graph"""
    scene_graph = object_manager.get("SceneGraph")
    scene_graph.reparent(src_np, target_np)


@obs.on("RemoveNPs")
def remove_nps(objects: list):
    def on_ok():
        command_manager.do(commands.RemoveObjects(object_manager.get("P3dApp"), objects))

    wx_main = object_manager.get("WxMain")

    dm = wx_main.dialogue_manager
    dm.create_dialog("YesNoDialog", "Remove selections",
                     dm,
                     descriptor_text="Confirm remove selection(s) ?",
                     ok_call=on_ok)


@obs.on("OnRemoveNPs")
def on_remove_nps(nps):
    """on remove nps is called just before permanently removing nps"""
    scene_graph_panel = object_manager.get("SceneGraph")
    inspector_panel = object_manager.get("InspectorPanel")

    scene_graph_panel.on_remove_nps(nps)
    inspector_panel.reset()


@obs.on("OnSelectNPs")
def on_select_nps(objects: list):
    np = objects[0]
    object_manager.get("InspectorPanel").layout_object_properties(np, np.get_name(), np.get_properties())
    # object_manager.get("ResourceTree").UnselectAll()
    object_manager.get("ResourceTilesPanel").deselect_all()
    object_manager.get("SceneGraph").select_np(objects)


@obs.on("OnDeselectAllNPs")
def on_deselect_all_nps():
    """called after levelEditor.deselect_all, only if length of deselected node-paths is greater than 0"""

    inspector = object_manager.get("InspectorPanel")
    scene_graph = object_manager.get("SceneGraph")

    inspector.reset()
    scene_graph.UnselectAll()


@obs.on("ToggleSceneLights")
def toggle_lights(value=None):
    le = object_manager.get("LevelEditor")
    wx_main = object_manager.get("WxMain")

    if value is None:
        # invert scene lights on or off status
        current_status = le.toggle_scene_lights()
    else:
        current_status = value

    # change graphics
    if current_status:
        wx_main.lights_toggle_btn.SetBitmap(wx_main.lights_on_icon)

    elif not current_status:
        wx_main.lights_toggle_btn.SetBitmap(wx_main.lights_off_icon)

    wx_main.aui_manager.Update()


@obs.on("PluginFailed")
def plugin_execution_failed(plugin):
    print("Plugin {0} execution failed".format(plugin._name))
    le = object_manager.get("LevelEditor")
    le.unregister_editor_plugins(plugin)


@obs.on("CleanUnusedLoadedNPs")
def clean_unused_loaded_nps(nps_to_remove):
    # TODO explanation
    object_manager.get("LevelEditor").remove_nps(nps_to_remove, permanent=True)


# ---------------------------------------- Wx EVENTs ---------------------------------------- #
# events emitted by wx-widgets
@obs.on("SwitchEdViewportStyle")
def switch_ed_viewport_style():
    """toggles between minimized and maximized game viewport"""
    le = object_manager.get("LevelEditor")
    le.switch_ed_viewport_style()


@obs.on("OnResourceItemSelected")
def on_resource_item_selected(selections):
    """event called when an item (some project folder) is selected in resource browser"""
    resource_browser = object_manager.get("ResourceBrowser")
    resource_tiles = resource_browser.tiles_panel
    resource_tiles.set_from_selections(selections)


@obs.on("OnResourceTileSelected")
def on_resource_tile_selected(tile_data):
    def on_module_selected(module):
        inspector_panel.layout_object_properties(module, module._name, module.get_properties())

    def on_txt_file_selected(txt_file):
        inspector_panel.set_text_from_file(txt_file)

    le = object_manager.get("LevelEditor")
    inspector_panel = object_manager.get("InspectorPanel")

    if len(le.selection.selected_nps) > 0:
        le.deselect_all()  # this also triggers deselect on scene graph

    file_name = tile_data
    file_name = file_name.split(".")[0]

    if le.is_module(file_name):
        on_module_selected(le.get_module(file_name))

    elif le.is_text_file(file_name):
        on_txt_file_selected(le.get_text_file(file_name))

    else:
        inspector_panel.reset()


@obs.on("OnSelectSceneGraphItem")
def on_select_scene_graph_item(nps):
    # do not call deselect on resource tree or tiles panel, it is called in "constants.on_select_objects",
    # triggered after call to level_editor.set_selected
    le = object_manager.get("LevelEditor")
    le.set_selected(nps)


@obs.on("DeselectAll")
def deselect_all():
    le = object_manager.get("LevelEditor")
    # resource_tree = object_manager.get("ResourceTree")
    resource_tiles = object_manager.get("ResourceBrowser").tiles_panel
    inspector = object_manager.get("InspectorPanel")
    scene_graph = object_manager.get("SceneGraph")

    if len(le.selection.selected_nps) > 0:
        le.deselect_all()

    scene_graph.UnselectAll()
    # resource_tree.UnselectAll()
    resource_tiles.deselect_all()
    inspector.reset()


@obs.on("PropertyModified")
def property_modified(*args):
    """should be called when a wx-property from object inspector is modified"""
    le = object_manager.get("LevelEditor")
    le.update_gizmo()


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


@obs.on("SaveUILayout")
def register_user_layout(*args):
    wx_main = object_manager.get("WxMain")
    wx_main.save_current_layout()


@obs.on("OnPluginMenuEntrySelected")
def on_plugin_menu_entry_selected(plugin_name):
    print(plugin_name)


@obs.on("LoadUserLayout")
def load_user_layout(layout):
    wx_main = object_manager.get("WxMain")
    wx_main.aui_manager.load_layout(layout)


@obs.on("DirectoryEvent")
def on_directory_event(*args):
    resource_browser = object_manager.get("ResourceBrowser")
    le = object_manager.get("LevelEditor")

    resource_tree = resource_browser.resource_tree
    tiles_panel = resource_browser.tiles_panel

    resource_tree.save_state()  # for example currently selected items
    tiles_panel.save_state()
    resource_tree.create_or_rebuild_tree("", rebuild_event=True)  # rebuild resources panel

    # reload all the resources
    le.load_all_mods(resource_tree.resources["py"])  # reload all user mods and editor plugins
    le.load_text_files(resource_tree.resources["txt"])  # reload all text files

    resource_tree.reload_state()
    tiles_panel.reload_state()

    # update properties panel
    # DO not call this here as it is also called from le.load_all_mods.
    # LevelEditorEventHandler.update_properties_panel()


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
    object_manager.get("P3dApp").Quit()
