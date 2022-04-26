from __future__ import division
from panda3d.core import *
from editor.p3d.object import Object


class ThreeAxisGrid(Object):
    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)

        axis_xy = 1
        axis_xz = 0
        axis_yz = 0

        self.x_size = 200
        self.y_size = 200
        self.z_size = 200
        self.gridStep = 10
        self.sub_divisions = 10

        # Plane and end cap line visibility (1 is show, 0 is hide)
        self.xy_plane_show = axis_xy
        self.xz_plane_show = axis_xz
        self.yz_plane_show = axis_yz
        self.show_end_cape_lines = 1

        # Colors (RGBA passed as a VBase4 object)
        self.x_axis_color = VBase4(1, 0, 0, 1)
        self.y_axis_color = VBase4(0, 1, 0, 1)
        self.z_axis_color = VBase4(0, 0, 1, 1)
        self.grid_color = VBase4(0, 0, 0, 1)
        self.sub_div_color = VBase4(.35, .35, .35, 1)

        # Line thicknesses (in pixels)
        self.axis_thickness = 1
        self.grid_thickness = 1
        self.sub_div_thickness = 1

        # Axis, grid, and subdivisions lines must be separate LineSeg
        # objects in order to allow different thicknesses.
        # The parentNode groups them together for convenience.
        # All may be accessed individually if necessary.
        self.parentNode = None
        self.parentNodePath = None
        self.axisLinesNode = None
        self.axisLinesNodePath = None
        self.gridLinesNode = None
        self.gridLinesNodePath = None
        self.subdivLinesNode = None
        self.subdivLinesNodePath = None

        # Create line objects
        self.axisLines = LineSegs()
        self.gridLines = LineSegs()
        self.subdivLines = LineSegs()

    def create(self, size, grid_step, sub_divisions):
        self.x_size = self.y_size = self.z_size = size
        self.gridStep = grid_step
        self.sub_divisions = sub_divisions

        self.axisLines = LineSegs()
        self.gridLines = LineSegs()
        self.subdivLines = LineSegs()

        # Set line thicknesses
        self.axisLines.setThickness(self.axis_thickness)
        self.gridLines.setThickness(self.grid_thickness)
        self.subdivLines.setThickness(self.sub_div_thickness)

        # Check to see if primary grid lines should be drawn at all
        if self.gridStep != 0:

            # Draw primary grid lines
            self.gridLines.setColor(self.grid_color)

            # Draw primary grid lines metering x axis if any x-length
            if self.x_size != 0:
                if (self.y_size != 0) and (self.xy_plane_show != 0):
                    # Draw y lines across x-axis starting from center moving out XY Plane
                    for x in self.myfrange(0, self.x_size, self.gridStep):
                        self.gridLines.moveTo(x, -self.y_size, 0)
                        self.gridLines.drawTo(x, self.y_size, 0)
                        self.gridLines.moveTo(-x, -self.y_size, 0)
                        self.gridLines.drawTo(-x, self.y_size, 0)

                    if self.show_end_cape_lines != 0:
                        # Draw endcap lines
                        self.gridLines.moveTo(self.x_size, -self.y_size, 0)
                        self.gridLines.drawTo(self.x_size, self.y_size, 0)
                        self.gridLines.moveTo(-self.x_size, -self.y_size, 0)
                        self.gridLines.drawTo(-self.x_size, self.y_size, 0)

                if (self.z_size != 0) and (self.xz_plane_show != 0):
                    # Draw z lines across x axis starting from center moving out
                    # XZ Plane
                    for x in self.myfrange(0, self.x_size, self.gridStep):
                        self.gridLines.moveTo(x, 0, -self.z_size)
                        self.gridLines.drawTo(x, 0, self.z_size)
                        self.gridLines.moveTo(-x, 0, -self.z_size)
                        self.gridLines.drawTo(-x, 0, self.z_size)

                    if self.show_end_cape_lines != 0:
                        # Draw endcap lines
                        self.gridLines.moveTo(self.x_size, 0, -self.z_size)
                        self.gridLines.drawTo(self.x_size, 0, self.z_size)
                        self.gridLines.moveTo(-self.x_size, 0, -self.z_size)
                        self.gridLines.drawTo(-self.x_size, 0, self.z_size)

            # Draw primary grid lines metering y axis if any y-length
            if self.y_size != 0:
                if (self.y_size != 0) and (self.xy_plane_show != 0):
                    # Draw x lines across y axis
                    # XY Plane
                    for y in self.myfrange(0, self.y_size, self.gridStep):
                        self.gridLines.moveTo(-self.x_size, y, 0)
                        self.gridLines.drawTo(self.x_size, y, 0)
                        self.gridLines.moveTo(-self.x_size, -y, 0)
                        self.gridLines.drawTo(self.x_size, -y, 0)

                    if self.show_end_cape_lines != 0:
                        # Draw endcap lines
                        self.gridLines.moveTo(-self.x_size, self.y_size, 0)
                        self.gridLines.drawTo(self.x_size, self.y_size, 0)
                        self.gridLines.moveTo(-self.x_size, -self.y_size, 0)
                        self.gridLines.drawTo(self.x_size, -self.y_size, 0)

                if (self.z_size != 0) and (self.yz_plane_show != 0):
                    # Draw z lines across y axis
                    # YZ Plane
                    for y in self.myfrange(0, self.y_size, self.gridStep):
                        self.gridLines.moveTo(0, y, -self.z_size)
                        self.gridLines.drawTo(0, y, self.z_size)
                        self.gridLines.moveTo(0, -y, -self.z_size)
                        self.gridLines.drawTo(0, -y, self.z_size)

                    if self.show_end_cape_lines != 0:
                        # Draw endcap lines
                        self.gridLines.moveTo(0, self.y_size, -self.z_size)
                        self.gridLines.drawTo(0, self.y_size, self.z_size)
                        self.gridLines.moveTo(0, -self.y_size, -self.z_size)
                        self.gridLines.drawTo(0, -self.y_size, self.z_size)

            # Draw primary grid lines metering z axis if any z-length
            if self.z_size != 0:
                if (self.x_size != 0) and (self.xz_plane_show != 0):
                    # Draw x lines across z axis
                    # XZ Plane
                    for z in self.myfrange(0, self.z_size, self.gridStep):
                        self.gridLines.moveTo(-self.x_size, 0, z)
                        self.gridLines.drawTo(self.x_size, 0, z)
                        self.gridLines.moveTo(-self.x_size, 0, -z)
                        self.gridLines.drawTo(self.x_size, 0, -z)

                    if self.show_end_cape_lines != 0:
                        # Draw endcap lines
                        self.gridLines.moveTo(-(self.x_size), 0, self.z_size)
                        self.gridLines.drawTo(self.x_size, 0, self.z_size)
                        self.gridLines.moveTo(-(self.x_size), 0, -(self.z_size))
                        self.gridLines.drawTo(self.x_size, 0, -(self.z_size))

                if (self.y_size != 0) and (self.yz_plane_show != 0):
                    # Draw y lines across z axis
                    # YZ Plane
                    for z in self.myfrange(0, self.z_size, self.gridStep):
                        self.gridLines.moveTo(0, -(self.y_size), z)
                        self.gridLines.drawTo(0, self.y_size, z)
                        self.gridLines.moveTo(0, -(self.y_size), -z)
                        self.gridLines.drawTo(0, self.y_size, -z)

                    if self.show_end_cape_lines != 0:
                        # Draw endcap lines
                        self.gridLines.moveTo(0, -(self.y_size), self.z_size)
                        self.gridLines.drawTo(0, self.y_size, self.z_size)
                        self.gridLines.moveTo(0, -(self.y_size), -(self.z_size))
                        self.gridLines.drawTo(0, self.y_size, -(self.z_size))

        # Check to see if secondary grid lines should be drawn
        if self.sub_divisions != 0:
            # Draw secondary grid lines
            self.subdivLines.setColor(self.sub_div_color)

            if self.x_size != 0:
                adjustedstep = self.gridStep / self.sub_divisions
                if (self.y_size != 0) and (self.xy_plane_show != 0):
                    # Draw y lines across x axis starting from center moving out XY
                    for x in self.myfrange(0, self.x_size, adjustedstep):
                        self.subdivLines.moveTo(x, -(self.y_size), 0)
                        self.subdivLines.drawTo(x, self.y_size, 0)
                        self.subdivLines.moveTo(-x, -(self.y_size), 0)
                        self.subdivLines.drawTo(-x, self.y_size, 0)

                if (self.z_size != 0) and (self.xz_plane_show != 0):
                    # Draw z lines across x axis starting from center moving out
                    # XZ
                    for x in self.myfrange(0, self.x_size, adjustedstep):
                        self.subdivLines.moveTo(x, 0, -(self.z_size))
                        self.subdivLines.drawTo(x, 0, self.z_size)
                        self.subdivLines.moveTo(-x, 0, -(self.z_size))
                        self.subdivLines.drawTo(-x, 0, self.z_size)

            if self.y_size != 0:

                if (self.y_size != 0) and (self.xy_plane_show != 0):
                    # Draw x lines across y axis XY
                    for y in self.myfrange(0, self.y_size, adjustedstep):
                        self.subdivLines.moveTo(-(self.x_size), y, 0)
                        self.subdivLines.drawTo(self.x_size, y, 0)
                        self.subdivLines.moveTo(-(self.x_size), -y, 0)
                        self.subdivLines.drawTo(self.x_size, -y, 0)

                if (self.z_size != 0) and (self.yz_plane_show != 0):
                    # Draw z lines across y axis
                    # YZ
                    for y in self.myfrange(0, self.y_size, adjustedstep):
                        self.subdivLines.moveTo(0, y, -(self.z_size))
                        self.subdivLines.drawTo(0, y, self.z_size)
                        self.subdivLines.moveTo(0, -y, -(self.z_size))
                        self.subdivLines.drawTo(0, -y, self.z_size)

            if self.z_size != 0:
                if (self.x_size != 0) and (self.xz_plane_show != 0):
                    # Draw x lines across z axis XZ
                    for z in self.myfrange(0, self.z_size, adjustedstep):
                        self.subdivLines.moveTo(-self.x_size, 0, z)
                        self.subdivLines.drawTo(self.x_size, 0, z)
                        self.subdivLines.moveTo(-self.x_size, 0, -z)
                        self.subdivLines.drawTo(self.x_size, 0, -z)

                if (self.y_size != 0) and (self.yz_plane_show != 0):
                    # Draw y lines across z axis YZ
                    for z in self.myfrange(0, self.z_size, adjustedstep):
                        self.subdivLines.moveTo(0, -self.y_size, z)
                        self.subdivLines.drawTo(0, self.y_size, z)
                        self.subdivLines.moveTo(0, -self.y_size, -z)
                        self.subdivLines.drawTo(0, self.y_size, -z)

        if self.x_size != 0:
            # Draw X axis line
            self.axisLines.setColor(self.x_axis_color)
            self.axisLines.moveTo(0, 0, 0)
            self.axisLines.moveTo(-self.x_size, 0, 0)
            self.axisLines.drawTo(self.x_size, 0, 0)

        if self.y_size != 0:
            # Draw Y axis line
            self.axisLines.setColor(self.y_axis_color)
            self.axisLines.moveTo(0, -self.y_size, 0)
            self.axisLines.drawTo(0, self.y_size, 0)

        # Create ThreeAxisGrid nodes and nodepaths
        # Create parent node and path
        self.parentNode = PandaNode('threeaxisgrid-parentnode')
        self.parentNodePath = NodePath(self.parentNode)

        # Create axis lines node and path, then reparent
        self.axisLinesNode = self.axisLines.create()
        self.axisLinesNodePath = NodePath(self.axisLinesNode)
        self.axisLinesNodePath.reparentTo(self.parentNodePath)

        # Create grid lines node and path, then reparent
        self.gridLinesNode = self.gridLines.create()
        self.gridLinesNodePath = NodePath(self.gridLinesNode)
        self.gridLinesNodePath.reparentTo(self.parentNodePath)

        # Create subdivision lines node and path then reparent
        self.subdivLinesNode = self.subdivLines.create()
        self.subdivLinesNodePath = NodePath(self.subdivLinesNode)
        self.subdivLinesNodePath.reparentTo(self.parentNodePath)

        return self.parentNodePath

    # Thanks to Edvard Majakari for this float-accepting range method
    def myfrange(self, start, stop=None, step=None):
        if stop is None:
            stop = float(start)
            start = 0.0
        if step is None:
            step = 1.0
        cur = float(start)
        while cur < stop:
            yield cur
            cur += step
