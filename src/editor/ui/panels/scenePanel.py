import sys
import wx

from panda3d.core import WindowProperties
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import taskMgr
from editor.ui.splitwindow import SplitWindow


class Viewport(SplitWindow):
    def __new__(cls, *args, **kwargs):
        """
        Initialise the wx panel. You must complete the other part of the
        init process by calling Initialise() once the wx-window has been
        built.
        """
        self = super().__new__(cls, *args, **kwargs)
        self.wx_main = args[0]
        self._win = None
        self._initialized = False
        return self

    def get_window(self):
        return self._win

    def set_window(self, win):
        self._win = win

    def initialize(self, use_main_win=True):
        """
        The panda3d window must be put into the wx-window after it has been
        shown, or it will not size correctly.
        """

        assert self.GetHandle() != 0
        wp = WindowProperties()
        wp.setOrigin(0, 0)

        size = self.GetSize()
        wp.setSize(size.x, size.y)
        wp.setParentWindow(self.GetHandle())

        if self._win is None:
            if use_main_win:
                base.openDefaultWindow(props=wp, gsg=None)
                self._win = base.win
            else:
                self._win = base.openWindow(props=wp, makeCamera=0)

        self._initialized = True
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_CHAR, self.on_event)

    def set_focus(self):
        wp = WindowProperties()
        wp.setForeground(True)
        self._win.requestProperties(wp)

    def on_resize(self, event):
        """When the wx-panel is resized, fit the panda3d window into it."""
        wp = WindowProperties()
        wp.setOrigin(0, 0)
        size = self.GetSize()
        wp.setSize(size.x, size.y)
        self._win.requestProperties(wp)
        event.Skip()

    def on_event(self, evt):
        evt.Skip()


class App(wx.App, DirectObject):
    """
    Don't forget to bind your frame's wx.EVT_CLOSE event to the app's
    self.Quit method, or the application will not close properly.
    """
    event_loop = None
    old_loop = None

    def replace_event_loop(self):
        self.event_loop = wx.GUIEventLoop()
        self.old_loop = wx.EventLoop.GetActive()
        wx.EventLoop.SetActive(self.event_loop)
        taskMgr.add(funcOrTask=self.wx_step, name='EvtLoopTask')

    def on_destroy(self, event=None):
        self.wx_step()
        wx.EventLoop.SetActive(self.old_loop)

    def quit(self, event=None):
        self.on_destroy(event)
        try:
            base
        except NameError:
            sys.exit()
        base.userExit()

    def start(self):
        while True:
            self.wx_step()

    def wx_step(self, task=None):
        while self.event_loop.Pending():
            self.event_loop.Dispatch()
            self.event_loop.ProcessIdle()

        # if task is not None:
        #     return task.cont
