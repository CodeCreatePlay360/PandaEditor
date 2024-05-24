from panda3d.core import MouseButton


class Mouse(object):
    def __init__(self, win, mwn):
        object.__init__(self)

        self.__win = win
        self.__mwn = mwn

        # 
        self.__center_mouse = False

        # for mouse movement
        self.__x = 0  # mouse pos x
        self.__y = 0  # mouse pos y
        self.__dx = 0  # mouse displacement x since last frame
        self.__dy = 0  # mouse displacement y since last frame

        # for button events
        self.__mouse_btns = {}

        # mouse btns and their corresponding status as dict key value pairs        
        self.__mouse_btns = {MouseButton.one().name: False,
                             MouseButton.two().name: False,
                             MouseButton.three().name: False,
                             MouseButton.four().name: False,
                             MouseButton.five().name: False, }

        # ---------------------------------------------
        self.__mp = self.__win.getPointer(0)

    def update(self):
        # for mouse move input
        if not self.__mwn.hasMouse():
            return

        # update mouse buttons
        for btn in self.__mouse_btns:
            self.__mouse_btns[btn] = self.__mwn.is_button_down(btn)

        # Get pointer from screen, calculate delta
        self.__mp = self.__win.getPointer(0)  # mouse position

        self.__dx = self.__x - self.__mp.getX()  # delta x
        self.__dy = self.__y - self.__mp.getY()  # delta y

        self.__x = self.__mp.getX()  # last x
        self.__y = self.__mp.getY()  # last y

        # print("dx: {0} dy: {1} x: {2} y: {3}".format(self.__dx, self.__dy,
        # self.__x, self.__y))

    @property
    def dx(self):
        return self.__dx

    @property
    def dy(self):
        return self.__dy

    @property
    def has_mouse(self):
        return self.__mwn.hasMouse()

    @property
    def mouse_btns(self):
        return self.__mouse_btns

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y
