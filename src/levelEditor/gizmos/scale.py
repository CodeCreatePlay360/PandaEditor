import math

from panda3d.core import Mat4, Vec3, Point3, CollisionSphere, NodePath
from utils.geometry import Box, Line
from utils.math import get_trs_matrices
from .axis import Axis
from .base import Base
from .constants import *


class Scale(Base):

    def __init__(self, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)

        self.__complementary = False

        # Create x, y, z and center axes
        self.axes.append(self.create_box(Vec3(1, 0, 0), RED))
        self.axes.append(self.create_box(Vec3(0, 1, 0), GREEN))
        self.axes.append(self.create_box(Vec3(0, 0, 1), BLUE))
        self.axes.append(self.create_center(Vec3(1, 1, 1), TEAL))

    def create_box(self, vector, colour):

        # Create the geometry and collision
        line = NodePath(Line((0, 0, 0), vector))
        box = NodePath(Box(0.1, 0.1, 0.1, vector * 0.05))

        collSphere = CollisionSphere(Point3(vector * -0.05), 0.1)

        # Create the axis, add the geometry and collision
        axis = Axis(self.name, vector, colour)
        axis.add_geometry(line, colour=GREY, highlight=False, sizeStyle=SCALE)
        axis.add_geometry(box, vector, colour)
        axis.add_collision_solid(collSphere, vector)
        axis.reparentTo(self)

        return axis

    def create_center(self, vector, colour):

        # Create the axis, add the geometry and collision
        axis = Axis(self.name, vector, colour, default=True)
        axis.add_geometry(NodePath(Box(0.1, 0.1, 0.1)), sizeStyle=NONE)
        axis.add_collision_solid(CollisionSphere(0, 0.1), sizeStyle=NONE)
        axis.reparentTo(self)

        return axis

    def transform(self):

        # Get the distance the mouse has moved during the drag operation -
        # compensate for how big the gizmo is on the screen
        axis = self.get_selected_axis()
        axisPoint = self.get_axis_point(axis)
        distance = (axisPoint - self.start_axis_point).length() / self.getScale()[0]

        # Using length() will give us a positive number, which doesn't work if
        # we're trying to scale down the object. Get the sign for the distance
        # from the dot of the axis and the mouse direction
        mousePoint = self.getRelativePoint(self.rootNp, axisPoint) - self.getRelativePoint(self.rootNp,
                                                                                           self.start_axis_point)
        direction = axis.vector.dot(mousePoint)
        sign = math.copysign(1, direction)
        distance = distance * sign

        # Transform the gizmo
        if axis.vector == Vec3(1, 1, 1):
            for otherAxis in self.axes:
                otherAxis.set_size(distance + self.size)
        else:
            axis.set_size(distance + self.size)

        # Use the "complementary" vector if in complementary mode
        vector = axis.vector
        if self.__complementary:
            vector = Vec3(1, 1, 1) - axis.vector

        # Create a scale matrix from the resulting vector
        scaleVec = vector * (distance + 1) + Vec3(1, 1, 1) - vector
        newScaleMat = Mat4().scaleMat(scaleVec)

        # Transform attached node paths
        for i, np in enumerate(self.attached_nps):

            # Perform transforms in local or world space
            if self.local:
                np.setMat(newScaleMat * self.init_np_xforms[i].getMat())
            else:
                transMat, rotMat, scaleMat = get_trs_matrices(self.init_np_xforms[i])
                np.setMat(scaleMat * rotMat * newScaleMat * transMat)

    def on_node_mouse1_down(self, planar, collEntry):

        # Cheating a bit here. We just need the planar flag taken from the
        # user ctrl-clicking the gizmo, none of the maths that come with it.
        # We'll use the complementary during the transform operation.
        self.__complementary = planar
        planar = False

        Base.on_node_mouse1_down(self, planar, collEntry)
