import math
import panda3d.core as p3d_core
from direct.showbase.ShowBase import taskMgr
import editor.core as ed_core
from editor.p3d.geometry import Axes
from editor.utils import common_maths


class EditorCamera(p3d_core.NodePath):
    """Class representing a camera"""

    class Target(p3d_core.NodePath):
        """Class representing the camera's point of interest"""
        def __init__(self, pos=p3d_core.Vec3(0, 0, 0)):
            p3d_core.NodePath.__init__(self, 'EdCamTarget')
            self.defaultPos = pos

    def __init__(self, mouse_watcher_node, render2d, win, default_pos):
        base.disableMouse()

        self.win = win
        self.mouse_watcher_node = mouse_watcher_node
        self.default_pos = default_pos
        self.speed = 0.5
        self.disabled = False

        self.mouse = ed_core.Mouse(self.mouse_watcher_node, win)

        # create a new camera
        self.cam = p3d_core.NodePath(p3d_core.Camera("EditorCamera"))

        # create a new lens
        lens = p3d_core.PerspectiveLens()
        lens.set_fov(60, 60)
        lens.setAspectRatio(800 / 600)
        self.cam.node().setLens(lens)

        # wrap the camera in this NodePath class
        p3d_core.NodePath.__init__(self, self.cam)

        # create a target to orbit around
        self.target = EditorCamera.Target()

        # create axes
        self.axes = p3d_core.NodePath(Axes())
        self.axes.reparentTo(render2d)
        self.axes.set_scale(0.005)

        self.task = None

        self.reset()

    def reset(self):
        # Reset camera and target back to default positions
        self.target.setPos(self.target.defaultPos)
        self.setPos(self.default_pos)

        # Set camera to look at target
        self.lookAt(self.target.getPos())
        self.target.setQuat(self.getQuat())

        self.update_axes()

    def start(self):
        # start the update task
        self.task = taskMgr.add(self.update, "EdCameraUpdate", sort=0, priority=None)

    def update(self, task):
        if self.disabled:
            return task.cont

        self.mouse.update()

        # Return if no mouse is found or alt not down
        if not self.mouse_watcher_node.hasMouse() or ed_core.MOUSE_ALT not in self.mouse.modifiers:
            return task.cont

        # orbit - If left mouse down
        if self.mouse.buttons[0]:
            self.orbit(p3d_core.Vec2(self.mouse.dx * self.speed, self.mouse.dy * self.speed))

        # dolly - If middle mouse down
        elif self.mouse.buttons[1]:
            self.move(p3d_core.Vec3(self.mouse.dx * self.speed, 0, -self.mouse.dy * self.speed))

        # zoom - If right mouse down
        elif self.mouse.buttons[2]:
            self.move(p3d_core.Vec3(0, -self.mouse.dx * self.speed, 0))

        self.update_axes()

        return task.cont

    def update_axes(self):
        # update axes
        # Set rotation to inverse of camera rotation
        y_pos = common_maths.map_to_range(0, self.win.getYSize(), 0, 1, self.win.getYSize())
        aspect = self.win.getXSize() / self.win.getYSize()
        self.axes.set_pos(p3d_core.Vec3(aspect - 0.2, 0, y_pos - 0.2))

        camera_quat = p3d_core.Quat(self.getQuat())
        camera_quat.invertInPlace()
        self.axes.setQuat(camera_quat)

    def move(self, move_vec):
        # Modify the move vector by the distance to the target, so the further
        # away the camera is the faster it moves
        camera_vec = self.getPos() - self.target.getPos()
        camera_vec_length = camera_vec.length()
        move_vec *= camera_vec_length / 300

        # Move the camera
        self.setPos(self, move_vec)

        # Move the target so it stays with the camera
        self.target.setQuat(self.getQuat())
        test = p3d_core.Vec3(move_vec.getX(), 0, move_vec.getZ())
        self.target.setPos(self.target, test)

    def orbit(self, delta):
        # Get new hpr
        hpr = p3d_core.Vec3()
        hpr.setX(self.getH() + delta.getX())
        hpr.setY(self.getP() + delta.getY())
        hpr.setZ(self.getR())

        # Set camera to new hpr
        self.setHpr(hpr)

        # Get the H and P in radians
        rad_x = hpr.getX() * (math.pi / 180.0)
        rad_y = hpr.getY() * (math.pi / 180.0)

        # Get distance from camera to target
        camera_vec = self.getPos() - self.target.getPos()
        cam_vec_dist = camera_vec.length()

        # Get new camera pos
        new_pos = p3d_core.Vec3()
        new_pos.setX(cam_vec_dist * math.sin(rad_x) * math.cos(rad_y))
        new_pos.setY(-cam_vec_dist * math.cos(rad_x) * math.cos(rad_y))
        new_pos.setZ(-cam_vec_dist * math.sin(rad_y))
        new_pos += self.target.getPos()

        # Set camera to new pos
        self.setPos(new_pos)
