from panda3d.core import GeomNode, CollisionNode, NodePath
from utils import Marquee, MousePicker


class Selection:
    def __init__(self, *args, **kwargs):
        
        self.__render = kwargs.pop('render')
        render2D      = kwargs.pop('render2D')
        self.__mwn    = kwargs.pop('mwn')
        cam           = kwargs.pop('cam')

        
        self.__append = False
        self.__selected_nps = []

        # Create a marquee
        self.__marquee = Marquee(
                                 name='Marquee',
                                 cam=cam,
                                 render2d=render2D,
                                 mwn=self.__mwn,
                                 *args, **kwargs)

        # Create node picker - set its collision mask to hit both geom nodes and collision nodes
        bit_mask = GeomNode.getDefaultCollideMask() | CollisionNode.getDefaultCollideMask()
        self.__picker = MousePicker(name='Picker',
                                    cam=cam,
                                    render=self.__render,
                                    mwn=self.__mwn,
                                    fromCollideMask=bit_mask,
                                    *args, **kwargs)

    def set_selected(self, nps, append=False):
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
        if self.__mwn.hasMouse():
            self.__append = append
            self.__marquee.start()

    def stop_drag_select(self):
        """
        Stop the marquee and get all the node paths under it with the correct
        tag. Also append any node which was under the mouse at the end of the
        operation.
        """

        self.__marquee.stop()
        new_selections = []

        if self.__append:
            for np in self.__selected_nps:
                new_selections.append(np)
        else:
            self.deselect_all()

        for pick_np in self.__render.findAllMatches('**'):
            if pick_np is not None:
                if self.__marquee.is_nodepath_inside(pick_np):  #and pick_np.hasNetPythonTag(TAG_GAME_OBJECT):
                    np = pick_np
                    if np not in new_selections:
                        new_selections.append(np)

        # Add any node path which was under the mouse to the selection.
        np = self.get_np_under_mouse()
        if np is not None:  #  np.hasNetPythonTag(TAG_GAME_OBJECT):
            if np not in new_selections:
                new_selections.append(np)

        result = []
        for np in new_selections:
            if np == self.__render:
                print("__see__")
                continue
            
            top_np = self.get_top_np(np)

            if top_np is not None and top_np not in result:
                result.append(top_np)

        return result

    def get_np_under_mouse(self):
        """
        Returns the closest node under the mouse, or None if there isn't one.
        """
        self.__picker.on_update(None)
        picked_np = self.__picker.get_first_np()
        return picked_np

    def get_top_np(self, np):
        top_np = np.get_parent()
        if top_np == self.__render:
            return np

        if top_np != self.__render and top_np is not None:
            return self.get_top_np(top_np)
        return top_np

    @property
    def selected_nps(self):
        selected = []
        for np in self.__selected_nps:
            selected.append(np)
        return selected