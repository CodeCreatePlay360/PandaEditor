import os
import webbrowser
import wx
import editor.commands as commands

from thirdparty.event.observable import Observable
from editor.utils.exceptionHandler import try_execute, try_execute_1
from panda3d.core import BitMask32
from editor.commandManager import CommandManager


EDITOR_STATE = 0
GAME_STATE = 1

MAX_COMMANDS_COUNT = 12

TAG_IGNORE = "SELECT_IGNORE"
TAG_PICKABLE = "PICKABLE"

ED_GEO_MASK = BitMask32.bit(0)
GAME_GEO_MASK = BitMask32.bit(1)

FILE_EXTENSIONS_ICONS_PATH = "src/editor/resources/icons/fileExtensions"
ICONS_PATH = "src/editor/resources/icons"
MODELS_PATH = "src/editor/resources"
MODELS_PATH_2 = "src/editor/resources/models"

DEFAULT_PROJECT_PATH = "src/Default Project"

# asset resources
POINT_LIGHT_MODEL = MODELS_PATH + "\\" + "Pointlight.egg.pz"
DIR_LIGHT_MODEL = MODELS_PATH + "\\" + "Dirlight.egg.pz"
SPOT_LIGHT_MODEL = MODELS_PATH + "\\" + "Spotlight.egg.pz"
AMBIENT_LIGHT_MODEL = MODELS_PATH + "\\" + "AmbientLight.obj"

CAMERA_MODEL = MODELS_PATH + "\\" + "camera.egg.pz"

CUBE_PATH = MODELS_PATH_2 + "\\" + "cube.fbx"
CAPSULE_PATH = MODELS_PATH_2 + "\\" + "capsule.fbx"
CONE_PATH = MODELS_PATH_2 + "\\" + "cone.fbx"
PLANE_PATH = MODELS_PATH_2 + "\\" + "plane.fbx"

command_manager = CommandManager()
obs = Observable()  # the event manager object
p3d_app = None
selected_resource_item = None  # selected resource item
selected_np = None


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


class DirectoryEventHandler:
    """handler all events related to project resources"""

    @staticmethod
    @obs.on("DirectoryEvent")
    def on_directory_event(*args):
        proj_browser = object_manager.get("ProjectBrowser")
        le = object_manager.get("LevelEditor")

        proj_browser.save_state()  # for example currently selected items
        proj_browser.create_or_rebuild_tree("", rebuild_event=True)  # rebuild resources panel

        # reload all the resources
        le.load_all_mods(proj_browser.resources["py"])  # reload all user mods and editor plugins
        le.load_text_files(proj_browser.resources["txt"])  # reload all text files

        proj_browser.reload_state()

        # update properties panel
        # DO not call this here, it is also called in le.load_all_mods.
        # LevelEditorEventHandler.update_properties_panel()


class LevelEditorEventHandler:
    """handles all events coming from level editor"""

    @staticmethod
    @obs.on("LevelEditorEvent")
    def on_le_event(*args):
        if args[0] in le_event_handler.keys():
            le_event_handler[args[0]](*args[1:])

    @staticmethod
    def on_le_start():
        pass

    @staticmethod
    def on_scene_start(*args):
        scene_graph = object_manager.get("SceneGraphPanel")
        le = object_manager.get("LevelEditor")
        scene_graph.init(le.active_scene.render)

    @staticmethod
    def on_enable_ed_mode(*args):
        scene_graph = object_manager.get("SceneGraphPanel")
        scene_graph.save_state()
        scene_graph.rebuild(object_manager.get("LevelEditor").active_scene.render)  # update SceneGraphPanel panel
        scene_graph.reload_state()

        # x_form task updates inspector panel according to current selection
        LevelEditorEventHandler.on_xform_task()

    @staticmethod
    def on_enable_game_mode(*args):
        pass

    @staticmethod
    @obs.on("OnAddNodePath")
    def on_add_np(nps):
        scene_graph = object_manager.get("SceneGraphPanel")
        scene_graph.add_np(nps)

    @staticmethod
    @obs.on("UpdatePropertiesPanel")
    def update_properties_panel(*args):
        """update properties panel based on currently selected resource or scene item"""

        le = object_manager.get("LevelEditor")
        proj_browser = object_manager.get("ProjectBrowser")
        properties_panel = object_manager.get("PropertiesPanel")
        scene_graph_panel = object_manager.get("SceneGraphPanel")

        # ===================================================================================================== #
        # if any resources are selected, than layout their properties
        selection = proj_browser.GetSelection()
        if selection:
            selection = proj_browser.GetItemText(selection)
            selection = selection.split(".")[0]

        module = le.get_module(selection)  # TODO replace this with is_resource
        if module:
            properties_panel.layout_object_properties(module, module._name, module.get_properties())
            return

        # ===================================================================================================== #
        # if any scene item is selected than layout its properties
        np = scene_graph_panel.get_selected_np()
        if np:
            properties_panel.layout_object_properties(np, np.get_name(), np.get_properties())
            return

        # ===================================================================================================== #
        # else resets object inspection panel
        properties_panel.reset()

    def toggle_scene_lights(val=None):
        le = object_manager.get("LevelEditor")

        if val is None:
            # invert scene lights on status
            current_status = le.toggle_scene_lights()
        else:
            current_status = val

        # change graphics
        wx_main = object_manager.get("WxMain")
        if current_status:
            wx_main.lights_toggle_btn.SetBitmap(wx_main.lights_on_icon)
        elif not current_status:
            wx_main.lights_toggle_btn.SetBitmap(wx_main.lights_off_icon)

        wx_main.aui_manager.Update()

    @staticmethod
    @obs.on("AddLight")
    def add_light(light):
        object_manager.get("LevelEditor").add_light(light)

    @staticmethod
    @obs.on("AddCamera")
    def add_camera():
        # print("currently support is limited to only camera per scene...!")
        object_manager.get("LevelEditor").add_camera()

    @staticmethod
    @obs.on("AddObject")
    def add_object(path):
        object_manager.get("LevelEditor").add_object(path)

    @staticmethod
    def on_remove_selected():
        def on_ok(*args):
            le = object_manager.get("LevelEditor")
            scene_graph_panel = object_manager.get("SceneGraphPanel")
            properties_panel = object_manager.get("PropertiesPanel")

            selections = []
            for np in le.selection.selected_nps:
                selections.append(np)
            le.selection.deselect_all()

            scene_graph_panel.on_remove_nps(selections)
            le.remove_selected_nps(selections)
            properties_panel.reset()

        wx_main = object_manager.get("WxMain")
        dm = wx_main.dialogue_manager
        dm.create_dialog("YesNoDialog", "Delete Item",
                         dm,
                         descriptor_text="Are you sure you want to delete this selection ?",
                         ok_call=on_ok)

    @staticmethod
    def on_remove_nodepaths(self):
        """This event is called after node paths have been removed... for any cleanup operations"""
        pass

    @staticmethod
    def np_selected(nps):
        if len(nps) > 0:
            np = nps[0]

            object_manager.get("PropertiesPanel").layout_object_properties(np, np.get_name(), np.get_properties())
            object_manager.get("ProjectBrowser").UnselectAll()
            object_manager.get("SceneGraphPanel").select_np(nps)

    @staticmethod
    @obs.on("DeselectAllNps")
    def deselect_all():
        object_manager.get("PropertiesPanel").reset()
        object_manager.get("ProjectBrowser").UnselectAll()
        object_manager.get("SceneGraphPanel").deselect_all()

    @staticmethod
    @obs.on("XFormTask")
    def on_xform_task(force_update_all=False):
        """updates properties panel according to currently selected object"""
        pp = object_manager.get("PropertiesPanel")
        if pp.has_object():
            pp.update_properties_panel(force_update_all)


le_Evt_Start = "OnLevelEditorStart"
le_Evt_On_Scene_Start = "OnSceneStart"
le_Evt_On_Add_NodePath = "OnAddNodePath"
le_Evt_NodePath_Selected = "NodePathSelected"
le_Evt_Deselect_All = "DeselectAll"
le_Evt_Remove_NodePaths = "RemoveSelectedNodePaths"
le_EVT_On_Enable_Ed_Mode = "OnEnableEdMode"
le_Evt_On_Enable_Game_Mode = "OnEnableGameMode"

le_event_handler = {
    le_Evt_Start: LevelEditorEventHandler.on_le_start,
    le_Evt_On_Scene_Start: LevelEditorEventHandler.on_scene_start,
    le_Evt_On_Add_NodePath: LevelEditorEventHandler.on_add_np,
    le_Evt_NodePath_Selected: LevelEditorEventHandler.np_selected,
    le_Evt_Deselect_All: LevelEditorEventHandler.deselect_all,
    le_Evt_Remove_NodePaths: LevelEditorEventHandler.on_remove_selected,
    le_EVT_On_Enable_Ed_Mode: LevelEditorEventHandler.on_enable_ed_mode,
    le_Evt_On_Enable_Game_Mode: LevelEditorEventHandler.on_enable_game_mode, }


class ProjectEventHandler:
    """handler all project related events"""

    @staticmethod
    @obs.on("ProjectEvent")
    def on_proj_event(evt, *args):
        if evt == "AppendLibrary":
            ProjectEventHandler.append_library()

        elif evt == "SetProject":
            ProjectEventHandler.create_new_project()

        elif evt == "LoadDefaultProject":
            ProjectEventHandler.load_default_project()

        elif evt == "NewScene":
            ProjectEventHandler.start_new_scene()

        elif evt == "SwitchEdState":
            le = object_manager.get("LevelEditor")
            wx_main = object_manager.get("WxMain")

            # get the current editor state
            ed_state = le.ed_state  # 0 = editor, 1 = game_state

            if len(args) > 0:
                le.switch_state(args[0])

            elif ed_state == 0:
                le.switch_state(1)

            elif ed_state == 1:
                le.switch_state(0)

            # change graphics
            if le.ed_state == 1:
                wx_main.ply_btn.SetBitmap(wx_main.stop_icon)
            elif le.ed_state == 0:
                wx_main.ply_btn.SetBitmap(wx_main.play_icon)

            wx_main.aui_manager.Update()

        elif evt == "ToggleSceneLights":
            LevelEditorEventHandler.toggle_scene_lights()

    def load_default_project(self):
        pass

    @staticmethod
    def create_new_project(*args):
        le = object_manager.get("LevelEditor")
        wx_main = object_manager.get("WxMain")
        file_browser = object_manager.get("ProjectBrowser")

        if le.ed_state is GAME_STATE:
            print("ProjectEventHandler --> Exit game mode to create a new project.")
            return

        def on_ok(proj_name, proj_path):
            if not proj_name.isalnum():  # validate project name
                print("ProjectEventHandler --> project name should not be null and can"
                      " only consists of alphabets and digits.")
                return

            # validate project path and set project
            #  and os.listdir(proj_path) == 0
            if os.path.exists(proj_path) and os.path.isdir(proj_path):
                le.create_new_project(proj_path)

                file_browser.create_or_rebuild_tree(proj_path, rebuild_event=False)
                file_browser.Refresh()

                DirectoryEventHandler.on_directory_event()

                wx_main.SetTitle("PandaEditor " + "(" + proj_name + ")")

                dialog.Close()  # finally, close project dialog
            else:
                print("ProjectEventHandler --> unable to create a new project, probably path is invalid.")

        def on_cancel(*_args):
            pass

        wx_main = object_manager.get("WxMain")
        dm = wx_main.dialogue_manager
        dialog = dm.create_dialog("ProjectDialog", "PandaEditor", dm, ok_call=on_ok, cancel_call=on_cancel)
        return

    @staticmethod
    def open_project(*args):
        pass

    @staticmethod
    def start_new_scene(*args):
        le = object_manager.get("LevelEditor")

        if le.ed_state is GAME_STATE:
            print("Exit game mode to create a new scene..!")
            return

        dlg = wx.MessageDialog(parent=None,
                               message="Confirm start new scene ?",
                               caption="NewScene",
                               style=wx.YES | wx.NO | wx.ICON_QUESTION)
        res = dlg.ShowModal()
        if res == wx.ID_YES:
            le = object_manager.get("LevelEditor")
            le.create_new_scene()

    @staticmethod
    def append_library(*args):
        le = object_manager.get("LevelEditor")

        if le.ed_state is GAME_STATE:
            print("Exit game mode to append new library..!")
            return

        dir_dialog = wx.DirDialog(None, style=wx.DD_DEFAULT_STYLE)

        if dir_dialog.ShowModal() == wx.ID_OK:
            path = dir_dialog.GetPath()
            name = ""
            dlg = wx.TextEntryDialog(object_manager.get("WxMain"), 'LibraryName', 'Set Library Name', value="")
            if dlg.ShowModal() == wx.ID_OK:
                name = dlg.GetValue()
            if name == "":
                return

            if le.project.on_add_library(name, path):
                object_manager.get("ProjectBrowser").append_library(name, path)
                DirectoryEventHandler.on_directory_event()

    @staticmethod
    @obs.on("OnRemoveLibrary")
    def remove_library(lib_path):
        """event called when a library is removed"""
        le = object_manager.get("LevelEditor")
        le.project.on_remove_library(lib_path)
        DirectoryEventHandler.on_directory_event()

    @staticmethod
    @obs.on("ToolExecutionFailed")
    def plugin_execution_failed(tool_name):
        print("plugin {} execution failed", tool_name)


class UserModuleEvent:
    """Handle all events coming from UserModules"""

    @staticmethod
    @obs.on("UserModuleEvent")
    def user_module_event(evt):
        if evt == "PluginExecutionFailed":
            UserModuleEvent.plugin_execution_failed()

    @staticmethod
    def plugin_execution_failed(*args):
        print("plugin executing failed...!")
        le = object_manager.get("LevelEditor")
        le.unregister_editor_plugins()


class WxEventHandler:
    """Handles events coming from different wx widgets"""

    @staticmethod
    @obs.on("WxEvent")
    def on_wx_event(*args):
        if args[0] in wx_event_handler.keys():
            wx_event_handler[args[0]](*args[1:])

    @staticmethod
    @obs.on("OnNodePathSelected")
    def on_np_selected(args):
        le = object_manager.get("LevelEditor")
        le.selection.set_selected(args, append=len(args) > 1)
        le.update_gizmo()
        obs.trigger("UpdateInspector", *args)

    @staticmethod
    def add_model(*args):
        le = object_manager.get("LevelEditor")

        model_path = args[0]
        xx = model_path[len(le.project.project_path) + 1:]
        le.add_nodepath(xx)

    def add_actor(*args):
        le = object_manager.get("LevelEditor")

        actor_path = args[0]
        xx = actor_path[len(le.project.project_path) + 1:]
        le.add_actor(xx)

    @staticmethod
    @obs.on("UILayoutEvent")
    def evt_ui_layout(evt):
        if evt == "SaveUILayout":
            WxEventHandler.register_user_layout()

    @staticmethod
    def register_user_layout():
        wx_main = object_manager.get("WxMain")
        aui_mgr = wx_main.aui_manager

        def on_ok(layout_name):
            if layout_name == "":
                return

            if aui_mgr.save_current_layout(layout_name):
                wx_main.menu_bar.add_layout_menu(layout_name)

        # get a name for this layout from user
        dm = wx_main.dialogue_manager
        dm.create_dialog("TextEntryDialog", "NewEditorLayout", dm,
                         descriptor_text="Enter new layout name", ok_call=on_ok)

    @staticmethod
    @obs.on("LoadUserLayout")
    def load_user_layout(layout):
        wx_main = object_manager.get("WxMain")
        aui_mgr = wx_main.aui_manager

        if aui_mgr.load_layout(layout):
            print("loaded layout: ", layout)


ui_Evt_On_NodePath_Selected = "OnNodePathSelected"
ui_Evt_Load_Model = "LoadModel"
ui_Evt_Load_Actor = "LoadActor"
ui_Evt_Reparent_NodePath = "ReparentNodePath"

wx_event_handler = {ui_Evt_On_NodePath_Selected: WxEventHandler.on_np_selected,
                    ui_Evt_Load_Model: WxEventHandler.add_model,
                    ui_Evt_Load_Actor: WxEventHandler.add_actor}


# ---------------------------------------- LEVEL EDITOR EVENTs ---------------------------------------- #
# events emitted by level editor or related to level editor

@obs.on("OnSceneStart")
def on_scene_start():
    """should be called as soon as a new scene is started"""
    scene_graph = object_manager.get("SceneGraphPanel")
    le = object_manager.get("LevelEditor")
    scene_graph.init(le.active_scene.render)


@obs.on("OnAddObjects(s)")
def on_add_objects(objects: list):
    scene_graph = p3d_app.wx_main.scene_graph_panel.scene_graph
    scene_graph.add_np(objects)


@obs.on("RenameNPs")
def on_rename_nps(np):
    def on_ok(new_name: str):
        if old_name != new_name:
            command_manager.do(commands.RenameNPs(p3d_app, np, old_name, new_name))

    old_name = np.get_name()

    dm = p3d_app.wx_main.dialogue_manager
    dm.create_dialog("TextEntryDialog",
                     "Rename Item",
                     dm,
                     descriptor_text="RenameSelection",
                     ok_call=on_ok,
                     initial_text=old_name)


@obs.on("OnRenameNPs")
def rename_nps(np, new_name):
    scene_graph = p3d_app.wx_main.scene_graph_panel.scene_graph
    scene_graph.on_item_rename(np, new_name)
    LevelEditorEventHandler.update_properties_panel()


@obs.on("ReparentNPs")
def reparent_np(src_np, target_np):
    le = p3d_app.level_editor
    if le.reparent_np(src_np, target_np):
        scene_graph = p3d_app.wx_main.scene_graph_panel.scene_graph
        scene_graph.reparent(src_np, target_np)


@obs.on("RemoveNPs")
def remove_nps(objects: list):
    def on_ok():
        command_manager.do(commands.RemoveObjects(p3d_app, objects))

    wx_main = p3d_app.wx_main

    dm = wx_main.dialogue_manager
    dm.create_dialog("YesNoDialog", "Remove selections",
                     dm,
                     descriptor_text="Confirm remove selection(s) ?",
                     ok_call=on_ok)


@obs.on("OnRemoveNPs")
def on_remove_nps(nps):
    """on remove nps is called just before permanently removing nps"""
    scene_graph_panel = p3d_app.wx_main.scene_graph_panel.scene_graph
    inspector_panel = p3d_app.wx_main.inspector_panel

    scene_graph_panel.on_remove_nps(nps)
    inspector_panel.reset()


@obs.on("OnSelectNPs")
def on_select_objects(objects: list):
    if len(objects) > 0:
        np = objects[0]
        object_manager.get("PropertiesPanel").layout_object_properties(np, np.get_name(), np.get_properties())
        object_manager.get("ProjectBrowser").UnselectAll()
        object_manager.get("SceneGraphPanel").select_np(objects)


@obs.on("OnDeselectAllNPs")
def on_deselect_all():
    object_manager.get("PropertiesPanel").reset()
    # object_manager.get("ProjectBrowser").UnselectAll()
    object_manager.get("SceneGraphPanel").deselect_all()


@obs.on("ToggleSceneLights")
def toggle_lights(value):
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


# ---------------------------------------- Wx EVENTs ---------------------------------------- #
# events emitted by wx-widgets

@obs.on("ResourceItemSelected")
def on_tree_item_select(selections):
    """event called when a resource item is selected in resource browser"""

    def on_module_selected(module):
        inspector_panel.layout_object_properties(module, module._name, module.get_properties())

    def on_txt_file_selected(txt_file):
        inspector_panel.set_text(txt_file)

    le = object_manager.get("LevelEditor")
    le.deselect_all()
    inspector_panel = object_manager.get("PropertiesPanel")

    for file_name, data in selections:
        # try to get module from level editor
        name = file_name.split(".")[0]

        if le.is_module(name):
            # if it's a user module
            on_module_selected(le.get_module(name))

        elif le.is_text_file(name):
            # if it's a text file
            on_txt_file_selected(le.get_text_file(name))

        else:
            inspector_panel.reset()


@obs.on("OnSelectSceneGraphItem")
def on_select_scene_graph_item(nps):
    p3d_app.level_editor.set_selected(nps)


@obs.on("PropertyModified")
def property_modified(*args):
    """should be called when a wx-property from object inspector is modified"""
    # object_manager.get("PropertiesPanel").update_properties_panel(*args)
    le = p3d_app.level_editor
    le.update_gizmo()


@obs.on("UpdateInspector")
def update_inspector(*args):
    pp = object_manager.get("PropertiesPanel")
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


@obs.on("LoadEdPluginPanel")
def add_panel(panel):
    """event called when a request to a new tab is made from main menu bar"""
    p3d_app.wx_main.add_panel(panel)


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


@obs.on("ResizeEvent")
def resize_event(*args):
    """emitted when window is resized, can be called manually for example
    to update aspect ratio"""

    if p3d_app:
        show_base = p3d_app.show_base
        level_editor = p3d_app.level_editor

        show_base.update_aspect_ratio()
        for user_module in level_editor.user_modules:
            user_module.on_resize_event()


@obs.on("OpenSocialMediaLink")
def open_social_media_link(link: str):
    if link == "Patreon":
        webbrowser.open("https://www.patreon.com/PandaEditor_", new=2)

    elif link == "Panda3dDiscourse":
        webbrowser.open("https://discourse.panda3d.org/t/pandaeditor-alpha-release/28408", new=2)

    elif link == "Discord":
        webbrowser.open("https://rutracker.org/forum/viewtopic.php?t=6100355", new=2)


@obs.on("EvtCloseApp")
def exit_app(close_wx=True):
    if close_wx:
        object_manager.get("WxMain").Close()
    object_manager.get("P3dApp").Quit()


# ---------------------------------------- All other events ---------------------------------------- #
@obs.on("CleanUnusedLoadedNPs")
def clean_unused_loaded_nps(nps_to_remove):
    # TODO explanation
    p3d_app.level_editor.remove_nps(nps_to_remove, permanent=True)
