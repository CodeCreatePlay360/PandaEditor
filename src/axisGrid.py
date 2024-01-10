from __future__ import division
from panda3d.core import *


class ThreeAxisGrid(NodePath):
    def __init__(self, *args, **kwargs):
        NodePath.__init__(self, "AxisGrid")
        self.grid_size = 100
        self.grid_step = 10
        self.sub_divisions = 10

        # Plane and end cap line visibility (1 is show, 0 is hide)
        self.show_end_cape_lines = 1

        # Colors (RGBA passed as a VBase4 object)
        self.x_axis_color = VBase4(1, 0, 0, 1)
        self.y_axis_color = VBase4(0, 1, 0, 1)

        self.grid_color = VBase4(0.4, 0.4, 0.4, 1)
        self.sub_div_color = VBase4(0.35, 0.35, 0.35, 1)

        # Line thicknesses (in pixels)
        self.axis_thickness = 1
        self.grid_thickness = 1
        self.sub_div_thickness = 1

        # Axis, grid, and subdivisions lines must be separate LineSeg
        # objects in order to allow different thicknesses.
        # The parentNode groups them together for convenience.
        # All may be accessed individually if necessary.

        self.axisLinesNode = None
        self.axisLinesNodePath = None
        
        self.gridLinesNode = None
        self.gridLinesNodePath = None
        
        self.subdivLinesNode = None
        self.subdivLinesNodePath = None

        self.axisLines = LineSegs()
        self.gridLines = LineSegs()
        self.subdivision_Lines = LineSegs()

    def create(self, size, grid_step, sub_divisions):
        self.grid_size = size
        self.grid_step = grid_step
        self.sub_divisions = sub_divisions

        # self.axisLines = LineSegs()
        self.axisLines.moveTo(0, 0, 0)

        # self.gridLines = LineSegs()
        self.gridLines.moveTo(0, 0, 0)

        # self.subdivision_Lines = LineSegs()
        self.subdivision_Lines.moveTo(0, 0, 0)

        # Set line thicknesses
        self.axisLines.setThickness(self.axis_thickness)
        self.gridLines.setThickness(self.grid_thickness)
        self.subdivision_Lines.setThickness(self.sub_div_thickness)

        self.gridLines.setColor(self.grid_color)
        self.subdivision_Lines.setColor(self.sub_div_color)

        # Draw primary grid lines
        for x in self.myfrange(0, self.grid_size, self.grid_step):
            self.gridLines.moveTo(x, -self.grid_size, 0)
            self.gridLines.drawTo(x, self.grid_size, 0)
            self.gridLines.moveTo(-x, -self.grid_size, 0)
            self.gridLines.drawTo(-x, self.grid_size, 0)

        # Draw end cap lines
        # self.gridLines.moveTo(self.grid_size, -self.grid_size, 0)
        # self.gridLines.drawTo(self.grid_size, self.grid_size, 0)
        # self.gridLines.moveTo(-self.grid_size, -self.grid_size, 0)
        # self.gridLines.drawTo(-self.grid_size, self.grid_size, 0)

        for z in self.myfrange(0, self.grid_size, self.grid_step):
            self.gridLines.moveTo(-self.grid_size, z, 0)
            self.gridLines.drawTo(self.grid_size, z, 0)
            self.gridLines.moveTo(-self.grid_size, -z, 0)
            self.gridLines.drawTo(self.grid_size, -z, 0)

        # Draw end cap lines
        # self.gridLines.moveTo(self.grid_size, -self.grid_size, 0)
        # self.gridLines.drawTo(-self.grid_size, -self.grid_size, 0)
        # self.gridLines.moveTo(-self.grid_size, self.grid_size, 0)
        # self.gridLines.drawTo(self.grid_size, self.grid_size, 0)

        adjusted_step = self.grid_step / self.sub_divisions

        for x in self.myfrange(0, self.grid_size, adjusted_step):
            self.subdivision_Lines.moveTo(x, -self.grid_size, 0)
            self.subdivision_Lines.drawTo(x, self.grid_size, 0)
            self.subdivision_Lines.moveTo(-x, -self.grid_size, 0)
            self.subdivision_Lines.drawTo(-x, self.grid_size, 0)

        for y in self.myfrange(0, self.grid_size, adjusted_step):
            self.subdivision_Lines.moveTo(-self.grid_size, y, 0)
            self.subdivision_Lines.drawTo(self.grid_size, y, 0)
            self.subdivision_Lines.moveTo(-self.grid_size, -y, 0)
            self.subdivision_Lines.drawTo(self.grid_size, -y, 0)

        # Draw X axis line
        self.axisLines.setColor(self.x_axis_color)
        self.axisLines.moveTo(0, 0, 0)
        self.axisLines.moveTo(-self.grid_size, 0, 0)
        self.axisLines.drawTo(self.grid_size, 0, 0)

        # Draw Y axis line
        self.axisLines.setColor(self.y_axis_color)
        self.axisLines.moveTo(0, 0, 0)
        self.axisLines.moveTo(0, -self.grid_size, 0)
        self.axisLines.drawTo(0, self.grid_size, 0)

        # Create axis lines node and path, then re-parent
        self.axisLinesNode = self.axisLines.create(None)
        self.axisLinesNodePath = NodePath(self.axisLinesNode)
        self.axisLinesNodePath.reparentTo(self)

        # Create grid lines node and path, then re-parent
        self.gridLinesNode = self.gridLines.create(None)
        self.gridLinesNodePath = NodePath(self.gridLinesNode)
        self.gridLinesNodePath.reparentTo(self)

        # Create subdivision lines node and path then re-parent
        self.subdivLinesNode = self.subdivision_Lines.create(None)
        self.subdivLinesNodePath = NodePath(self.subdivLinesNode)
        self.subdivLinesNodePath.reparentTo(self)

        # self.parentNodePath = self

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
