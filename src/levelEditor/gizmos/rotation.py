import math

from panda3d.core import (Mat4, Vec3, Point3, Plane, NodePath, 
                          CollisionSphere, CollisionPolygon, BillboardEffect)
from utils.math import get_trs_matrices
from utils.geometry import Arc, Line
from .axis import Axis
from .base import Base
from .constants import *


class Rotation(Base):
    def __init__(self, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)

        self.__camera = kwargs.pop("camera")

        # instance attributes
        self.coll_entry = None
        self.start_vec = None
        self.cam_axis = None
        self.init_coll_entry = None

        # Create the 'ball' border
        self.__border = self.create_circle(GREY, 1)

        # Create the collision sphere - except for the camera normal, all axes
        # will use this single collision object
        self.__coll_sphere = CollisionSphere(0, 1)

        # Create x, y, z and camera normal axes
        self.axes.append(self.create_ring(Vec3(1, 0, 0), RED, Vec3(0, 0, 90)))
        self.axes.append(self.create_ring(Vec3(0, 1, 0), GREEN, Vec3(0, 90, 0)))
        self.axes.append(self.create_ring(Vec3(0, 0, 1), BLUE, Vec3(0, 0, 0)))

        # DEBUG
        self.__foobar = self.create_cam_circle(TEAL, 1.2)
        self.axes.append(self.__foobar)

        self.set_size(0.7)

    def create_ring(self, vector, colour, rot):

        # Create an arc
        arc = Arc(numSegs=32, degrees=180, axis=Vec3(0, 0, 1))
        arc.setH(180)

        # Create the axis from the arc
        axis = Axis(self.name, vector, colour)
        axis.add_geometry(arc, sizeStyle=SCALE)
        axis.add_collision_solid(self.__coll_sphere, sizeStyle=SCALE)
        axis.reparentTo(self)

        # Create the billboard effect and apply it to the arc. We need an
        # extra NodePath to help the billboard effect, so it orients properly.
        hlpr = NodePath('helper')
        hlpr.setHpr(rot)
        hlpr.reparentTo(self)
        arc.reparentTo(hlpr)
        bbe = BillboardEffect.make(Vec3(0, 0, 1), False, True, 0, self.__camera, (0, 0, 0))
        arc.setEffect(bbe)

        return axis

    def create_circle(self, colour, radius):

        # Create a circle
        arc = Arc(radius, numSegs=64, axis=Vec3(0, 1, 0))
        arc.setColorScale(colour)
        arc.setLightOff()
        arc.reparentTo(self)

        # Set the billboard effect
        arc.setBillboardPointEye()

        return arc

    def create_cam_circle(self, colour, radius):

        # Create the geometry and collision
        circle = self.create_circle(colour, radius)
        collPoly = CollisionPolygon(Point3(-1.2, 0, -1.2), Point3(-1.25, 0, 1.25), Point3(1.25, 0, 1.25),
                                    Point3(1.25, 0, -1.25))

        # Create the axis, add the geometry and collision
        self.cam_axis = Axis(self.name, CAMERA_VECTOR, colour, planar=True, default=True)
        self.cam_axis.add_geometry(circle, sizeStyle=SCALE)
        self.cam_axis.add_collision_solid(collPoly, sizeStyle=SCALE)
        self.cam_axis.reparentTo(self)

        return self.cam_axis

    def set_size(self, factor):
        Base.set_size(self, factor)

        # Scale up any additional geo
        self.__border.setScale(self.size)

    def get_axis(self, collEntry):
        axis = Base.get_axis(self, collEntry)

        # Return None if the axis is None
        if axis is None:
            return None

        if axis.vector != CAMERA_VECTOR:

            # Return the axis from the specified normal within a tolerance of 
            # degrees
            normal = collEntry.getSurfaceNormal(self)
            normal.normalize()
            for axis in self.axes:
                if math.fabs(normal.angleDeg(axis.vector) - 90) < (2.5 / self.size):
                    return axis
        else:

            # Get the collision point on the poly, return the axis if the
            # mouse is within tolerance of the circle
            point = collEntry.getSurfacePoint(collEntry.getIntoNodePath())
            length = Vec3(point / 1.25).length()
            if 0.9 < length < 1:
                return axis

    def update(self, task):
        Base.update(self, task)

        # DEBUG - make the camera normal collision plane look at the camera.
        # Probably should be a better way to do this.
        self.cam_axis.coll_node_paths[0].lookAt(self.__camera)

        return task.cont

    def transform(self):
        startVec = self.start_vec
        axis = self.get_selected_axis()

        if axis is not None and axis.vector == CAMERA_VECTOR:
            endVec = self.get_relative_vector(self.rootNp, self.get_axis_point(axis) - self.getPos())

            cross = startVec.cross(endVec)
            direction = self.get_relative_vector(self.__camera, Vec3(0, -1, 0)).dot(cross)
            sign = math.copysign(1, direction)

            # Get the rotation axis
            rotAxis = self.get_relative_vector(self.__camera, Vec3(0, -1, 0)) * sign
        else:
            if self.coll_entry.getIntoNode() == self.init_coll_entry.getIntoNode():
                endVec = self.coll_entry.getSurfaceNormal(self)
            else:
                endVec = self.get_relative_vector(self.rootNp, self.get_axis_point(self.__foobar) - self.getPos())

            # If an axis is selected then constrain the vectors by projecting
            # them onto a plane whose normal is the axis vector
            if axis is not None:
                plane = Plane(axis.vector, Point3(0))
                startVec = Vec3(plane.project(Point3(startVec)))
                endVec = Vec3(plane.project(Point3(endVec)))

            # Get the rotation axis
            rotAxis = endVec.cross(startVec) * -1

        # Return if the rotation vector is not valid, ie it does not have any
        # length
        if not rotAxis.length():
            return

        # Normalize all vectors
        startVec.normalize()
        endVec.normalize()
        rotAxis.normalize()

        # Get the amount of degrees to rotate
        degs = startVec.angleDeg(endVec)

        # Transform the gizmo if in local rotation mode
        newRotMat = Mat4().rotateMat(degs, rotAxis)
        if self.local:
            self.setMat(newRotMat * self.getMat())

        # Transform all attached node paths
        for i, np in enumerate(self.attached_nps):

            # Split the transform into scale, rotation and translation
            # matrices
            transMat, rotMat, scaleMat = get_trs_matrices(np.getTransform())

            # Perform transforms in local or world space
            if self.local:
                np.setMat(scaleMat * newRotMat * rotMat * transMat)
            else:
                self.init_np_xforms[i].getQuat().extractToMatrix(rotMat)
                np.setMat(scaleMat * rotMat * newRotMat * transMat)

    def on_node_mouse1_down(self, planar, collEntry):
        Base.on_node_mouse1_down(self, planar, collEntry)

        # Store the initial collision entry
        self.init_coll_entry = collEntry

        # If the selected axis is the camera vector then use a point on the
        # plane whose normal is the camera vector as the starting vector,
        # otherwise use the surface normal from the collision with the sphere
        axis = self.get_selected_axis()
        if axis is not None and axis.vector == CAMERA_VECTOR:
            self.start_vec = self.get_relative_vector(self.rootNp, self.start_axis_point - self.getPos())
        else:
            self.start_vec = self.init_coll_entry.getSurfaceNormal(self)

    def on_mouse2_down(self):
        Base.on_mouse2_down(self)

        # axis = self.GetSelectedAxis()
        if (hasattr(self, 'collEntry') and hasattr(self, 'initCollEntry') and
                self.coll_entry.getIntoNode() != self.init_coll_entry.getIntoNode()):

            self.start_vec = self.get_relative_vector(self.rootNp,
                                                      self.get_axis_point(self.__foobar) - self.getPos())
        else:
            self.start_vec = self.get_relative_vector(self.rootNp,
                                                      self.startAxisPoint - self.getPos())

    def on_node_mouse_over(self, collEntry):
        Base.on_node_mouse_over(self, collEntry)

        # Store the collision entry
        self.coll_entry = collEntry
