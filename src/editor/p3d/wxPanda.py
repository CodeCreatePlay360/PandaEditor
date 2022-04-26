import sys
import wx

from direct.showbase.DirectObject import DirectObject
from panda3d.core import WindowProperties, Point3, Vec3
from direct.showbase.ShowBase import taskMgr
from editor.constants import object_manager


keyCodes = {
    wx.WXK_SPACE: 'space',
    wx.WXK_DELETE: 'del',
    wx.WXK_ESCAPE: 'escape',
    wx.WXK_BACK: 'backspace',
    wx.WXK_CONTROL: 'control',
    wx.WXK_ALT: 'alt',
    wx.WXK_UP: 'arrow_up',
    wx.WXK_DOWN: 'arrow_down',
    wx.WXK_LEFT: 'arrow_left',
    wx.WXK_RIGHT: 'arrow_right'
}


def on_key(evt, action=''):
    """
    Bind this method to a wx.EVT_KEY_XXX event coming from a wx panel or other
    widget, and it will re_schedule wx 'eating' the event and passing it to Panda's
    base class instead.
    """
    keyCode = evt.GetKeyCode()
    if keyCode in keyCodes:
        messenger.send(keyCodes[keyCode] + action)
    elif keyCode in range(256):
        # Test for any other modifiers. Add these in the order shift, control,
        # alt
        mod = ''
        if evt.ShiftDown():
            mod += 'shift-'
        if evt.ControlDown():
            mod += 'control-'
        if evt.AltDown():
            mod += 'alt-'
        char = chr(keyCode).lower()
        messenger.send(mod + char + action)


def on_key_map(evt):
    on_key(evt, '-up')


def on_key_down(evt):
    on_key(evt)


def on_left_up(evt):
    messenger.send('mouse1-up')


class Viewport(wx.Panel):
    def __init__(self, *args, **kwargs):
        """
        Initialise the wx panel. You must complete the other part of the
        init process by calling Initialize() once the wx-window has been
        built.
        """
        wx.Panel.__init__(self, *args, **kwargs)

        self.wx_main = args[0]
        self._win = None
        self.SetBackgroundColour("blue")

    def GetWindow(self):
        return self._win

    def SetWindow(self, win):
        self._win = win

    def Initialize(self, useMainWin=True):
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
            if useMainWin:
                base.openDefaultWindow(props=wp, gsg=None)
                self._win = base.win
            else:
                self._win = base.openWindow(props=wp, makeCamera=0)

        # list of all resource browser items(assets or models) being dragged in drag 
        # operation
        self.models = [] 

        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_CHAR, self.OnEvent)

    def OnOpen(self):
        wp = WindowProperties()
        wp.setOpen(True)
        self.GetWindow().requestProperties(wp)

    def OnClose(self):
        wp = WindowProperties()
        wp.setOpen(False)
        self.GetWindow().requestProperties(wp)

    def OnResize(self, event):
        """When the wx-panel is resized, fit the panda3d window into it."""
        frame_size = event.GetSize()
        wp = WindowProperties()
        wp.setOrigin(0, 0)
        size = self.GetSize()
        wp.setSize(size.x, size.y)
        # wp.setSize(800, 600)
        self._win.requestProperties(wp)
        event.Skip()
        
    def OnEvent(self, evt):
        evt.Skip()

    def OnMouseEnter(self):
        le = self.wx_main.panda_app.level_editor
        resource_browser = object_manager.get("ProjectBrowser")

        if not resource_browser.mouse_left_down or not self.wx_main.panda_app.on_mouse1_down:
            return

        '''
        asset_paths = resource_browser.GetSelections()
        self.models.clear()
        # load paths from Resource_Handler
        for path in asset_paths:
            path = resource_browser.GetItemText(path)
            if path in AssetsHandler.ASSETS_3D.keys():
                model = AssetsHandler.ASSETS_3D[path]

                # model.reparent_to(le.level_editor_render)
                model = le.duplicate_object([model])[0]
                model.setScale(7)
                
                self.models.append(model)
        '''

    def OnMouseLeave(self):
        if len(self.models) > 0:
            object_manager.get("ProjectBrowser").end_drag()

    def OnMouseHover(self, x, y):
        cam = self.wx_main.panda_app.level_editor.panda_app.showbase.ed_camera
        mousePointer = self.wx_main.panda_app.showbase.ed_mouse_watcher_node

        for model in self.models:

            # first check collision detection using mouse picker

            # else
            hoverX = mousePointer.getMouseX() * 20
            hoverY = mousePointer.getMouseY() * 20
            model.setPos(cam, Vec3(hoverX, 35, hoverY))

    def OnMouseOneDown(self):
        pass

    def OnMouseOneUp(self):
        self.models.clear()
        # object_manager.get("ProjectBrowser").end_drag()
        
    def ScreenToViewport(self, x, y):
        x = (x / float(self.GetSize()[0]) - 0.5) * 2
        y = (y / float(self.GetSize()[1]) - 0.5) * -2
        return x, y

    def GetDroppedObject(self, x, y):
        x, y = self.ScreenToViewport(x, y)
        return self.app.selection.GetNodePathAtPosition(x, y)


class App(wx.App, DirectObject):
    """
    Don't forget to bind your frame's wx.EVT_CLOSE event to the app's
    self.Quit method, or the application will not close properly.
    """

    def ReplaceEventLoop(self):
        self.evtLoop = wx.GUIEventLoop()
        self.oldLoop = wx.EventLoop.GetActive()
        wx.EventLoop.SetActive(self.evtLoop)
        taskMgr.add(self.WxStep, 'evtLoopTask')

    def OnDestroy(self, event=None):
        self.WxStep()
        wx.EventLoop.SetActive(self.oldLoop)

    def Quit(self, event=None):
        self.OnDestroy(event)
        try:
            base
        except NameError:
            sys.exit()
        base.userExit()

    def start(self):
        while True:
            self.WxStep()

    def WxStep(self, task=None):
        while self.evtLoop.Pending():
            self.evtLoop.Dispatch()
            self.evtLoop.ProcessIdle()

        if task is not None:
            return task.cont
