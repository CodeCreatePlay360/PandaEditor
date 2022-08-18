import sys
import importlib
import traceback
import panda3d.core as p3d_core
import editor.core as ed_core
import editor.nodes as ed_node_paths
import editor.gizmos as gizmos
import editor.constants as constants
import editor.globals as ed_globals
import editor.commands as commands

from datetime import date
from direct.showbase.DirectObject import DirectObject
from direct.showbase.Loader import Loader
from direct.showbase.ShowBase import taskMgr
from editor.project import Project
from editor.selection import Selection
from editor.pluginManager import PluginsManager
from editor.editorSettings import EditorSettings


class LevelEditor(DirectObject):
    def __init__(self, panda_app, *args, **kwargs):
        """Actual Level / scene editor all editor systems should be initialized from here"""

        DirectObject.__init__(self)
        constants.object_manager.add_object("LevelEditor", self)

        self.app = panda_app

        self.project = Project(panda_app)
        self.editor_settings = EditorSettings(self)
        self.plugins_manager = PluginsManager()

        self.active_scene = None

        # gizmos, grid, selection
        self.grid_np = None
        self.selection = None
        self.gizmo_mgr_root_np = None
        self.gizmo = False
        self.gizmo_mgr = None
        self.active_gizmo = None  # position, rotation, or scale

        '''grid, selection and gizmos'''
        self.create_grid(200, 40, 5)
        self.setup_selection_system()
        self.setup_gizmo_manager()

        # create event map for various keyboard events and bind them
        self.key_event_map = {"q": (self.set_active_gizmo, "None"),
                              "w": (self.set_active_gizmo, "pos"),
                              "e": (self.set_active_gizmo, "rot"),
                              "r": (self.set_active_gizmo, "scl"),
                              "space": (self.toggle_gizmo_local, None),
                              "+": (self.gizmo_mgr.SetSize, 2),
                              "-": (self.gizmo_mgr.SetSize, 0.5),
                              "control-d": (self.on_duplicate_nps, None),
                              "x": (self.on_remove, None),
                              "control-z": (constants.command_manager.undo, None),

                              "mouse1": (self.on_mouse1_down, [False]),
                              "mouse2": (self.on_mouse2_down, None),

                              "mouse1-up": (self.on_mouse1_up, None),
                              "mouse2-up": (self.on_mouse2_up, None),

                              "shift-mouse1": (self.on_mouse1_down, [True]),
                              "control-mouse1": (self.on_mouse1_down, None)
                              }

        self.scene_lights_on = False  # scene lights are on or off ?
        self.mouse_1_down = False  # is mouse button 1 down ?
        self.mouse_2_down = False  # is mouse button 2 down ?
        self.ed_state = constants.EDITOR_STATE  # is current state editor or game state ?

        self.__game_viewport_maximized = False
        self.current_mouse_mode = None

        # editor update task
        self.update_task = None
        self.current_xform_time = 0
        self.x_form_delay = 0.1  # delay time before updating inspector panel
        self.update_task = taskMgr.add(self.update, 'EditorUpdateTask', sort=1)

        # available loaded resources
        # TODO replace this with ResourceHandler
        self.__loader = Loader(self.app.show_base)
        self.__ed_plugins = {}
        self.__user_modules = {}
        self.__text_files = {}
        # ---------------------------------------

        # TODO replace this with something global
        self.today = date.today()

        self.bind_key_events()

    def start(self):
        p3d_core.get_model_path().clear()
        panda_path = p3d_core.Filename.fromOsSpecific(constants.MODELS_PATH)
        p3d_core.get_model_path().prependDirectory(panda_path)
        self.create_new_project("DefaultProject", constants.DEFAULT_PROJECT_PATH)
        constants.obs.trigger("OnLevelEditorFinishInit")

    def update(self, task):
        """this method should be called ever frame in editor_state and game_state"""

        # XFormTask updates Inspector panel
        if task.time > self.current_xform_time:
            constants.obs.trigger("XFormTask")
            self.current_xform_time += self.x_form_delay

        constants.obs.trigger("EditorUpdate")

        return task.cont

    # --------------------------------Scene operations-----------------------------#
    def create_new_project(self, name, path):
        if self.ed_state == constants.GAME_STATE:
            print("[Editor] Cannot create new project in game mode")
            return

        self.project.set_project(name, path)
        self.create_new_scene()
        self.reload_resources()

    def create_new_scene(self):
        if self.active_scene:
            # TODO prompt the user to save current scene
            self.clean_active_scene()

        self.active_scene = self.project.game.create_new_scene("default")
        constants.obs.trigger("OnSceneStart")

        self.setup_default_scene()

    def setup_default_scene(self):
        self.active_gizmo = "pos"

        # add a default sunlight
        constants.command_manager.do(commands.AddLight(constants.p3d_app, "DirectionalLight"), select=False)
        light_np = self.active_scene.render.find("**/DirectionalLight")
        light_np = light_np.getPythonTag(constants.TAG_PICKABLE)
        light_np.setPos(400, 200, 350)
        light_np.setHpr(p3d_core.Vec3(115, -25, 0))
        light_np.set_color(p3d_core.Vec4(255, 250, 140, 255))

        # add a default player camera
        constants.command_manager.do(commands.AddCamera(constants.p3d_app), select=False)
        cam = self.active_scene.render.find("**/PlayerCam").getNetPythonTag(constants.TAG_PICKABLE)
        cam.setPos(-239.722, 336.966, 216.269)
        cam.setHpr(p3d_core.Vec3(-145.0, -20, 0))
        self.set_player_camera(cam)

        # add a default cube
        constants.command_manager.do(commands.ObjectAdd(constants.p3d_app, constants.CUBE_PATH), select=False)
        obj = self.active_scene.render.find("**/cube.fbx")
        obj.setScale(0.5)

        self.set_active_gizmo(self.active_gizmo)
        self.toggle_scene_lights()
        constants.obs.trigger("ToggleSceneLights", True)

    def clean_active_scene(self):
        # clear scene lights
        self.app.show_base.render.clearLight()
        self.active_scene.scene_lights.clear()
        self.scene_lights_on = False
        constants.obs.trigger("ToggleSceneLights", False)

        # clear scene cameras
        self.active_scene.scene_cameras.clear()

        self.selection.deselect_all()
        self.update_gizmo()

        for np in self.app.show_base.edRender.get_children():
            if np.hasPythonTag(constants.TAG_PICKABLE):
                np.getPythonTag(constants.TAG_PICKABLE).on_remove()
                np.remove_node()

        for np in self.app.show_base.render.get_children():
            if np.hasPythonTag(constants.TAG_PICKABLE):
                np.getPythonTag(constants.TAG_PICKABLE).on_remove()
            np.remove_node()

    def save_ed_state(self):
        def save(np):
            if len(np.getChildren()) > 0:
                for child in np.getChildren():
                    if type(child) is p3d_core.NodePath and child.hasPythonTag(constants.TAG_PICKABLE):
                        child = child.getPythonTag(constants.TAG_PICKABLE)
                        child.save_data()
                        save(child.getPythonTag(constants.TAG_PICKABLE))

        save(self.active_scene.render)

    def clean_runtime_scene_modifications(self):
        def do_cleanup(_np):
            if len(_np.getChildren()) > 0:
                for child in _np.getChildren():
                    if type(child) is p3d_core.NodePath and child.hasPythonTag(constants.TAG_PICKABLE):
                        child = child.getPythonTag(constants.TAG_PICKABLE)
                        child.restore_data()

                        do_cleanup(child.getPythonTag(constants.TAG_PICKABLE))

        do_cleanup(self.active_scene.render)

    # -------------------------------Resources section-----------------------------#
    # load and register resources
    # TODO replace this with ResourceHandler

    def reload_resources(self):
        # reload resources
        # TODO replace this a call resource_handler.reload_resources()
        resources = self.app.wx_main.resource_browser.resource_tree
        resources.create_or_rebuild_tree(self.project.project_path, rebuild_event=False)
        resources.Refresh()
        self.load_all_mods(resources.resources["py"])
        self.load_text_files(resources.resources["txt"])

    def load_all_mods(self, modules_paths):
        def import_modules():
            for path in modules_paths:
                file = path.split("/")[-1]
                # path = _path
                # print("LOADED \n FILE--> {0} \n PATH {1} \n".format(file, path))

                mod_name = file.split(".")[0]
                cls_name_ = mod_name[0].upper() + mod_name[1:]

                # load the module
                spec = importlib.util.spec_from_file_location(mod_name, path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)

                imported_modules.append((module, cls_name_))

            return imported_modules

        def init_runtime_module(name, runtime_module):
            instance = runtime_module(
                name=name,
                show_base=self.project.game.show_base,
                win=self.app.show_base.main_win,
                dr=self.app.show_base.game_dr,  # TODO reimplement this in game
                dr2d=self.project.game.display_region_2d,
                mouse_watcher_node=self.project.game.mouse_watcher_node,
                render=self.active_scene.render,
                render2d=self.active_scene.render_2d,
                aspect2d=self.active_scene.aspect_2d,
                game=self.project.game,
            )
            return instance

        def init_ed_plugin(name, plugin):
            instance = plugin(
                name=name,
                win=self.app.show_base.main_win,
                dr=self.app.show_base.edDr,
                dr2d=self.app.show_base.edDr2d,
                mouse_watcher_node=self.app.show_base.ed_mouse_watcher_node,
                render=None,
                render2d=None,
                aspect2d=self.app.show_base.ed_aspect2d,
                level_editor=self,
                globals=self.app.globals
            )
            return instance

        if len(modules_paths) == 0:
            return True

        imported_modules = []

        if not constants.try_execute_1(import_modules):
            return

        save_data = {}  # save module data here, [cls_name] = save_data, and do any necessary cleanup
        for cls_name in self.__user_modules.keys():
            user_mod = self.__user_modules[cls_name]
            cls_instance = user_mod.class_instance

            cls_instance.ignore_all()

            # do not clear ui for editor plugins,
            # all editor plugins use a common aspect_2d,
            # clear them all at once.
            if cls_instance.module_type == constants.EditorPlugin:
                cls_instance.clear_ui()

            user_mod.save_data()
            save_data[cls_name] = user_mod.saved_data

        self.app.show_base.clear_ed_aspect_2d()
        self.__user_modules.clear()
        self.unregister_editor_plugins()  # TODO replace this with unload
        ed_plugins = []  # save editor tools here
        game_modules = {}  # save runtime modules here

        for mod, cls_name in imported_modules:
            if hasattr(mod, cls_name):
                cls = getattr(mod, cls_name)
                obj_type = None

                try:
                    obj_type = cls.__mro__[1]
                except AttributeError:
                    pass

                # make sure to load only EditorPlugin and RuntimeModule object types
                if obj_type == ed_core.runtimeModule.RuntimeModule or obj_type == ed_core.editorPlugin.EditorPlugin:
                    pass
                else:
                    continue

                # instantiate the class and catch any errors from its init method
                cls_instance = None
                try:
                    if obj_type == ed_core.runtimeModule.RuntimeModule:
                        cls_instance = init_runtime_module(cls_name, cls)

                    if obj_type == ed_core.editorPlugin.EditorPlugin:
                        cls_instance = init_ed_plugin(cls_name, cls)

                    module_type = cls_instance.module_type

                except Exception as e:
                    tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
                    for x in tb_str:
                        print(x)
                    print("{0} Unable to load user module {1}".format(self.today, cls_name))
                    continue

                # create a new user module
                self.__user_modules[cls_name] = ed_core.UserModule(cls_instance, cls_instance._sort)

                # try restore data
                if save_data.__contains__(cls_name):
                    # print("[LevelEditor] attempting to restore data for {0}".format(cls_name))
                    self.__user_modules[cls_name].saved_data = save_data[cls_name]
                    self.__user_modules[cls_name].reload_data()

                if module_type == constants.RuntimeModule:
                    game_modules[cls_name] = self.__user_modules[cls_name]
                    print("[{0}] Loaded runtime user module {1}.".format(self.today, cls_name))
                else:
                    # it's an editor plugin
                    ed_plugin = self.__user_modules[cls_name].class_instance
                    ed_plugin._sort = 1
                    ed_plugins.append(ed_plugin)

        # finally, register editor tools
        self.register_editor_plugins(ed_plugins)
        self.project.game.game_modules = game_modules
        constants.obs.trigger("UpdatePropertiesPanel")
        # print("[LevelEditor] Modules loaded successfully.")
        return True

    def load_text_files(self, text_files):
        self.__text_files.clear()
        for file in text_files:
            name = file.split("/")[-1]
            name = name.split(".")[0]
            self.__text_files[name] = file
            print("[{0}] Loaded text file {1}.".format(self.today, name))

    def register_editor_plugins(self, plugins):
        for plugin in plugins:
            self.__ed_plugins[plugin._name] = plugin
            plugin.start(sort=1)
            self.app.wx_main.menu_bar.add_plugin_menu(plugin._name)
            print("[{0}] Loaded editor plugin {1}.".format(self.today, plugin._name))

    def unregister_editor_plugins(self, plugin=None):
        if plugin:
            plugin.stop()
        else:
            for key in self.__ed_plugins.keys():
                self.__ed_plugins[key].stop()
                self.app.wx_main.clear_panel_contents("")

            self.__ed_plugins.clear()
            self.app.wx_main.menu_bar.clear_plugin_menus()

    @property
    def user_modules(self):
        user_modules = []
        for key in self.__user_modules.keys():
            user_modules.append(self.__user_modules[key].class_instance)
        return user_modules

    # ------------------------------Level editor section ----------------------------- #

    def setup_selection_system(self):
        self.selection = Selection(
            camera=self.app.show_base.ed_camera,
            rootNp=self.app.show_base.edRender,
            root2d=self.app.show_base.edRender2d,
            win=self.app.show_base.main_win,
            mouseWatcherNode=self.app.show_base.ed_mouse_watcher_node,
        )

    def create_grid(self, size, grid_step, sub_divisions):
        grid_np = self.app.show_base.edRender.find("AxisGrid")
        if grid_np:
            grid_np.clearPythonTag("AxisGridNP")
            grid_np.remove_node()

        grid_np = ed_core.ThreeAxisGrid()
        grid_np.setPythonTag(grid_np, "AxisGridNP")
        grid_np.create(size, grid_step, sub_divisions)
        grid_np.reparent_to(self.app.show_base.edRender)
        grid_np.show(constants.ED_GEO_MASK)
        grid_np.hide(constants.GAME_GEO_MASK)

    def setup_gizmo_manager(self):
        """Create gizmo manager."""
        self.gizmo_mgr_root_np = p3d_core.NodePath("Gizmos")
        self.gizmo_mgr_root_np.reparent_to(self.app.show_base.render)

        kwargs = {
            'camera': self.app.show_base.ed_camera,
            'rootNp': self.gizmo_mgr_root_np,
            'win': self.app.show_base.win,
            'mouseWatcherNode': self.app.show_base.ed_mouse_watcher_node
        }
        self.gizmo_mgr = gizmos.Manager(**kwargs)
        self.gizmo_mgr.AddGizmo(gizmos.Translation('pos', **kwargs))
        self.gizmo_mgr.AddGizmo(gizmos.Rotation('rot', **kwargs))
        self.gizmo_mgr.AddGizmo(gizmos.Scale('scl', **kwargs))

        for key in self.gizmo_mgr._gizmos.keys():
            gizmo = self.gizmo_mgr._gizmos[key]
            gizmo.hide(constants.GAME_GEO_MASK)

    def start_transform(self):
        self.selection.previous_matrices.clear()
        for np in self.selection.selected_nps:
            self.selection.previous_matrices[np] = np.get_transform()

    def stop_transform(self):
        self.gizmo = False
        cmd = commands.TransformNPs(self.app, self.selection.previous_matrices)
        constants.command_manager.do(cmd)

    def set_active_gizmo(self, gizmo):
        self.gizmo = True
        self.active_gizmo = gizmo
        self.gizmo_mgr.SetActiveGizmo(gizmo)

    def set_gizmo_local(self, val):
        self.gizmo_mgr.SetLocal(val)

    def toggle_gizmo_local(self, *args):
        self.gizmo_mgr.ToggleLocal()

    def update_gizmo(self):
        nps = self.selection.selected_nps
        self.gizmo_mgr.AttachNodePaths(nps)
        self.gizmo_mgr.RefreshActiveGizmo()

    def bind_key_events(self):
        for key in self.key_event_map.keys():
            func = self.key_event_map[key][0]
            args = self.key_event_map[key][1]

            if args is None:
                self.accept(key, func)
            else:
                self.accept(key, func, [args])

        self.app.show_base.ed_camera.disabled = False

    def unbind_key_events(self):
        for key in self.key_event_map.keys():
            self.ignore(key)

        self.app.show_base.ed_camera.disabled = True

    def on_mouse1_down(self, shift):
        self.mouse_1_down = True

        if not self.gizmo_mgr.IsDragging() and ed_core.MOUSE_ALT not in self.app.show_base.ed_camera.mouse.modifiers:
            self.selection.start_drag_select(shift[0])

        elif self.gizmo_mgr.IsDragging():
            self.start_transform()

    def on_mouse1_up(self):
        self.mouse_1_down = False

        if self.selection.marquee.IsRunning():
            last_selections = [np for np in self.selection.selected_nps]
            nps = self.selection.stop_drag_select()

            # select nps and start transform
            if len(nps) > 0:
                constants.command_manager.do(commands.SelectObjects(self.app, nps, last_selections))
            else:
                self.deselect_all()

        elif self.gizmo_mgr.IsDragging() or self.gizmo:
            self.stop_transform()

    def on_mouse2_down(self):
        pass

    def on_mouse2_up(self):
        pass

    def deselect_all(self):
        len_selected = len(self.selection.selected_nps)
        self.selection.deselect_all()
        self.gizmo_mgr.SetActiveGizmo(None)
        self.gizmo = False
        if len_selected > 0:
            constants.obs.trigger("OnDeselectAllNPs")

    def deselect_nps(self, nps):
        pass

    def switch_state(self, state):
        if state == constants.GAME_STATE:
            self.enable_game_state()

        elif state == constants.EDITOR_STATE:
            self.enable_editor_state()

        else:
            print("[LevelEditor] Undefined editor state {0}".format(state))

    def enable_editor_state(self):
        # print("LevelEditor --> Editor state enabled.")

        self.ed_state = constants.EDITOR_STATE

        if self.__game_viewport_maximized:
            self.app.show_base.edDr.setActive(True)
            self.app.show_base.game_dr.set_dimensions((0, 0.4, 0, 0.4))
            self.project.game.display_region_2d.set_dimensions((0, 0.4, 0, 0.4))

        self.project.game.stop()
        self.clean_runtime_scene_modifications()

        self.bind_key_events()

        # for any cleanup operations
        constants.obs.trigger("OnEnableEditorState")
        constants.obs.trigger("XFormTask", True)

    def enable_game_state(self):
        # print("LevelEditor --> Game state enabled.")

        self.ed_state = constants.GAME_STATE
        self.unbind_key_events()
        self.set_active_gizmo(None)

        self.save_ed_state()  # save editor state data

        if self.__game_viewport_maximized:
            self.app.show_base.edDr.setActive(False)
            self.app.show_base.game_dr.set_dimensions((0, 1, 0, 1))
            self.project.game.display_region_2d.set_dimensions((0, 1, 0, 1))

        self.project.game.start()

    LIGHT_MAP = {"PointLight": (p3d_core.PointLight, ed_node_paths.EdPointLight, constants.POINT_LIGHT_MODEL),
                 "SpotLight": (p3d_core.Spotlight, ed_node_paths.EdSpotLight, constants.SPOT_LIGHT_MODEL),
                 "DirectionalLight": (p3d_core.DirectionalLight, ed_node_paths.EdDirectionalLight,
                                      constants.DIR_LIGHT_MODEL),
                 "AmbientLight": (p3d_core.AmbientLight, ed_node_paths.EdAmbientLight, constants.AMBIENT_LIGHT_MODEL)}

    NODE_TYPE_MAP = {"DirectionalLight": ed_node_paths.EdDirectionalLight,
                     "PointLight": ed_node_paths.EdPointLight,
                     "SpotLight": ed_node_paths.EdSpotLight,
                     "AmbientLight": ed_node_paths.EdAmbientLight,
                     "EdCameraNp": ed_node_paths.CameraNodePath,
                     "ModelNodePath": ed_node_paths.BaseNodePath}

    def load_model(self, path, select=True):
        """loads a 3d model from input argument "path" to active render"""

        # TODO insert an exception handler here
        # TODO replace show-base loader with a new loader instance

        def add_children(_np):
            if len(_np.getChildren()) > 0:
                for child in _np.getChildren():
                    if not type(child) is p3d_core.NodePath:
                        continue
                    child = ed_node_paths.ModelNp(child, uid="ModelNp")
                    child.setColor(p3d_core.LColor(1, 1, 1, 1))
                    child.setPythonTag(constants.TAG_PICKABLE, child)
                    add_children(child)

        np = self.__loader.loadModel(path)
        np = ed_node_paths.BaseNodePath(np, uid="ModelNp", path=path)
        np.setColor(p3d_core.LColor(1, 1, 1, 1))
        np.setPythonTag(constants.TAG_PICKABLE, np)

        add_children(np)

        if self.ed_state is constants.EDITOR_STATE:
            np.reparent_to(self.active_scene.render)

        elif self.ed_state is constants.GAME_STATE:
            pass

        constants.obs.trigger("OnAddObjects(s)", [np])
        if select:
            self.set_selected([np])
        return np

    def add_actor(self, path):
        actor = ed_node_paths.ActorNp(path, uid="ActorNp")
        actor.setPythonTag(constants.TAG_PICKABLE, actor)
        actor.reparentTo(self.active_scene.render)

        constants.obs.trigger("OnAddObjects(s)", [actor])
        self.set_selected([actor])
        return actor

    def add_camera(self, select=True):
        # and wrap it into editor camera
        cam_np = ed_node_paths.CameraNodePath(uid="CameraNP")
        cam_np.set_name("PlayerCam")
        cam_np.node().setCameraMask(constants.GAME_GEO_MASK)
        cam_np.setPythonTag(constants.TAG_PICKABLE, cam_np)
        cam_np.reparent_to(self.active_scene.render)
        cam_np.setLightOff()

        # create a handle
        cam_handle = self.__loader.loadModel(constants.CAMERA_MODEL)
        cam_handle.show(constants.ED_GEO_MASK)
        cam_handle.hide(constants.GAME_GEO_MASK)

        # re-parent handle to cam_np
        cam_handle.reparent_to(cam_np)
        cam_handle.setScale(12)

        self.active_scene.scene_cameras.append(cam_np)

        if self.project.game.display_region.get_camera() == p3d_core.NodePath():
            self.set_player_camera(cam_np)

        constants.obs.trigger("OnAddObjects(s)", [cam_np])
        if select:
            self.set_selected([cam_np])
        return cam_np

    def add_object(self, path, select=True):
        np = self.__loader.loadModel(path, noCache=True)
        np.set_scale(0.5)

        # fix this name otherwise folder name also gets included
        name = np.get_name()
        name = name.split("\\")[-1]
        np.set_name(name)
        # ------------------------------------------------------

        np = ed_node_paths.BaseNodePath(np, uid="ModelNodePath", path=path)
        np.setPythonTag(constants.TAG_PICKABLE, np)
        np.reparent_to(self.active_scene.render)
        np.setHpr(p3d_core.Vec3(0, 90, 0))
        np.setColor(1, 1, 1, 1)
        mat = p3d_core.Material()
        mat.setDiffuse((1, 1, 1, 1))
        np.setMaterial(mat)

        # constants.obs.trigger("LevelEditorEvent", constants.le_Evt_On_Add_NodePath, np)
        constants.obs.trigger("OnAddObjects(s)", [np])
        if select:
            self.set_selected([np])
        return np

    def add_light(self, light, select=True):
        if self.LIGHT_MAP.__contains__(light):

            x = self.LIGHT_MAP[light]

            light_node = x[0](light)
            ed_handle = x[1]
            model = x[2]

            np = p3d_core.NodePath("light")
            np = np.attachNewNode(light_node)

            light_np = ed_handle(np, uid=light)
            light_np.setPythonTag(constants.TAG_PICKABLE, light_np)
            light_np.setLightOff()
            light_np.show(constants.ED_GEO_MASK)
            light_np.hide(constants.GAME_GEO_MASK)

            # TODO fix this
            if self.ed_state == constants.GAME_STATE:
                pass
                # light_np.reparent_to(self.runtime_np_parent)
            else:
                light_np.reparent_to(self.active_scene.render)

            if self.scene_lights_on:
                self.app.show_base.render.setLight(light_np)

            self.active_scene.scene_lights.append(light_np)

            model = self.__loader.loadModel(model, noCache=True)
            model.reparentTo(light_np)

            constants.obs.trigger("OnAddObjects(s)", [light_np])
            if select:
                self.set_selected([light_np])
            return light_np

    def on_duplicate_nps(self):
        if len(self.selection.selected_nps) > 0:
            (constants.command_manager.do(commands.DuplicateNPs(self.app)))

    def duplicate_nps(self, selections=None, select=True, *args):
        def recreate_object(_np):
            """for some reason np.copy does not duplicate python tag,
            so clear existing python tag and recreate it"""
            if _np.hasPythonTag(constants.TAG_PICKABLE):
                _uid = _np.getPythonTag(constants.TAG_PICKABLE).uid
                _np = self.NODE_TYPE_MAP[_uid](_np, uid=_uid)  # wrap panda node-path into editor node-path
                _np.setPythonTag(constants.TAG_PICKABLE, _np)

                # TO:DO copy object's editor data

                if _uid in ["PointLight", "DirectionalLight", "SpotLight"]:
                    self.active_scene.scene_lights.append(_np)
                    if self.scene_lights_on:
                        self.app.show_base.render.setLight(_np)

                # new_selections.append(_np.getPythonTag(constants.TAG_PICKABLE))
                return _np.getPythonTag(constants.TAG_PICKABLE)

            return None

        def recreate_children(_np):
            """to though all of _np children and recreate their python tags as well"""
            if len(_np.getChildren()) > 0:
                for child in _np.getChildren():
                    recreate_object(child)
                    recreate_children(child)

        if selections is None:
            selections = []

        if len(selections) == 0:
            selections = self.selection.selected_nps

        new_selections = []

        for np in selections:
            uid = np.uid
            if uid in self.NODE_TYPE_MAP.keys():
                x = np.copyTo(self.active_scene.render)
                x = recreate_object(x)  # recreate the parent
                new_selections.append(x)
                recreate_children(x)  # recreate children

        # constants.obs.trigger("LevelEditorEvent", constants.le_Evt_On_Add_NodePath, new_selections)
        constants.obs.trigger("OnAddObjects(s)", new_selections)

        if select:
            self.set_selected(new_selections)
            # constants.obs.trigger("LevelEditorEvent", constants.le_Evt_NodePath_Selected, new_selections)

        return new_selections

    def reparent_np(self, src_np, target_np):
        if src_np.getPythonTag(constants.TAG_PICKABLE).uid in ed_globals.LIGHT_UIDs:
            self.active_scene.scene_lights.remove(src_np)

        src_np.wrtReparentTo(target_np)

        if src_np.getPythonTag(constants.TAG_PICKABLE).uid in ed_globals.LIGHT_UIDs:
            self.active_scene.scene_lights.append(src_np)

        constants.obs.trigger("OnReparentNPs", src_np, target_np)
        return True

    def on_remove(self, *args, **kwargs):
        constants.obs.trigger("RemoveNPs", self.selection.selected_nps)

    def remove_nps(self, nps: list = None, permanent=False):
        """removes the given nps or current selected nps from active_scene but does not delete them"""

        def clean_np(_np):
            _np = _np.getPythonTag(constants.TAG_PICKABLE)

            if _np is None:
                return

            # clean up for scene lights
            if _np == self.project.game.display_region.get_camera():
                self.project.game.clear_active_3d_display_region()
                self.app.show_base.player_camera = None

            # clean up for scene lights
            if _np.uid in ["PointLight", "SpotLight", "DirectionalLight", "AmbientLight"]:
                self.active_scene.scene_lights.remove(_np)
                self.app.show_base.render.clearLight(_np)

        def clean_children(_np):
            if len(_np.getChildren()) > 0:
                for child in _np.getChildren():
                    clean_np(child)
                    clean_children(child)

        if not nps:
            nps = []
            for np in self.selection.selected_nps:
                nps.append(np)

        if not permanent:
            constants.obs.trigger("OnRemoveNPs", nps)
            self.deselect_all()

        detached_nodes = []

        for np in nps:
            if permanent:
                np.clearPythonTag(constants.TAG_PICKABLE)
                if np.uid == "ActorNp":
                    np.cleanup()
                else:
                    # print("permanent removed np {0}".format(np))
                    np.remove_node()
            else:
                clean_np(np)
                clean_children(np)
                detached_nodes.append(np)
                np.detachNode()

            # break all references to detached nodes in all user modules
            for key in self.__user_modules.keys():
                cls = self.__user_modules[key].class_instance
                for name, val in cls.__dict__.items():
                    if (type(val) == p3d_core.NodePath) and (val in detached_nodes):
                        setattr(cls, name, None)

    def restore_nps(self, nps: list):
        """restores given nps or current selected nps from ed_render to active_scene"""

        def restore_np(_np):
            _np = _np.getPythonTag(constants.TAG_PICKABLE)

            if _np is None:
                return

            # clean up for scene lights
            if _np == self.project.game.display_region.get_camera():
                self.project.game.clear_active_3d_display_region()

            # clean up for scene lights
            if _np.uid in ["PointLight", "SpotLight", "DirectionalLight", "AmbientLight"]:
                self.active_scene.scene_lights.append(_np)
                self.app.show_base.render.set_light(_np)

        def restore_children(_np):
            if len(_np.getChildren()) > 0:
                for child in _np.getChildren():
                    restore_np(child)
                    restore_children(child)

        for np in nps:
            np.reparent_to(self.active_scene.render)

            restore_np(np)
            restore_children(np)

            np.show(constants.ED_GEO_MASK)
            np.show(constants.GAME_GEO_MASK)

        constants.obs.trigger("OnAddObjects(s)", nps)
        self.set_selected(nps)

    def toggle_scene_lights(self):
        """inverts scene_light_on status and returns inverted value"""

        if self.scene_lights_on:
            self.scene_lights_on = False
            self.app.show_base.render.setLightOff()

        elif not self.scene_lights_on:
            for light in self.active_scene.scene_lights:
                self.app.show_base.render.setLight(light)
            self.scene_lights_on = True

        self.gizmo_mgr_root_np.setLightOff()
        return self.scene_lights_on

    def set_selected(self, selections: list):
        if len(selections) > 0:
            self.selection.set_selected(selections)

            # start transform------------------------------
            self.gizmo_mgr.SetActiveGizmo(self.active_gizmo)
            self.gizmo = True
            self.update_gizmo()
            # ----------------------------------------------

            constants.obs.trigger("OnSelectNPs", selections)

    def switch_ed_viewport_style(self):
        self.__game_viewport_maximized = not self.__game_viewport_maximized

    def set_player_camera(self, cam):
        cam = cam.getNetPythonTag(constants.TAG_PICKABLE)
        if cam and cam.uid == "CameraNP":
            cam.node().setCameraMask(constants.GAME_GEO_MASK)
            self.project.game.set_3d_display_region_active(cam)

            # TODO FIX THIS
            self.app.show_base.player_camera = cam
            self.app.show_base.update_aspect_ratio()
        else:
            print("[LevelEditor] failed to set player camera")

    def get_save_data(self):
        pass

    def get_module(self, module_name):
        """returns a user module by class_name, modules with an error will not be found"""

        if self.__user_modules.__contains__(module_name):
            if not self.__user_modules[module_name].class_instance._error:
                return self.__user_modules[module_name].class_instance
        return None

    def get_text_file(self, file_name):
        if self.__text_files.__contains__(file_name):
            return self.__text_files[file_name]
        return None

    def is_module(self, name):
        """returns a user module, by class_name, modules with an error will not be found"""

        if self.__user_modules.__contains__(name):
            return True
        return False

    def is_text_file(self, name):
        if self.__text_files.__contains__(name):
            return True
        return False

    def is_light(self, np):
        pass

    @property
    def game_viewport_maximized(self):
        return self.__game_viewport_maximized
