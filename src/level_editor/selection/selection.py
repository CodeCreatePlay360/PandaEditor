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

        self.selected_nps = [*self.selected_nps, *nps]

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

    def stop_drag_select(self, double_click=False):
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
        
        new_np = None
        
        for np in self.render.findAllMatches('**'):
            if np is None:
                continue
                
            if not self.marquee.is_nodepath_inside(np):
                continue
    
            if not np.hasNetTag(selectable_node_tag):
                continue
            
            new_np = self.get_selected_np(np)
            
            if new_np not in new_selections:
                new_selections.append(new_np)

        # Add any node path which was under the mouse at the time of
        # selection.
        new_np = self.get_np_under_mouse()
        if new_np is not None and new_np.hasNetTag(selectable_node_tag):
            if not double_click:
                new_np = self.get_selected_np(new_np)
            if new_np not in new_selections:
                new_selections.append(new_np)
                
        self.set_selected(new_selections)
                
        for np in self.selected_nps:
            print("Selected {0}".format(np.getName()))
                
        return self.selected_nps

    def get_np_under_mouse(self):
        """
        Returns the closest node under the mouse, or None if there isn't one.
        """
        self.__picker.update(None)
        picked_np = self.__picker.get_first_np()
        return picked_np
    
    def get_selected_np(self, np):
        top_np = np.get_parent()
        
        if not top_np.hasNetTag(selectable_node_tag):
            return np
        
        if top_np.getTag(selectable_node_tag):
            return np

        if not np.getTag(selectable_node_tag) and top_np is not None:
            return self.get_selected_np(top_np)
        
        return top_np
