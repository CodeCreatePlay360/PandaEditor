from panda3d.core import GeomNode, CollisionNode, NodePath
from editor.selection.marquee import Marquee
from editor.selection.mousePicker import MousePicker
from editor.constants import TAG_GAME_OBJECT


class Selection:
    def __init__(self, *args, **kwargs):

        self.__render = None
        self.__append = False
        self.__selected_nps = []
        self.previous_matrices = {}

        # Create a marquee
        self.__marquee = Marquee('marquee', *args, **kwargs)

        # Create node picker - set its collision mask to hit both geom nodes and collision nodes
        bit_mask = GeomNode.getDefaultCollideMask() | CollisionNode.getDefaultCollideMask()
        self.__picker = MousePicker('picker',
                                    *args,
                                    fromCollideMask=bit_mask,
                                    **kwargs)

    def set_render(self, render):
        assert type(render) != type(NodePath)
        self.__render = render

    def set_selected(self, nps, append=False):
        if type(nps) is not list:
            print("[Selection] Input argument 'nps' must be a list")
            return

        if not append:
            self.deselect_all()

        for np in nps:
            self.__selected_nps.append(np)

        for np in self.__selected_nps:
            np.showTightBounds()

    def deselect_all(self):
        for np in self.__selected_nps:
            np.hideBounds()
        self.__selected_nps.clear()

    def start_drag_select(self, append=False):
        """
        Start the marquee and put the tool into append mode if specified.
        """
        if self.__marquee.mouseWatcherNode.hasMouse():
            self.__append = append
            self.__marquee.Start()

    def stop_drag_select(self, return_py_tags=False):
        """
        Stop the marquee and get all the node paths under it with the correct
        tag. Also append any node which was under the mouse at the end of the
        operation.
        """

        self.__marquee.Stop()
        new_selections = []

        if self.__append:
            for np in self.__selected_nps:
                new_selections.append(np)
        else:
            self.deselect_all()

        for pick_np in self.__render.findAllMatches('**'):
            if pick_np is not None:
                if self.__marquee.IsNodePathInside(pick_np) and pick_np.hasNetPythonTag(TAG_GAME_OBJECT):
                    np = pick_np.getNetPythonTag(TAG_GAME_OBJECT)
                    if np not in new_selections:
                        new_selections.append(np)

        # Add any node path which was under the mouse to the selection.
        np = self.get_np_under_mouse()
        if np is not None and np.hasNetPythonTag(TAG_GAME_OBJECT):
            np = np.getNetPythonTag(TAG_GAME_OBJECT)
            if np not in new_selections:
                new_selections.append(np)

        final = []
        for np in new_selections:
            self.top_np = None
            self.get_top_np(np)
            if self.top_np not in final:
                final.append(self.top_np)

        return final

    def get_np_under_mouse(self):
        """
        Returns the closest node under the mouse, or None if there isn't one.
        """
        self.__picker.on_update(None)
        picked_np = self.__picker.GetFirstNodePath()
        return picked_np

    top_np = None
    def get_top_np(self, np):
        top_np = np.get_parent()
        if top_np == self.__render:
            self.top_np = np.getPythonTag(TAG_GAME_OBJECT)
            return

        top_np = top_np.getPythonTag(TAG_GAME_OBJECT)
        if top_np != self.__render and top_np is not None:
            self.get_top_np(top_np)

    @property
    def selected_nps(self):
        selected = []
        for np in self.__selected_nps:
            selected.append(np)
        return selected

    @property
    def marquee(self):
        return self.__marquee

    @property
    def render(self):
        return self.__render
