import panda3d.core as p3d_core
from editor.core.editorPlugin import EditorPlugin


class EdPlugin(EditorPlugin):
    def __init__(self, *args, **kwargs):
        EditorPlugin.__init__(self, *args, **kwargs)

        # __init__ should not contain anything except for variable declaration...!

        win = self._win  # the window we are rendering into currently
        mouse_watcher_node = self._mouse_watcher_node  # mouse watcher node
        render = self._render  # parent node-path of all scenes
        le = self._le  # instance of level editor

    def on_start(self):
        """on_start method is called once when editor is loaded,
        new node-paths such as direct gui elements, should be created here."""
        pass

    def on_update(self):
        """update method is called every frame"""
        pass
