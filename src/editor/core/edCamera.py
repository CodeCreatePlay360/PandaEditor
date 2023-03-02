import math
import editor.core as ed_core
from panda3d.core import NodePath, Camera, PerspectiveLens, LVecBase3f, LVecBase2f, BoundingSphere, Point3, Quat
from direct.showbase.ShowBase import taskMgr
from editor.p3d.geometry import Axes
from editor.utils import common_maths


class EditorCamera(NodePath):
    """Class representing a camera"""

    class Target(NodePath):
        """Class representing the camera's point of interest"""
        def __init__(self, pos=LVecBase3f(0, 0, 0)):
            NodePath.__init__(self, 'EdCamTarget')
            self.defaultPos = pos

    def __init__(self, win, mouse_watcher_node, render, render2d, default_pos):
        base.disableMouse()

        self.win = win
        self.render = render
        self.mouse_watcher_node = mouse_watcher_node
        self.default_pos = default_pos
        self.speed = 0.5

        self.mouse = ed_core.Mouse(self.mouse_watcher_node, win)

        # create a new camera
        self.cam = NodePath(Camera("EditorCamera"))

        # create a new lens
        lens = PerspectiveLens()
        lens.set_fov(60)
        lens.setAspectRatio(800 / 600)
        self.cam.node().setLens(lens)

        # wrap the camera in this NodePath class
        NodePath.__init__(self, self.cam)

        # create a target to orbit around
        self.target = EditorCamera.Target()

        # create axes
        self.axes = NodePath(Axes())
        self.axes.set_name("CameraAxes")
        self.axes.reparentTo(render2d)
        self.axes.set_scale(0.008)

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
        self.task = taskMgr.add(self.update, "_ed_task_LECameraUpdate", sort=0, priority=None)

    def update(self, task):
        self.mouse.update()

        # Return if no mouse is found or alt not down
        if not self.mouse_watcher_node.hasMouse() or ed_core.MOUSE_ALT not in self.mouse.modifiers:
            return task.cont

        # orbit - If left mouse down
        if self.mouse.buttons[0]:
            self.orbit(LVecBase2f(self.mouse.dx * self.speed, self.mouse.dy * self.speed))

        # dolly - If middle mouse down
        elif self.mouse.buttons[1]:
            self.move(LVecBase3f(self.mouse.dx * self.speed, 0, -self.mouse.dy * self.speed))

        # zoom - If right mouse down
        elif self.mouse.buttons[2]:
            self.move(LVecBase3f(0, -self.mouse.dx * self.speed, 0))

        self.update_axes()

        return task.cont

    def frame(self, nps: list, direction=0):
        """frame the nps into camera view and optionally camera in any one direction left, right or top
        as specified by direction parameter.
        direction= 1: align-right, -1: align-left, 2: align top"""

        if len(nps) == 0:
            return

        # Get a list of bounding spheres for each NodePath in world space.
        allBnds = []
        allCntr = LVecBase3f()
        for np in nps:
            bnds = np.getBounds()
            if bnds.isInfinite():
                continue
            mat = np.getParent().getMat(self.render)
            bnds.xform(mat)
            allBnds.append(bnds)
            allCntr += bnds.getCenter()

        # Now create a bounding sphere at the center point of all the
        # NodePaths and extend it to encapsulate each one.
        bnds = BoundingSphere(Point3(allCntr / len(nps)), 0)
        for bnd in allBnds:
            bnds.extendBy(bnd)

        # Move the camera and the target the bounding sphere's center.
        self.target.setPos(bnds.getCenter())
        self.setPos(bnds.getCenter())

        # Now move the camera back so the view accommodate all NodePaths.
        # Default the bounding radius to something reasonable if the object
        # has no size.
        fov = self.node().getLens().getFov()
        radius = bnds.getRadius() or 0.5
        dist = radius / math.tan(math.radians(min(fov[0], fov[1]) * 0.5))

        if direction == 0:
            self.setY(self, -dist)
        elif direction == 2:
            self.setPos(self.getPos()+LVecBase3f(0, 0, dist))
            self.setHpr(0, 270, 0)
        elif direction == 1:
            self.setPos(self.getPos()+LVecBase3f(dist, 0, 0))
            self.setHpr(90, 0, 0)
        elif direction == -1:
            self.setPos(self.getPos()+LVecBase3f(-dist, 0, 0))
            self.setHpr(-90, 0, 0)

    def update_axes(self):
        # update axes
        # Set rotation to inverse of camera rotation
        y_pos = common_maths.map_to_range(0, self.win.getYSize(), 0, 1, self.win.getYSize())
        aspect = self.win.getXSize() / self.win.getYSize()
        self.axes.set_pos(LVecBase3f(aspect - 0.25, 0, y_pos - 0.25))
        camera_quat = Quat(self.getQuat())
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
        test = LVecBase3f(move_vec.getX(), 0, move_vec.getZ())
        self.target.setPos(self.target, test)

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
        camera_vec = self.getPos() - self.target.getPos()
        cam_vec_dist = camera_vec.length()

        # Get new camera pos
        new_pos = LVecBase3f()
        new_pos.setX(cam_vec_dist * math.sin(rad_x) * math.cos(rad_y))
        new_pos.setY(-cam_vec_dist * math.cos(rad_x) * math.cos(rad_y))
        new_pos.setZ(-cam_vec_dist * math.sin(rad_y))
        new_pos += self.target.getPos()

        # Set camera to new pos
        self.setPos(new_pos)
