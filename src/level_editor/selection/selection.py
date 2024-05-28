from panda3d.core import GeomNode, CollisionNode, BitMask32
from level_editor.constants import selectable_node_tag
from system import Systems
from utils import Marquee
from . import MousePicker


class Selection:
    def __init__(self, render, **kwargs):
        
        self.render = render
        self.selected_nps = []
        self.__append = False

        # Create a marquee
        self.marquee = Marquee(
            name='Marquee',
            camera=Systems.cam,
            render2D=Systems.render2d,
            mwn=Systems.mw.node())

        # mouse picker to detect collision and geo nodes under mouse
        # Create node picker - set its collision mask to hit both geom nodes 
        # and collision nodes
        bit_mask = GeomNode.getDefaultCollideMask() | \
        CollisionNode.getDefaultCollideMask()
        
        # exclude editor geo mask        
        self.__picker = MousePicker(name='EdSelectionMousePicker',
                                    camera=Systems.cam,
                                    render=Systems.render,
                                    mwn=Systems.mw.node(),
                                    from_collide_mask=bit_mask)

    def set_selected(self, nps, append=False):
        if not append:
            self.deselect_all()

        for np in nps:
            self.selected_nps.append(np)

        for np in self.selected_nps:
            np.showTightBounds()

    def deselect_all(self):
        for np in self.selected_nps:
            np.hideBounds()
        self.selected_nps.clear()

    def start_drag_select(self, append=False):
        """
        Start the marquee and put the tool into append mode if specified.
        """
        if Systems.mw.node().hasMouse():
            self.__append = append
            self.marquee.start()

    def stop_drag_select(self):
        """
        Stop the marquee and get all the node paths under it with the correct
        tag. Also append any node which was under the mouse at the end of the
        operation.
        """

        self.marquee.stop()
        new_selections = []

        if self.__append:
            for np in self.selected_nps:
                new_selections.append(np)
        else:
            self.deselect_all()
                        
        for pick_np in self.render.findAllMatches('**'):
            if pick_np is None:
                continue
                
            if not self.marquee.is_nodepath_inside(pick_np):
                continue
                
            if pick_np in new_selections:
                continue
            
            if not pick_np.hasNetTag(selectable_node_tag):
                continue
            
            new_selections.append(pick_np)


        # Add any node path which was under the mouse to the selection.
        np = self.get_np_under_mouse()
        if np is not None and np.hasNetTag(selectable_node_tag):
            if np not in new_selections:
                new_selections.append(np)

        result = []
        for np in new_selections:
            result.append(np)
            print("Selected {0}".format(np.getName()))

        return result

    def get_np_under_mouse(self):
        """
        Returns the closest node under the mouse, or None if there isn't one.
        """
        self.__picker.update(None)
        picked_np = self.__picker.get_first_np()
        return picked_np

    def get_top_np(self, np):
        top_np = np.get_parent()
        if top_np == Systems.render:
            return np

        if top_np != Systems.render and top_np is not None:
            return self.get_top_np(top_np)
        return top_np
