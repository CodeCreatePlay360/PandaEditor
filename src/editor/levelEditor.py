import sys
import importlib
import traceback
import panda3d.core as p3d_core
import editor.core as ed_core
import editor.nodes as ed_nodepaths
import editor.gizmos as gizmos
import editor.constants as constants
import editor.commands as commands
import editor.utils as ed_utils

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
                              "x": (
                              lambda: self.app.command_manager.do(
                                  commands.RemoveObjects(self.app, self.selection.selected_nps)), None),
                              "control-z": (self.app.command_manager.undo, None),

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
        self.selection.active_scene = self.active_scene.render
        self.app.command_manager.clear()

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
        # reload editor here

    def create_new_scene(self):
        if self.active_scene:
            # TODO prompt the user to save current scene
            self.clean_active_scene()

        # create a new scene
        self.active_scene = self.project.game.create_new_scene("default")

        # get the wx-scene graph panel and set it up
        scene_graph = constants.object_manager.get("SceneGraph")
        scene_graph.init(self.active_scene.render)

        # finally, set up the default scene
        self.setup_default_scene()

    def setup_default_scene(self):
        # add a default sunlight
        self.app.command_manager.do(commands.AddLight(constants.p3d_app, "__DirectionalLight__"), select=False)
        light_np = self.active_scene.render.find("**/DirectionalLight")
        light_np = light_np.getPythonTag(constants.TAG_PICKABLE)
        light_np.setPos(400, 200, 350)
        light_np.setHpr(p3d_core.Vec3(115, -25, 0))
        light_np.set_color(p3d_core.Vec4(255, 250, 140, 255))

        # add a default player camera
        self.app.command_manager.do(commands.AddCamera(constants.p3d_app), select=False)
        cam = self.active_scene.render.find("**/Camera").getNetPythonTag(constants.TAG_PICKABLE)
        cam.setPos(-239.722, 336.966, 216.269)
        cam.setHpr(p3d_core.Vec3(-145.0, -20, 0))
        self.set_player_camera(cam)

        # add a default cube
        self.app.command_manager.do(commands.ObjectAdd(constants.p3d_app, constants.CUBE_PATH), select=False)
        obj = self.active_scene.render.find("**/cube.fbx")
        obj.setScale(0.5)

        self.set_active_gizmo("pos")

        constants.obs.trigger("OnSceneStart")
        constants.obs.trigger("ToggleSceneLights")

    def clean_active_scene(self):
        constants.obs.trigger("OnSceneClean", None)

        self.scene_lights_on = False
        self.selection.deselect_all()
        self.active_scene.render.remove_node()

    def save_ed_state(self):
        """saves current active scene into a hidden np"""
        # duplicate current active scene node-path
        self.hidden_np = p3d_core.NodePath("Hidden")
        self.hidden_np = self.active_scene.render.copy_to(self.hidden_np)
        self.traverse_scene_graph(self.hidden_np, recreate=True)

    def clean_runtime_scene_modifications(self):
        for np in self.active_scene.render.get_children():
            self.traverse_scene_graph(np,
                                      light_func=self.active_scene.render.clear_light if self.scene_lights_on else None)
            np.remove_node()

        self.app.show_base.player_camera = None
        for np in self.hidden_np.getChildren():
            np.reparent_to(self.active_scene.render)
            self.traverse_scene_graph(np,
                                      cam_func=self.set_player_camera,
                                      light_func=self.active_scene.render.set_light if self.scene_lights_on else None)

        self.hidden_np.remove_node()
        self.hidden_np = None

    # -------------------------------Resources section-----------------------------#
    # load and register resources
    # TODO replace this with ResourceHandler

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

                imported_modules.append((path, module, cls_name_))

            return imported_modules

        def init_runtime_module(name, runtime_module, path_):
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
                path=path_
            )
            return instance

        def init_ed_plugin(name, plugin, path_):
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
                globals=self.app.globals,
                path=path_,
                command_manager=self.app.command_manager
            )
            return instance

        if len(modules_paths) == 0:
            return True

        imported_modules = []

        if not constants.try_execute_1(import_modules):
            return

        save_data = {}  # save module data here, [cls_name] = save_data, and do any necessary cleanup
        for key in self.__user_modules.keys():
            user_mod = self.__user_modules[key]
            cls_instance = user_mod.class_instance

            cls_instance.ignore_all()

            # do not clear ui for editor plugins,
            # all editor plugins use a common aspect_2d,
            # clear them all at once.
            if cls_instance.type == constants.EditorPlugin:
                cls_instance.clear_ui()

            user_mod.save_data()
            save_data[key] = user_mod.saved_data

        self.app.show_base.clear_ed_aspect_2d()
        self.__user_modules.clear()
        self.unload_editor_plugins()  # TODO replace this with unload
        ed_plugins = []  # save editor tools here
        game_modules = {}  # save runtime modules here

        for path, mod, cls_name in imported_modules:
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
                        cls_instance = init_runtime_module(cls_name, cls, path)

                    if obj_type == ed_core.editorPlugin.EditorPlugin:
                        cls_instance = init_ed_plugin(cls_name, cls, path)

                    module_type = cls_instance.type

                except Exception as e:
                    tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
                    for x in tb_str:
                        print(x)
                    print("{0} Unable to load user module {1}".format(self.today, cls_name))
                    continue

                # create a new user module
                module = ed_core.UserModule(path, cls_instance, cls_instance.sort)
                self.__user_modules[path] = module

                # try restore data
                if save_data.__contains__(cls_name):
                    # print("[LevelEditor] attempting to restore data for {0}".format(cls_name))
                    self.__user_modules[path].saved_data = save_data[path]
                    self.__user_modules[path].reload_data()

                if module_type == constants.RuntimeModule:
                    game_modules[path] = self.__user_modules[path]
                    print("[{0}] Loaded runtime user module {1}.".format(self.today, cls_name))
                else:
                    # it's an editor plugin
                    ed_plugin = self.__user_modules[path].class_instance
                    ed_plugin._sort = 1
                    ed_plugins.append(ed_plugin)

        # finally, register editor tools
        self.load_editor_plugins(ed_plugins)
        self.project.game.game_modules = game_modules
        constants.obs.trigger("UpdatePropertiesPanel")
        # print("[LevelEditor] Modules loaded successfully.")
        return True

    def load_text_files(self, paths):
        self.__text_files.clear()
        for path in paths:
            name = path.split("/")[-1]
            name = name.split(".")[0]
            self.__text_files[path] = ed_core.TextFile(path)
            print("[{0}] Loaded text file {1}.".format(self.today, name))

    def load_editor_plugins(self, plugins):
        """load all editor plugins"""
        for plugin in plugins:
            self.__ed_plugins[plugin.name] = plugin
            res = plugin.start(sort=1)
            if res:
                self.app.wx_main.menu_bar.add_plugin_menu(plugin.name)
                print("[{0}] Loaded editor plugin {1}.".format(self.today, plugin.name))

    def unload_editor_plugins(self):
        """unloads all editor plugins"""
        for key in self.__ed_plugins.keys():
            self.__ed_plugins[key].stop()

        self.__ed_plugins.clear()
        self.app.wx_main.menu_bar.clear_plugins_menu()

    def unload_editor_plugin(self, plugin):
        if plugin.name in self.__ed_plugins.keys():
            del self.__ed_plugins[plugin.name]
            del self.__user_modules[plugin.path]
            print("Plugin execution failed {0}".format(plugin.name))

        self.app.wx_main.menu_bar.clear_plugins_menu()
        for plugin in self.__ed_plugins.keys():
            self.app.wx_main.menu_bar.add_plugin_menu(plugin.name)

    def get_module(self, file_path):
        """returns a user module by path"""
        if file_path in self.__user_modules.keys():
            return self.__user_modules[file_path].class_instance
        return None

    def get_text_file(self, file_name):
        if self.__text_files.__contains__(file_name):
            return self.__text_files[file_name]
        return None

    def is_module(self, file_path):
        """returns a user module by path"""
        if file_path in self.__user_modules.keys():
            return True
        return False

    def is_text_file(self, name):
        if self.__text_files.__contains__(name):
            return True
        return False

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
        self.gizmo_mgr_root_np.reparent_to(self.app.show_base.edRender)

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
        self.app.command_manager.do(cmd)

    def set_active_gizmo(self, gizmo):
        self.gizmo = True
        self.active_gizmo = gizmo
        self.gizmo_mgr.SetActiveGizmo(gizmo)

    def set_gizmo_local(self, val):
        self.gizmo_mgr.SetLocal(val)

    def set_selected(self, selections: list):
        if len(selections) > 0:
            self.selection.set_selected(selections)

            # start transform------------------------------
            self.gizmo_mgr.SetActiveGizmo(self.active_gizmo)
            self.gizmo = True
            self.update_gizmo()
            # ----------------------------------------------

            # constants.obs.trigger("OnSelectNPs", selections)

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
                self.app.command_manager.do(commands.SelectObjects(self.app, nps, last_selections))
            else:
                self.deselect_all(len(last_selections))

        elif self.gizmo_mgr.IsDragging() or self.gizmo:
            self.stop_transform()

    def on_mouse2_down(self):
        pass

    def on_mouse2_up(self):
        pass

    def deselect_all(self, len_last_selections: int = 0):
        len_selected = len(self.selection.selected_nps)
        self.selection.deselect_all()
        self.gizmo_mgr.SetActiveGizmo(None)
        self.gizmo = False
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
        self.deselect_all()  # call to deselect all, triggers OnDeselectAllNps event which properly handles
        # UI updates (inspector, scene graph etc.)

        # -------------------------------------------------------
        nps = []
        for cmd in self.app.command_manager.undo_commands:
            try:
                cmd.RemoveNPsCmd
                nps_ = []
                for np, parent in cmd.saved:
                    nps_.append(np)
                nps.extend(nps_)
            except AttributeError:
                pass

        self.remove_nps(nps, permanent=True)
        self.app.command_manager.clear()
        # -------------------------------------------------------

        self.save_ed_state()  # save editor state data

        if self.__game_viewport_maximized:
            self.app.show_base.edDr.setActive(False)
            self.app.show_base.game_dr.set_dimensions((0, 1, 0, 1))
            self.project.game.display_region_2d.set_dimensions((0, 1, 0, 1))

        constants.obs.trigger("OnEnableGameState")
        constants.obs.trigger("ResizeEvent")
        self.project.game.start()

    def load_model(self, path):
        """loads a 3d model from input argument "path" to active render"""

        def add_children(_np):
            if len(_np.getChildren()) > 0:
                for child in _np.getChildren():
                    if not type(child) == p3d_core.NodePath:
                        continue
                    # print("child: {0} type: {1}".format(child, type(child)))
                    child = ed_nodepaths.BaseNodePath(child)
                    child.setColor(p3d_core.LColor(1, 1, 1, 1))
                    child.setPythonTag(constants.TAG_PICKABLE, child)
                    if child.get_name() == "":
                        child.set_name("NoName")
                    add_children(child)

        np = ed_utils.try_execute_1(self.__loader.loadModel, path)
        if not np:
            return
        np = self.__loader.loadModel(path)
        np = ed_nodepaths.BaseNodePath(np, path=path)
        np.setColor(p3d_core.LColor(1, 1, 1, 1))
        np.setPythonTag(constants.TAG_PICKABLE, np)

        add_children(np)

        if self.ed_state is constants.EDITOR_STATE:
            np.reparent_to(self.active_scene.render)

        elif self.ed_state is constants.GAME_STATE:
            pass

        constants.obs.trigger("OnAddObjects(s)", [np])
        self.set_selected([np])
        return np

    def add_actor(self, path):
        try:
            actor = ed_nodepaths.ActorNodePath(path, uid="ActorNodePath")
        except Exception as e:
            print(e)
            return

        actor.setPythonTag(constants.TAG_PICKABLE, actor)
        actor.reparentTo(self.active_scene.render)

        constants.obs.trigger("OnAddObjects(s)", [actor])
        self.set_selected([actor])
        return actor

    def add_camera(self, select=True):
        # and wrap it into editor camera
        cam_np = ed_nodepaths.CameraNodePath(None)
        cam_np.set_name("Camera")
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

        self.active_scene.cameras.append(cam_np)

        if not self.app.show_base.player_camera:
            self.set_player_camera(cam_np)

        return cam_np

    def add_object(self, path):
        np = self.__loader.loadModel(path, noCache=True)
        np.set_scale(0.5)

        # fix this name otherwise folder name also gets included
        name = np.get_name()
        name = name.split("\\")[-1]
        np.set_name(name)
        # ------------------------------------------------------

        np = ed_nodepaths.BaseNodePath(np, id_="ModelNodePath", path=path)
        np.setPythonTag(constants.TAG_PICKABLE, np)
        np.reparent_to(self.active_scene.render)
        np.setHpr(p3d_core.Vec3(0, 90, 0))
        np.setColor(1, 1, 1, 1)
        mat = p3d_core.Material()
        mat.setDiffuse((1, 1, 1, 1))
        np.setMaterial(mat)

        return np

    def add_light(self, light: str, select=True):
        if constants.LIGHT_MAP.__contains__(light):

            x = constants.LIGHT_MAP[light]

            name = light.split("_")[2]
            light_node = x[0](name)
            ed_handle = x[1]
            model = x[2]

            np = p3d_core.NodePath("Light")
            np = np.attachNewNode(light_node)

            light_np = ed_handle(np)
            light_np.setPythonTag(constants.TAG_PICKABLE, light_np)
            light_np.setLightOff()
            light_np.show(constants.ED_GEO_MASK)
            light_np.hide(constants.GAME_GEO_MASK)

            if self.scene_lights_on:
                self.active_scene.render.setLight(light_np)

            model = self.__loader.loadModel(model, noCache=True)
            model.reparentTo(light_np)
            light_np.reparent_to(self.active_scene.render)

            constants.obs.trigger("OnAddObjects(s)", [light_np])
            if select:
                self.set_selected([light_np])
            return light_np
        else:
            print("Unable to add light {0}".format(light))

    def on_duplicate_nps(self):
        if len(self.selection.selected_nps) > 0:
            (self.app.command_manager.do(commands.DuplicateNPs(self.app)))

    def duplicate_nps(self, selections=None, render=None):
        selections = self.selection.selected_nps if selections is None else selections
        new_selections = []

        if render is None:
            render = self.active_scene.render

        for np in selections:
            if not np.hasPythonTag(constants.TAG_PICKABLE):
                print("Warning attempt to duplicate a nodepath with no python tag")

            x = np.copyTo(np.get_parent())
            self.traverse_scene_graph(x,
                                      light_func=self.active_scene.render.set_light if self.scene_lights_on else None,
                                      recreate=True)
            new_selections.append(x.getPythonTag(constants.TAG_PICKABLE))

        # constants.obs.trigger("OnAddObjects(s)", new_selections)
        return new_selections

    def reparent_np(self, src_nps, target_np):
        for i in range(len(src_nps)):
            src_np = src_nps[i]

            if type(target_np) is list:
                target_np_ = target_np[i]
            else:
                target_np_ = target_np

            src_np.wrtReparentTo(target_np_)

        return True

    def remove_nps(self, nps: list = None, permanent=False):
        """removes the given nps or current selected nps from active_scene but does not delete them"""

        nps = self.selection.selected_nps if nps is None else nps

        for np in nps:
            self.traverse_scene_graph(np,
                                      light_func=self.active_scene.render.clear_light if self.scene_lights_on else None)

        for np in nps:
            if permanent:
                np.remove_node()
            else:
                np.detach_node()

    def restore_nps(self, nps: list):
        """restores given nps or current selected nps from ed_render to active_scene"""

        restored_nps = []
        for np, parent in nps:
            np.reparent_to(parent)
            self.traverse_scene_graph(np,
                                      self.set_player_camera if not self.app.show_base.player_camera else None,
                                      self.active_scene.render.setLight)
            restored_nps.append(np)
        restored_nps = [np for np in restored_nps if np.get_parent() not in restored_nps]
        return restored_nps

    def toggle_scene_lights(self):
        """inverts scene_light_on status and returns inverted value"""

        if self.scene_lights_on:
            self.scene_lights_on = False
            self.active_scene.render.clear_light()

        else:
            for light in self.active_scene.scene_lights:
                self.active_scene.render.set_light(light)
            self.scene_lights_on = True

        return self.scene_lights_on

    def switch_ed_viewport_style(self):
        self.__game_viewport_maximized = not self.__game_viewport_maximized

    def set_player_camera(self, cam):
        cam = cam.getNetPythonTag(constants.TAG_PICKABLE)
        if cam and cam.id == "__CameraNodePath__":
            cam.node().setCameraMask(constants.GAME_GEO_MASK)
            self.project.game.set_3d_display_region_active(cam)

            # TODO FIX THIS
            self.app.show_base.player_camera = cam
            self.app.show_base.update_aspect_ratio()
        else:
            print("[LevelEditor] failed to set player camera")

    @property
    def game_viewport_maximized(self):
        return self.__game_viewport_maximized

    def traverse_scene_graph(self, np, cam_func=None, light_func=None, np_func=None, recreate=False, ):
        def op(np_):
            if isinstance(np_, p3d_core.NodePath) and np_.hasPythonTag(constants.TAG_PICKABLE):
                obj = np_.getPythonTag(constants.TAG_PICKABLE)

                if obj and recreate:
                    new_obj = constants.NODE_TYPE_MAP[obj.id](np_, copy=True)
                    np_.setPythonTag(constants.TAG_PICKABLE, new_obj)
                    obj = np_.getPythonTag(constants.TAG_PICKABLE)

                if obj.id in ["__PointLight__", "__DirectionalLight__", "__SpotLight__", "__AmbientLight__"]:
                    if light_func:
                        light_func(obj)
                elif obj.id == "__CameraNodePath__" and not self.app.show_base.player_camera:
                    if cam_func:
                        cam_func(obj)
                else:
                    if np_func:
                        np_func(obj)

        def traverse(np_):
            op(np_)
            for child in np_.getChildren():
                traverse(child)

        traverse(np)

    def get_np_by_uid(self, uid):
        pass
