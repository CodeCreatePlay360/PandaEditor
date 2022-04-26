import os
import sys
import importlib
import traceback
import panda3d.core as p3d_core
import editor.core as ed_core
import editor.nodes as ed_node_paths
import editor.gizmos as gizmos
import editor.constants as constants

from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import taskMgr
from editor.project import Project
from editor.selection import Selection


class LevelEditor(DirectObject):
    def __init__(self, panda_app, *args, **kwargs):
        DirectObject.__init__(self)

        constants.object_manager.add_object("LevelEditor", self)

        self.panda_app = panda_app

        self.project = Project(self)
        self.project_set = False

        self.ed_state = constants.EDITOR_STATE

        self.runtime_np_parent = None
        self.scene_render = None
        self.player_camera = None
        self.selected_module = None

        # gizmos, grid, selection
        self.grid_np = None
        self.selection = None
        self.gizmo_mgr_root_np = None
        self.gizmo = False
        self.gizmo_mgr = None
        self.update_task = None
        self.mouse_mode = None

        self.mouse_1_down = False
        self.mouse_2_down = False

        '''setup selection and gizmos'''
        self.create_grid(200, 20, 4)
        self.setup_selection_system()
        self.setup_gizmo_manager()

        # create event map for various keyboard events and bind them
        self.key_event_map = {"q": (self.set_active_gizmo, None),
                              "w": (self.set_active_gizmo, "pos"),
                              "e": (self.set_active_gizmo, "rot"),
                              "r": (self.set_active_gizmo, "scl"),
                              "space": (self.toggle_gizmo_local, None),
                              "+": (self.gizmo_mgr.SetSize, 2),
                              "-": (self.gizmo_mgr.SetSize, 0.5),
                              "control-d": (self.duplicate_object, []),
                              "x": (self.on_remove, None),

                              "mouse1": (self.on_mouse1_down, [False]),
                              "mouse2": (self.on_mouse2_down, None),

                              "mouse1-up": (self.on_mouse1_up, None),
                              "mouse2-up": (self.on_mouse2_up, None),

                              "shift-mouse1": (self.on_mouse1_down, [True]),
                              "control-mouse1": (self.on_mouse1_down, None)
                              }
        self.bind_key_events()

        self.active_gizmo = None
        self.gizmos_active = False

        self.scene_lights_on = False

        self.scene_lights = []  # all scene lights in one repository
        self.scene_cameras = []  # all scene camera in one repository

        self.__ed_plugins = {}
        self.__user_modules = {}
        self.__text_files = {}

        self._game_view_minimized = True

        self.save_file = ""

        self.current_time = 0
        self.x_form_delay = 0.1
        self.update_task = taskMgr.add(self.update, 'EditorUpdateTask', sort=1)

    def start(self):
        self.create_default_project(constants.DEFAULT_PROJECT_PATH)

    def update(self, task):
        """this method is called ever frame in editor_state and play_state"""
        if task.time > self.current_time:
            constants.obs.trigger("XFormTask")
            self.current_time += self.x_form_delay

        return task.cont

    def create_default_project(self, proj_path):
        wx_main = constants.object_manager.get("WxMain")
        file_browser = constants.object_manager.get("ProjectBrowser")

        if os.path.exists(proj_path) and os.path.isdir(proj_path):
            self.create_new_project(proj_path)

            wx_main.SetTitle("PandaEditor (Default Project)")

            file_browser.create_or_rebuild_tree(proj_path, rebuild_event=False)
            file_browser.Refresh()

            # replace this with a call to reload_editor
            self.load_all_mods(file_browser.resources["py"])
            self.load_text_files(file_browser.resources["txt"])

    def create_new_project(self, path):
        if self.ed_state == constants.GAME_STATE:
            self.switch_state(constants.EDITOR_STATE)

        res = self.project.set_project(path)
        if res is True:
            self.__user_modules.clear()
            self.__ed_plugins.clear()

            self.create_new_scene()

            self.project_set = True

            return True
        return False

    def load_project(self):
        pass

    # ------------------------------- various scene operations -----------------------------#
    def create_new_scene(self):
        self.clean_scene()

        # holds all geometry procedurally generated or loaded
        # at run time, it is cleaned on exit from game-mode
        self.runtime_np_parent = p3d_core.NodePath("GameRender")
        self.runtime_np_parent.reparent_to(self.panda_app.showbase.render)

        self.scene_render = p3d_core.NodePath("LevelEditorRender")
        self.scene_render.reparent_to(self.panda_app.showbase.render)

        constants.obs.trigger("LevelEditorEvent", "OnSceneStart")

        self.add_camera()
        self.setup_default_scene()

    def setup_default_scene(self):
        light = self.add_light("DirectionalLight")
        light.setPos(400, 200, 350)
        light.setHpr(p3d_core.Vec3(115, -25, 0))
        light.set_color(p3d_core.Vec4(255, 250, 140, 255))

        self.player_camera.setPos(-220, 280, 80)
        self.player_camera.setHpr(p3d_core.Vec3(218, 0, 0))

        self.panda_app.showbase.ed_camera.reset()

        obj = self.add_object(constants.CUBE_PATH)
        obj.setScale(0.5)
        obj.setHpr(90, 90, 0)

        self.toggle_scene_lights()
        constants.obs.trigger("ToggleSceneLights", True)

    def clean_scene(self):
        # clear scene lights
        self.panda_app.showbase.render.clearLight()
        self.scene_lights.clear()
        self.scene_lights_on = False
        constants.obs.trigger("ToggleSceneLights", False)

        # clear scene cameras
        self.scene_cameras.clear()

        self.selection.deselect_all()
        self.update_gizmo()

        for np in self.panda_app.showbase.render.get_children():
            if type(np) == p3d_core.NodePath:
                if np.hasPythonTag(constants.TAG_PICKABLE):
                    np.getPythonTag(constants.TAG_PICKABLE).on_remove()
                np.remove_node()

        self.player_camera = None

    def load_scene(self):
        pass

    def save_ed_state(self):
        def save(np):
            if len(np.getChildren()) > 0:
                for child in np.getChildren():
                    if type(child) is p3d_core.NodePath and child.hasPythonTag(constants.TAG_PICKABLE):

                        child = child.getPythonTag(constants.TAG_PICKABLE)
                        child.save_data()

                        save(child.getPythonTag(constants.TAG_PICKABLE))

        save(self.scene_render)

    def clean_runtime_scene_modifications(self):
        def do_cleanup(_np):
            if len(_np.getChildren()) > 0:
                for child in _np.getChildren():
                    if type(child) is p3d_core.NodePath and child.hasPythonTag(constants.TAG_PICKABLE):

                        child = child.getPythonTag(constants.TAG_PICKABLE)
                        child.restore_data()

                        do_cleanup(child.getPythonTag(constants.TAG_PICKABLE))

        # clean scene hierarchy from any objects loaded at runtime
        for np in self.runtime_np_parent.get_children():
            if type(np) == p3d_core.NodePath:
                np.getPythonTag(constants.TAG_PICKABLE).on_remove()
                np.remove_node()

        do_cleanup(self.scene_render)

    # -------------------------------USER MODULES / edTools SECTION-----------------------------#
    def load_all_mods(self, modules_paths):
        if self.ed_state == constants.GAME_STATE:
            return

        imported_modules = []

        # ---------------import python modules ------------------ #
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
        # ---------------------------------------------------------------------

        if len(modules_paths) == 0:
            return True

        result = constants.try_execute_1(import_modules)

        if result:
            pass
            # print("[LevelEditor] Modules imported successfully.")
        else:
            # print("[LevelEditor] Error while importing modules.")
            return False

        # save modules data here
        save_data = {}  # [cls_name] = save_data
        for cls_name in self.__user_modules.keys():
            self.__user_modules[cls_name].save_data()
            save_data[cls_name] = self.__user_modules[cls_name].saved_data

        self.__user_modules.clear()
        ed_plugins = []  # temporarily save editor tools here
        self.unregister_editor_plugins()

        for mod, cls_name in imported_modules:
            if hasattr(mod, cls_name):
                cls = getattr(mod, cls_name)
                obj_type = None

                try:
                    obj_type = cls.__mro__[1]
                except AttributeError:
                    pass

                # make sure to load only PModBase and PToolBase object types
                if obj_type == ed_core.pModBase.PModBase:
                    pass
                else:
                    continue

                # instantiate the class and catch any errors from its init method
                try:
                    cls_instance = cls(
                        name=cls_name,
                        win=self.panda_app.showbase.main_win,
                        mouse_watcher_node=self.panda_app.showbase.ed_mouse_watcher_node,
                        level_editor=self,
                        render=self.scene_render,
                        render_2d=self.panda_app.showbase.render2d,
                        game_cam=self.player_camera,
                        )

                except Exception as e:
                    print("LevelEditor --> Unable to load user module {0}".format(cls_name))
                    cls_instance = None
                    tb_str = traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
                    for x in tb_str:
                        print(x)
                    continue

                # create a new user module
                self.__user_modules[cls_name] = ed_core.UserModule(cls_instance, cls_instance._sort)

                # try restore data
                if save_data.__contains__(cls_name):
                    # print("[LevelEditor] attempting to restore data for {0}".format(cls_name))
                    self.__user_modules[cls_name].saved_data = save_data[cls_name]
                    self.__user_modules[cls_name].reload_data()

                # take care of editor plugins
                if self.__user_modules[cls_name].class_instance._editor_plugin:
                    ed_plugins.append(self.__user_modules[cls_name].class_instance)
                    self.__user_modules[cls_name].class_instance._sort = 2

        # finally, register editor tools
        self.register_editor_plugins(ed_plugins)

        # print("[LevelEditor] Modules loaded successfully.")
        constants.obs.trigger("UpdatePropertiesPanel")
        return True

    def load_text_files(self, text_files):
        self.__text_files.clear()
        for file in text_files:
            name = file.split("/")[-1]
            name = name.split(".")[0]
            # print("[LevelEditor] Loaded text file (NAME) {0} (PATH) {1}".format(name, file))
            self.__text_files[name] = file

    def register_editor_plugins(self, plugins):
        # start plugins
        for plugin in plugins:
            plugin.start(1)
            self.__ed_plugins[plugin._name] = plugin  # save the tool into editor_tools repository

    def unregister_editor_plugins(self):
        for key in self.__ed_plugins.keys():
            self.__ed_plugins[key].stop()
        self.__ed_plugins.clear()

    # ----------------------------- level editor section ----------------------------- #
    def setup_selection_system(self):
        self.selection = Selection(
            camera=self.panda_app.showbase.ed_camera,
            rootNp=self.panda_app.showbase.edRender,
            root2d=self.panda_app.showbase.edRender2d,
            win=self.panda_app.showbase.win,
            mouseWatcherNode=self.panda_app.showbase.ed_mouse_watcher_node
        )

    def create_grid(self, size, grid_step, sub_divisions):
        grid = ed_core.ThreeAxisGrid(rootNp=self.panda_app.showbase.edRender)
        self.grid_np = grid.create(size, grid_step, sub_divisions)
        self.grid_np.reparent_to(self.panda_app.showbase.edRender)
        self.grid_np.show(constants.ED_GEO_MASK)
        self.grid_np.hide(constants.GAME_GEO_MASK)

    def update_grid(self, size, grid_step, sub_divisions):
        self.grid_np.remove_node()
        self.create_grid(size, grid_step, sub_divisions)

    def setup_gizmo_manager(self):
        """Create gizmo manager."""
        self.gizmo_mgr_root_np = p3d_core.NodePath("Gizmos")
        self.gizmo_mgr_root_np.reparent_to(self.panda_app.showbase.edRender)

        kwargs = {
            'camera': self.panda_app.showbase.ed_camera,
            'rootNp': self.gizmo_mgr_root_np,
            'win': self.panda_app.showbase.win,
            'mouseWatcherNode': self.panda_app.showbase.ed_mouse_watcher_node
        }
        self.gizmo_mgr = gizmos.Manager(**kwargs)
        self.gizmo_mgr.AddGizmo(gizmos.Translation('pos', **kwargs))
        self.gizmo_mgr.AddGizmo(gizmos.Rotation('rot', **kwargs))
        self.gizmo_mgr.AddGizmo(gizmos.Scale('scl', **kwargs))

        for key in self.gizmo_mgr._gizmos.keys():
            gizmo = self.gizmo_mgr._gizmos[key]
            gizmo.hide(constants.GAME_GEO_MASK)

    def start_transform(self):
        self.gizmo = True
        self.update_gizmo()

    def stop_transform(self):
        self.gizmo = False

    def set_active_gizmo(self, gizmo):
        self.active_gizmo = gizmo
        if len(self.selection.selected_nps) > 0:
            self.gizmo_mgr.SetActiveGizmo(gizmo)
            self.update_gizmo()

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

        self.panda_app.showbase.ed_camera.disabled = False

    def unbind_key_events(self):
        for key in self.key_event_map.keys():
            self.ignore(key)

        self.panda_app.showbase.ed_camera.disabled = True

    def on_mouse1_down(self, shift):
        self.mouse_1_down = True

        if not self.gizmo_mgr.IsDragging() and ed_core.MOUSE_ALT not in self.panda_app.showbase.ed_camera.mouse.modifiers:
            self.selection.start_drag_select(shift[0])

        elif self.gizmo_mgr.IsDragging():
            self.start_transform()

    def on_mouse1_up(self):
        self.mouse_1_down = False

        if self.selection.marquee.IsRunning():
            nps = self.selection.stop_drag_select()
            # start transform
            if len(nps) > 0:
                constants.obs.trigger("LevelEditorEvent", constants.le_Evt_NodePath_Selected, nps)
                self.selection.set_selected(nps)
                self.gizmo_mgr.SetActiveGizmo(self.active_gizmo)
                self.start_transform()
            else:
                self.gizmo_mgr.SetActiveGizmo(None)
                self.gizmo = False
                # trigger deselect all
                constants.obs.trigger("LevelEditorEvent", constants.le_Evt_Deselect_All)

        elif self.gizmo_mgr.IsDragging() or self.gizmo:
            self.stop_transform()

        # self.panda_app.wx_main.ed_viewport_panel.OnMouseOneUp()

    def on_mouse2_down(self):
        pass

    def on_mouse2_up(self):
        pass

    def deselect_all(self):
        self.selection.deselect_all()
        self.gizmo_mgr.RefreshActiveGizmo()

    def reload_editor(self):
        pass

    def reset(self):
        pass

    def switch_state(self, state):
        if state == constants.GAME_STATE:
            self.enable_game_state()

        elif state == constants.EDITOR_STATE:
            self.enable_editor_state()

        else:
            print("LevelEditor --> Undefined editor state {0}".format(state))

    def enable_editor_state(self):
        # print("LevelEditor --> Editor state enabled.")

        self.ed_state = constants.EDITOR_STATE

        if not self._game_view_minimized:
            # if game view is not minimized toggle to full screen game view
            self.panda_app.showbase.on_enable_editor()

        self.stop_user_modules()
        self.clean_runtime_scene_modifications()

        self.bind_key_events()
        self.reload_editor()

        # for any cleanup operations
        constants.obs.trigger("LevelEditorEvent", constants.le_EVT_On_Enable_Ed_Mode)
        constants.obs.trigger("XFormTask", True)

    def enable_game_state(self):
        # print("LevelEditor --> Game state enabled.")

        self.ed_state = constants.GAME_STATE
        self.unbind_key_events()
        self.set_active_gizmo(None)

        self.save_ed_state()  # save editor state data

        if not self._game_view_minimized:
            # if game view is not minimized exit from full screen game view
            self.panda_app.showbase.on_enable_game()

        self.start_user_modules()

    def start_user_modules(self):
        mod_exec_order = {}
        for key in self.__user_modules:
            mod = self.__user_modules[key]

            if mod.class_instance._editor_plugin:
                continue

            sort_value = mod.class_instance._sort

            if mod_exec_order.__contains__(sort_value):
                mod_exec_order[sort_value].append(mod)
            else:
                mod_exec_order[sort_value] = []
                mod_exec_order[sort_value].append(mod)

        def _start(j):
            for _mod in mod_exec_order[j]:

                cls_instance = _mod.class_instance

                if not cls_instance._enabled:
                    return

                _mod.save_data()

                # start module's update
                _res = cls_instance.start(late_update_sort=late_update_sort)
                if not _res:
                    return False
                # print("start", _mod.class_instance._name)

            return True

        # copy modules execution orders as an int list
        lst = [*mod_exec_order.keys()]

        if len(lst) == 0:
            return

        # sort the sort order
        lst.sort()

        # self-explanatory
        start = lst[0]
        stop = lst[len(lst) - 1]

        # late updates are executed after all updates have been executed,
        # the sort order of all updates set in a way, that messenger executes them after updates
        late_update_sort = stop + 1

        for i in range(start, stop + 1):
            res = _start(i)
            if not res:
                break
            late_update_sort += 1

    def stop_user_modules(self):
        for key in self.__user_modules:
            mod = self.__user_modules[key]

            if mod.class_instance._editor_plugin:
                continue

            mod.class_instance.ignore_all()
            mod.class_instance.stop()
            # print("stopped", mod.class_instance._name)
            mod.reload_data()

    LIGHT_MAP = {"PointLight": (p3d_core.PointLight, ed_node_paths.EdPointLight, constants.POINT_LIGHT_MODEL),
                 "Spotlight": (p3d_core.Spotlight, ed_node_paths.EdSpotLight, constants.SPOT_LIGHT_MODEL),
                 "DirectionalLight": (p3d_core.DirectionalLight, ed_node_paths.EdDirectionalLight,
                                      constants.DIR_LIGHT_MODEL)}

    NODE_TYPE_MAP = {"ModelNp": ed_node_paths.ModelNp,
                     "DirectionalLight": ed_node_paths.EdDirectionalLight,
                     "PointLight": ed_node_paths.EdPointLight,
                     "SpotLight": ed_node_paths.EdSpotLight,
                     "EdCameraNp": ed_node_paths.EdCameraNp}

    def add_nodepath(self, path, geo=constants.SCENE_GEO, reparent_to_render=True):
        # TODO insert an exception handler here
        # TODO replace showbase.loader with a new loader instance

        np = self.panda_app.showbase.loader.loadModel(path)
        np = ed_node_paths.ModelNp(np, uid="ModelNp")

        # set a default model colour
        np.setColor(1, 1, 1, 1)

        # setup a default material
        mat = p3d_core.Material()
        mat.setDiffuse((1, 1, 1, 1))
        np.setMaterial(mat)

        # parent only if asked to do so !
        if geo == constants.EDITOR_GEO and reparent_to_render:
            np.reparent_to(self.panda_app.showbase.edRender)

        elif geo == constants.RUN_TIME_GEO and reparent_to_render:
            np.reparent_to(self.runtime_np_parent)

        elif geo == constants.SCENE_GEO and reparent_to_render:
            np.reparent_to(self.scene_render)

        elif geo == constants.GEO_NO_PARENT:
            pass

        elif reparent_to_render:
            np.remove_node()
            print("LevelEditor --> Unable to load 3d model.")
            return False

        constants.obs.trigger("LevelEditorEvent", constants.le_Evt_On_Add_NodePath, np)

        return np

    def add_actor(self, path):
        actor = ed_node_paths.ActorNp(path, uid="ActorNp")
        actor.setPythonTag(constants.TAG_PICKABLE, actor)
        actor.reparentTo(self.scene_render)
        constants.obs.trigger("LevelEditorEvent", constants.le_Evt_On_Add_NodePath, actor)

    def reparent_np(self, src_np, target_np):
        if target_np is None:
            src_np.wrtReparentTo(self.scene_render)
        else:
            src_np.wrtReparentTo(target_np)
        return True

    def add_camera(self, *args):
        if len(self.scene_cameras) > 0:
            print("[LevelEditor] currently support is limited to one camera per scene.")
            return

        # create lens
        lens = p3d_core.PerspectiveLens()
        lens.set_fov(60)
        lens.setAspectRatio(800 / 600)

        # create a panda3d camera
        cam_np = p3d_core.NodePath(p3d_core.Camera("Camera"))
        cam_np.node().setLens(lens)
        cam_np.node().setCameraMask(constants.GAME_GEO_MASK)

        # and wrap it into editor camera
        cam_np = ed_node_paths.EdCameraNp(cam_np, uid="EdCameraNp")
        cam_np.setPythonTag(constants.TAG_PICKABLE, cam_np)
        cam_np.reparent_to(self.scene_render)

        # create a handle
        cam_handle = self.panda_app.showbase.loader.loadModel(constants.CAMERA_MODEL)
        cam_handle.setLightOff()
        cam_handle.show(constants.ED_GEO_MASK)
        cam_handle.hide(constants.GAME_GEO_MASK)

        # re-parent handle to cam_np
        cam_handle.reparent_to(cam_np)
        cam_handle.setScale(2.25)

        self.scene_cameras.append(cam_np)
        self.player_camera = cam_np

        self.panda_app.showbase.set_player_camera(self.player_camera)
        self.panda_app.showbase.update_aspect_ratio()

        constants.obs.trigger("LevelEditorEvent", constants.le_Evt_On_Add_NodePath, cam_np)

        return cam_np

    def add_object(self, path):
        np = self.panda_app.showbase.loader.loadModel(path, noCache=True)
        np = ed_node_paths.ModelNp(np, uid="ModelNp")
        np.setPythonTag(constants.TAG_PICKABLE, np)
        np.reparent_to(self.scene_render)
        np.setHpr(p3d_core.Vec3(0, 90, 0))
        np.setColor(1, 1, 1, 1)
        mat = p3d_core.Material()
        mat.setDiffuse((1, 1, 1, 1))
        np.setMaterial(mat)

        constants.obs.trigger("LevelEditorEvent", constants.le_Evt_On_Add_NodePath, np)
        return np

    def add_light(self, light):
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

            if self.ed_state == constants.GAME_STATE:
                light_np.reparent_to(self.runtime_np_parent)
            else:
                light_np.reparent_to(self.scene_render)

            if self.scene_lights_on:
                self.panda_app.showbase.render.setLight(light_np)

            self.scene_lights.append(light_np)

            model = self.panda_app.showbase.loader.loadModel(model)
            model.reparentTo(light_np)

            constants.obs.trigger("LevelEditorEvent", constants.le_Evt_On_Add_NodePath, light_np)

            return light_np

    def rename_object(self, np, name):
        np.set_name(name)

    def duplicate_object(self, selections=None, select=True, *args):
        def recreate_object(_np):
            """for some reason np.copy does not duplicate python tag as well
            so clear existing python tag and recreate it"""
            if _np.hasPythonTag(constants.TAG_PICKABLE):
                _uid = _np.getPythonTag(constants.TAG_PICKABLE).uid
                _np = self.NODE_TYPE_MAP[_uid](_np, uid=_uid)  # wrap panda node-path into editor node-path
                _np.setPythonTag(constants.TAG_PICKABLE, _np)

                # TO:DO copy object's editor data

                if _uid in ["PointLight", "DirectionalLight", "SpotLight"]:
                    self.scene_lights.append(_np)
                    if self.scene_lights_on:
                        self.panda_app.showbase.render.setLight(_np)

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

        if len(selections) is 0:
            selections = self.selection.selected_nps

        new_selections = []

        for np in selections:
            uid = np.uid
            if uid in self.NODE_TYPE_MAP.keys():

                # ---------------------------------------------------------------- #
                # for the time being there is one camera limit per scene
                if uid is "EdCameraNp" or self.get_uid(np, "EdCameraNp") is not None:
                    print("[LevelEditor] only one scene camera limit per scene")
                    continue
                # ----------------------------------------------------------------- #

                x = np.copyTo(self.scene_render)
                x = recreate_object(x)  # recreate the parent
                new_selections.append(x)
                recreate_children(x)    # recreate children

        constants.obs.trigger("LevelEditorEvent", constants.le_Evt_On_Add_NodePath, new_selections)

        if select:
            self.selection.deselect_all()
            self.selection.set_selected(new_selections)
            self.update_gizmo()

            constants.obs.trigger("LevelEditorEvent", constants.le_Evt_NodePath_Selected, new_selections)

        return new_selections

    def on_remove(self, *args, **kwargs):
        if len(self.selection.selected_nps) > 0:
            constants.obs.trigger("LevelEditorEvent", constants.le_Evt_Remove_NodePaths)

    cam_found = False  # set this to true, if a camera is found during recursive NodePath remove operation
                       # as removing a camera requires some proper clean up, remember to set back to false afterwards.
    found_uid = None

    def remove_selected_nps(self, selections=None):
        if selections is None:
            selections = self.selection.selected_nps

        def clean(_np):
            _np = _np.getPythonTag(constants.TAG_PICKABLE)
            if _np is None:
                return

            if _np.uid in ["PointLight", "SpotLight", "DirectionalLight"]:
                self.scene_lights.remove(_np)
                self.panda_app.showbase.render.clearLight(_np)

            elif _np.uid is "EdCameraNp":
                self.cam_found = True

        def clean_up_children(_np):
            if len(_np.getChildren()) > 0:
                for child in _np.getChildren():
                    clean(child)
                    clean_up_children(child)

        # go through all node paths, and perform a cleanup.
        for np in selections:
            if np.hasNetPythonTag(constants.TAG_PICKABLE):
                clean(np)  # clean up parent
                clean_up_children(np)  # go through all the children, do cleanup

                if np.uid is "ActorNp":
                    np.cleanup()
                elif np.uid is "EdCameraNp":
                    self.cam_found = True
                else:
                    np.remove_node()

            else:
                np.remove_node()

        if self.cam_found:
            # properly clean up removing a camera
            self.player_camera.reparent_to(self.scene_render)
            self.scene_cameras.remove(self.player_camera)
            self.player_camera.remove_node()
            self.player_camera = None
            self.panda_app.showbase.player_camera = None

        self.cam_found = False
        self.selection.selected_nps.clear()
        self.update_gizmo()

    def toggle_scene_lights(self):
        """inverts scene_light_on status and returns inverted value"""

        if self.scene_lights_on:
            self.scene_lights_on = False
            self.panda_app.showbase.render.setLightOff()

        elif not self.scene_lights_on:
            for light in self.scene_lights:
                self.panda_app.showbase.render.setLight(light)
            self.scene_lights_on = True

        self.gizmo_mgr_root_np.setLightOff()
        return self.scene_lights_on

    def get_save_data(self):
        pass

    def get_uid(self, np, uid):
        """this function recursively searches a node-path and finds np with uid equal to argument uid,
        if more than one np of same uid is found the last is returned, None is returned is no np is found"""
        def search(_np):
            if len(_np.getChildren()) > 0:
                for child in _np.getChildren():
                    if child.hasPythonTag(constants.TAG_PICKABLE):
                        if child.getPythonTag(constants.TAG_PICKABLE).uid == uid:
                            self.found_uid = child.getPythonTag(constants.TAG_PICKABLE)

                    search(child)

        self.found_uid = None
        search(np)
        return self.found_uid

    def get_module(self, module_name):
        """returns a user module, by class_name, modules with an error will not be found"""

        if self.__user_modules.__contains__(module_name):
            if not self.__user_modules[module_name].class_instance._error:
                return self.__user_modules[module_name].class_instance
        return None

    def get_text_file(self, file_name):
        if self.__text_files.__contains__(file_name):
            return self.__text_files[file_name]
        return None

    def get_scene_render(self):
        return self.scene_render

    def get_player_camera(self):
        return self.player_camera

    def is_module(self, name):
        """returns a user module, by class_name, modules with an error will not be found"""

        if self.__user_modules.__contains__(name):
            return True
        return False

    def is_text_file(self, name):
        if self.__text_files.__contains__(name):
            return True
        return False

    def toggle_minimized_game_view(self, value: bool):
        self._game_view_minimized = value
