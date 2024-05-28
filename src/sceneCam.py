import math
from panda3d.core import LVecBase2f, LVecBase3f, PerspectiveLens, Camera
from panda3d.core import ClockObject, Quat, NodePath, LineSegs
from panda3d.core import KeyboardButton


class SceneCamera(NodePath):
    """Class representing a camera"""

    class Target(NodePath):
        """Class representing the camera's point of interest"""

        def __init__(self, pos=LVecBase3f(0, 0, 0)):
            NodePath.__init__(self, 'CamTarget')
            self.defaultPos = pos

    def __init__(self, speed=0.5, default_pos=(300, 400, 350)):
        self.__axes = None

        # 
        self.__win = None
        self.__mouse_watcher_node = None
        self.__aspect2d = None
        self.__mouse = None

        # create a new camera
        self.__cam = NodePath(Camera("SceneCamera"))

        # and a lens for it
        lens = PerspectiveLens()
        lens.set_fov(60)
        lens.setAspectRatio(800 / 600)
        self.__cam.node().setLens(lens)

        # wrap the camera in this NodePath class
        NodePath.__init__(self, self.__cam)

        # create a target to orbit around
        self.__target = SceneCamera.Target()

        # some movement related stuff
        self.__speed = speed
        self.__default_pos = default_pos
        self.__target_pos = self.getPos()

    def axes(self, thickness=1, length=25):
        """Class representing the viewport camera axes."""
        # Build line segments
        ls = LineSegs()
        ls.setThickness(thickness)

        # X Axis - Red
        ls.setColor(1.0, 0.0, 0.0, 1.0)
        ls.moveTo(0.0, 0.0, 0.0)
        ls.drawTo(length, 0.0, 0.0)

        # Y Axis - Green
        ls.setColor(0.0, 1.0, 0.0, 1.0)
        ls.moveTo(0.0, 0.0, 0.0)
        ls.drawTo(0.0, length, 0.0)

        # Z Axis - Blue
        ls.setColor(0.0, 0.0, 1.0, 1.0)
        ls.moveTo(0.0, 0.0, 0.0)
        ls.drawTo(0.0, 0.0, length)

        return ls.create()

    def initialize(self, engine):
        self.__win = engine.win
        self.__mouse_watcher_node = engine.mw.node()
        self.__aspect2d = engine.aspect2d
        self.__mouse = engine.mouse

        self.__axes = NodePath(self.axes())
        self.__axes.set_name("CameraAxes")
        self.__axes.reparentTo(self.__aspect2d)
        self.__axes.set_scale(0.008)

        # btns = self.__mouse_watcher_node.get_modifier_buttons().get_buttons()

    def move(self, move_vec):
        # Modify the move vector by the distance to the target, so the further
        # away the camera is the faster it moves
        camera_vec = self.getPos() - self.__target.getPos()
        camera_vec_length = camera_vec.length()
        move_vec *= camera_vec_length / 300

        self.setPos(self, move_vec)

        # ----------------------------------------------
        # lerp the current position to move pos
        # distance moved equals elapsed time times speed.
        # dist_covered = (ClockObject.get_global_clock().getRealTime() - 0) * self.__speed

        # fraction of journey completed equals current distance divided by total distance
        # fractionOfJourney = dist_covered / (move_vec-self.getPos()).length()
        # self.__target_pos = lerp(self.getPos(), move_vec, fractionOfJourney)
        # ----------------------------------------------

        # Move the target so it stays with the camera
        self.__target.setQuat(self.getQuat())
        test = LVecBase3f(move_vec.getX(), 0, move_vec.getZ())
        self.__target.setPos(self.__target, test)

    def orbit(self, delta):
        # Get new hpr
        hpr = LVecBase3f()
        hpr.setX(self.getH() + delta.getX())
        hpr.setY(self.getP() + delta.getY())
        hpr.setZ(self.getR())

        # Set camera to new hpr
        self.setHpr(hpr)

        # Get the H and P in radians
        rad_x = hpr.getX() * (math.pi / 180.0)
        rad_y = hpr.getY() * (math.pi / 180.0)

        # Get distance from camera to target
        camera_vec = self.getPos() - self.__target.getPos()
        cam_vec_dist = camera_vec.length()

        # Get new camera pos
        new_pos = LVecBase3f()
        new_pos.setX(cam_vec_dist * math.sin(rad_x) * math.cos(rad_y))
        new_pos.setY(-cam_vec_dist * math.cos(rad_x) * math.cos(rad_y))
        new_pos.setZ(-cam_vec_dist * math.sin(rad_y))
        new_pos += self.__target.getPos()

        # Set camera to new pos
        self.setPos(new_pos)

    def on_resize_event(self, aspect_ratio):
        """should be called when window is resized"""
        self.node().getLens().setAspectRatio(aspect_ratio)
        self.update_axes()

    def reset(self):
        # Reset camera and target back to default positions
        self.__target.setPos(self.__target.defaultPos)
        self.setPos(self.__default_pos)

        # Set camera to look at target
        self.lookAt(self.__target.getPos())
        self.__target.setQuat(self.getQuat())

        self.update_axes()

    def update(self):
        # Return if no input is found or alt not down
        if not self.__mouse_watcher_node.hasMouse() or not \
                self.__mouse_watcher_node.is_button_down(KeyboardButton.alt()):
            return

        # orbit - If left input down
        if self.__mouse.mouse_btns["mouse1"]:
            self.orbit(LVecBase2f(self.__mouse.dx * self.__speed,
                                  self.__mouse.dy * self.__speed))

        # dolly - If middle input down
        elif self.__mouse.mouse_btns["mouse2"]:
            self.move(LVecBase3f(self.__mouse.dx * self.__speed, 0,
                                 -self.__mouse.dy * self.__speed))

        # zoom - If right input down
        elif self.__mouse.mouse_btns["mouse3"]:
            self.move(LVecBase3f(0, -self.__mouse.dx * self.__speed, 0))

        # self.setPos(self, self.__target_pos)
        self.update_axes()

    def update_axes(self):
        # update axes
        # Set rotation to inverse of camera rotation

        aspect = self.__win.getXSize() / self.__win.getYSize()

        self.__axes.set_pos(LVecBase3f(aspect - 0.25, 0, 1 - 0.25))

        camera_quat = Quat(self.getQuat())
        camera_quat.invertInPlace()

        self.__axes.setQuat(camera_quat)
