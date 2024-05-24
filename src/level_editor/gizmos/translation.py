import panda3d.core as pm

from direct.directtools.DirectUtil import ROUND_TO
from system import Systems

from utils.geometry import Cone, Square, Line
from utils.math import snap_point, scale_point
from .axis import Axis
from .base import Base
from .constants import *

TOL = 0.1


class Translation(Base):

    def __init__(self, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)

        self.snpAmt = 0.5

        self.snap = False
        self.snap_distance = None
        self.square_np = None

        # Create x, y, z and camera normal axes
        self.axes.append(self.create_arrow(pm.Vec3(1, 0, 0), RED))
        self.axes.append(self.create_arrow(pm.Vec3(0, 1, 0), GREEN))
        self.axes.append(self.create_arrow(pm.Vec3(0, 0, 1), BLUE))
        # self.axes.append( self.CreateArrow( pm.Vec3(1, 1, 0), YELLOW ) )
        # self.axes.append( self.CreateArrow( pm.Vec3(-2, 1, 0), TEAL ) )
        self.axes.append(self.create_square(pm.Vec3(0, 0, 0), TEAL))

    def create_arrow(self, vec, colour):
        # Create the geometry and collision
        vec.normalize()
        line = pm.NodePath(Line((0, 0, 0), vec))
        cone = pm.NodePath(Cone(0.05, 0.25, axis=vec, origin=vec * 0.125))
        collTube = pm.CollisionTube((0, 0, 0), pm.Point3(vec) * 0.95, 0.05)

        # Create the axis, add the geometry and collision
        axis = Axis(self.name, vec, colour)
        axis.add_geometry(line, sizeStyle=SCALE)
        axis.add_geometry(cone, vec, colour)
        axis.add_collision_solid(collTube, sizeStyle=TRANSLATE_POINT_B)
        axis.reparentTo(self)

        return axis

    def create_square(self, vec, colour):
        # Create the geometry and collision
        self.square_np = pm.NodePath(Square(0.2, 0.2, pm.Vec3(0, 1, 0)))
        self.square_np.setBillboardPointEye()
        collSphere = pm.CollisionSphere(0, 0.125)

        # Create the axis, add the geometry and collision
        axis = Axis(self.name, CAMERA_VECTOR, colour, planar=True, default=True)
        axis.add_geometry(self.square_np, sizeStyle=NONE)
        axis.add_collision_solid(collSphere, sizeStyle=NONE)
        axis.reparentTo(self)

        return axis

    def _snap(self, vec):
        if vec.length():
            snpLen = ROUND_TO(vec.length(), self.snpAmt)
            snapVec = vec / vec.length() * snpLen
            return snapVec
        else:
            return pm.Vec3(0)

    def transform(self):
        axis = self.get_selected_axis()
        axisPoint = self.get_axis_point(axis)

        # Calculate delta and snapping.
        d = axisPoint - self.last_axis_point
        lastSnap = self._snap(self.snap_distance)
        self.snap_distance += d
        thisSnap = self._snap(self.snap_distance)

        if self.snap:

            # If snapping in planar mode or using the camera axis, snap to a
            # point on the ground plane.
            if axis.vector == CAMERA_VECTOR or self.planar:
                pnt = self.get_mouse_plane_collision_point(pm.Point3(0), pm.Vec3(0, 0, 1))
                pnt = snap_point(pnt, self.snpAmt)

                self.setPos(self.render, pnt)
                for np in self.attachedNps:
                    np.setPos(self.render, pnt)

                return

            # If snapping in world space, construct a plane where the mouse
            # clicked the axis and move all NodePaths, so they intersect it.
            elif not self.local:
                pnt = snap_point(self.startAxisPoint + d, self.snpAmt)
                pl = pm.Plane(axis.vector, pm.Point3(pnt))

                self.setPos(self.render, pl.project(self.getPos(self.render)))
                for np in self.attachedNps:
                    np.setPos(self.render, pl.project(np.getPos(self.render)))

                return

            # Gone over the snap threshold - set the delta to the snap amount.
            elif thisSnap.compareTo(lastSnap, TOL):
                d.normalize()
                d *= self.snpAmt

                # BUG - need to resize to compensate for cam dist?

            # In snapping mode but haven't gone past the snap threshold.
            else:
                d = pm.Vec3(0)

        d = self.getRelativeVector(self.rootNp, d)
        self.setMat(pm.Mat4().translateMat(d) * self.getMat())

        # Adjust the size of delta by the gizmo size to get real world units.
        d = scale_point(d, self.getScale())

        # Hack for fixing camera vector xforming in local mode.
        if self.local and axis.vector == CAMERA_VECTOR:
            d = self.rootNp.getRelativeVector(self, d)
            d = scale_point(d, self.getScale(), True)

        # Xform attached NodePaths.
        for np in self.attached_nps:
            if self.local and axis.vector != CAMERA_VECTOR:
                sclD = scale_point(d, np.getScale(self.rootNp), True)
                np.setMat(pm.Mat4().translateMat(sclD) * np.getMat())
            else:
                np.setMat(self.rootNp, np.getMat(self.rootNp) *
                          pm.Mat4().translateMat(d))

        self.last_axis_point = axisPoint

    def on_node_mouse1_down(self, planar, collEntry):
        Base.on_node_mouse1_down(self, planar, collEntry)

        self.snap_distance = pm.Vec3(0)

        # If in planar mode, clear the billboard effect on the center square
        # and make it face the selected axis
        axis = self.get_selected_axis()
        if self.planar and not axis.planar:
            self.square_np.clearBillboard()
            self.square_np.lookAt(self, pm.Point3(axis.vector))
        else:
            self.square_np.setHpr(pm.Vec3(0, 0, 0))
            self.square_np.setBillboardPointEye()

    def on_mouse2_down(self):
        Base.on_mouse2_down(self)
        self.snap_distance = pm.Vec3(0)

    def accept_events(self):
        Base.accept_events(self)
        Systems.demon.accept('x', self.set_snap, [True])
        Systems.demon.accept('x-up', self.set_snap, [False])

    def set_snap(self, val):
        self.snap = val
