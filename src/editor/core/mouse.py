from direct.showbase.DirectObject import DirectObject

MOUSE_ALT = 0
MOUSE_CTRL = 1


class Mouse(DirectObject):
    """Class representing the mouse."""

    def __init__(self, mouse_watcher, win):
        DirectObject.__init__(self)

        self.mouse_watcher_node = mouse_watcher
        self.win = win

        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.buttons = [False, False, False]
        self.modifiers = []

        # Bind button events
        self.accept('alt', self.set_modifier, [MOUSE_ALT])
        self.accept('alt-up', self.clean_modifier, [MOUSE_ALT])
        self.accept('control', self.set_modifier, [MOUSE_CTRL])
        self.accept('control-up', self.clean_modifier, [MOUSE_CTRL])

        self.accept('alt-mouse1', self.set_button, [0, True])
        self.accept('control-mouse1', self.set_button, [0, True])
        self.accept('mouse1', self.set_button, [0, True])
        self.accept('mouse1-up', self.set_button, [0, False])

        self.accept('alt-mouse2', self.set_button, [1, True])
        self.accept('control-mouse2', self.set_button, [1, True])
        self.accept('mouse2', self.set_button, [1, True])
        self.accept('mouse2-up', self.set_button, [1, False])

        self.accept('alt-mouse3', self.set_button, [2, True])
        self.accept('control-mouse3', self.set_button, [2, True])
        self.accept('mouse3', self.set_button, [2, True])
        self.accept('mouse3-up', self.set_button, [2, False])

    def update(self):
        # Get pointer from screen, calculate delta
        if not self.mouse_watcher_node.hasMouse():
            return

        mp = self.win.getPointer(0)
        self.dx = self.x - mp.getX()
        self.dy = self.y - mp.getY()
        self.x = mp.getX()
        self.y = mp.getY()

    def set_modifier(self, modifier):
        # Record modifier
        if modifier not in self.modifiers:
            self.modifiers.append(modifier)

    def clean_modifier(self, modifier):
        # Remove modifier
        if modifier in self.modifiers:
            self.modifiers.remove(modifier)

    def set_button(self, _id, value):
        # Record button value
        self.buttons[_id] = value
