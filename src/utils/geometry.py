import math
import panda3d.core as p3d


def GetPointsForSquare(x, y, reverse=False):
    points = [(-x / 2.0, -y / 2.0), (-x / 2.0, y / 2.0), (x / 2.0, y / 2.0), (x / 2.0, -y / 2.0)]

    # Reverse the order if necessary
    if reverse:
        points.reverse()

    return points


def GetPointsForBox(x, y, z):
    points = []

    for dx in (-x / 2.0, x / 2.0):
        for p in GetPointsForSquare(y, z, dx > 0):
            points.append((dx, p[0], p[1]))

    for dy in (-y / 2.0, y / 2.0):
        for p in GetPointsForSquare(x, z, dy < 0):
            points.append((p[0], dy, p[1]))

    for dz in (-z / 2.0, z / 2.0):
        for p in GetPointsForSquare(x, y, dz > 0):
            points.append((p[0], p[1], dz))

    return points


def GetPointsForArc(degrees, numSegs, reverse=False):
    points = []

    radians = math.radians(degrees)
    for i in range(numSegs + 1):
        a = radians * i / numSegs
        y = math.sin(a)
        x = math.cos(a)

        points.append((x, y))

    # Reverse the order if necessary
    if reverse:
        points.reverse()

    return points


def RotatePoint3(p, v1, v2):
    """
    Return the input point rotated around the cross of the input vectors. The
    amount to rotate is the angle between the two vectors.
    """
    v1 = p3d.Vec3(v1)
    v2 = p3d.Vec3(v2)
    v1.normalize()
    v2.normalize()
    cross = v1.cross(v2)
    cross.normalize()
    if cross.length():
        a = v1.angleDeg(v2)
        quat = p3d.Quat()
        quat.setFromAxisAngle(a, cross)
        p = quat.xform(p)

    return p


def GetGeomTriangle(v1, v2, v3):
    tri = p3d.GeomTriangles(p3d.Geom.UHDynamic)
    tri.addVertex(v1)
    tri.addVertex(v2)
    tri.addVertex(v3)
    tri.closePrimitive()

    return tri


def Circle(radius=1.0, numSegs=16, axis=p3d.Vec3(1, 0, 0),
           thickness=1.0, origin=p3d.Point3(0, 0, 0)):
    # Create line segments
    ls = p3d.LineSegs()
    ls.setThickness(thickness)

    # Get the points for an arc
    for p in GetPointsForArc(360, numSegs):
        # Draw the point rotated around the desired axis
        p = p3d.Point3(p[0], p[1], 0) - origin
        p = RotatePoint3(p, p3d.Vec3(0, 0, 1), p3d.Vec3(axis))
        ls.drawTo(p * radius)

    return ls.create()


def Square(width=1, height=1, axis=p3d.Vec3(1, 0, 0), thickness=1.0, origin=p3d.Point3(0, 0, 0)):
    """Return a geom node representing a wire square."""
    # Create line segments
    ls = p3d.LineSegs()
    ls.setThickness(thickness)

    # Get the points for a square
    points = GetPointsForSquare(width, height)
    points.append(points[0])
    for p in points:
        # Draw the point rotated around the desired axis
        p = p3d.Point3(p[0], p[1], 0) - origin
        p = RotatePoint3(p, p3d.Vec3(0, 0, 1), axis)
        ls.drawTo(p)

    # Return the geom node
    return ls.create()


def Cone(radius=1.0, height=2.0, numSegs=16, degrees=360,
         axis=p3d.Vec3(0, 0, 1), origin=p3d.Point3(0, 0, 0)):
    """Return a geom node representing a cone."""
    # Create vetex data format
    gvf = p3d.GeomVertexFormat.getV3n3()
    gvd = p3d.GeomVertexData('vertexData', gvf, p3d.Geom.UHStatic)

    # Create vetex writers for each type of data we are going to store
    gvwV = p3d.GeomVertexWriter(gvd, 'vertex')
    gvwN = p3d.GeomVertexWriter(gvd, 'normal')

    # Get the points for an arc
    axis2 = p3d.Vec3(axis)
    axis2.normalize()
    offset = axis2 * height / 2.0
    points = GetPointsForArc(degrees, numSegs, True)
    for i in range(len(points) - 1):

        # Rotate the points around the desired axis
        p1 = p3d.Point3(points[i][0], points[i][1], 0) * radius
        p1 = RotatePoint3(p1, p3d.Vec3(0, 0, 1), axis) - origin
        p2 = p3d.Point3(points[i + 1][0], points[i + 1][1], 0) * radius
        p2 = RotatePoint3(p2, p3d.Vec3(0, 0, 1), axis) - origin

        cross = (p2 - axis).cross(p1 - axis)
        cross.normalize()

        # Facet
        gvwV.addData3f(p1 - offset)
        gvwV.addData3f(offset - origin)
        gvwV.addData3f(p2 - offset)
        for j in range(3):
            gvwN.addData3f(cross)

        # Base
        gvwV.addData3f(p2 - offset)
        gvwV.addData3f(-offset - origin)
        gvwV.addData3f(p1 - offset)
        for k in range(3):
            gvwN.addData3f(-axis)

    geom = p3d.Geom(gvd)
    for i in range(0, gvwV.getWriteRow(), 3):
        # Create and add triangle
        geom.addPrimitive(GetGeomTriangle(i, i + 1, i + 2))

    # Return the cone GeomNode
    geomNode = p3d.GeomNode('cone')
    geomNode.addGeom(geom)
    return geomNode


def Cylinder(radius=1.0, height=2.0, numSegs=16, degrees=360,
             axis=p3d.Vec3(0, 0, 1), origin=p3d.Point3(0, 0, 0)):
    """Return a geom node representing a cylinder."""
    # Create vetex data format
    gvf = p3d.GeomVertexFormat.getV3n3()
    gvd = p3d.GeomVertexData('vertexData', gvf, p3d.Geom.UHStatic)

    # Create vetex writers for each type of data we are going to store
    gvwV = p3d.GeomVertexWriter(gvd, 'vertex')
    gvwN = p3d.GeomVertexWriter(gvd, 'normal')

    # Get the points for an arc
    # offset = height / 2.0
    axis2 = p3d.Vec3(axis)
    axis2.normalize()
    offset = axis2 * height / 2.0
    points = GetPointsForArc(degrees, numSegs, True)
    for i in range(len(points) - 1):

        # Rotate the points around the desired axis
        p1 = p3d.Point3(points[i][0], points[i][1], 0) * radius
        p1 = RotatePoint3(p1, p3d.Vec3(0, 0, 1), axis) - origin
        p2 = p3d.Point3(points[i + 1][0], points[i + 1][1], 0) * radius
        p2 = RotatePoint3(p2, p3d.Vec3(0, 0, 1), axis) - origin

        # Base
        gvwV.addData3f(p2 - offset)
        gvwV.addData3f(-offset - origin)
        gvwV.addData3f(p1 - offset)
        for j in range(3):
            gvwN.addData3f(-axis)

        # Cap
        gvwV.addData3f(p1 + offset)
        gvwV.addData3f(offset - origin)
        gvwV.addData3f(p2 + offset)
        for k in range(3):
            gvwN.addData3f(axis)

        # Sides
        gvwV.addData3f(p1 + offset)
        gvwV.addData3f(p2 + offset)
        gvwV.addData3f(p1 - offset)
        gvwV.addData3f(p2 - offset)
        gvwV.addData3f(p1 - offset)
        gvwV.addData3f(p2 + offset)
        cross = (p1 + offset - p1).cross(p2 - p1)
        for x in range(6):
            gvwN.addData3f(cross)

    geom = p3d.Geom(gvd)
    for i in range(0, gvwV.getWriteRow(), 3):
        # Create and add triangle
        geom.addPrimitive(GetGeomTriangle(i, i + 1, i + 2))

    # Return the cylinder GeomNode
    geomNode = p3d.GeomNode('cylinder')
    geomNode.addGeom(geom)
    return geomNode


def Sphere(radius=1.0, numSegs=16, degrees=360,
           axis=p3d.Vec3(0, 0, 1), origin=p3d.Point3(0, 0, 0)):
    """Return a geom node representing a cylinder."""
    # Create vetex data format
    gvf = p3d.GeomVertexFormat.getV3n3()
    gvd = p3d.GeomVertexData('vertexData', gvf, p3d.Geom.UHStatic)

    # Create vetex writers for each type of data we are going to store
    gvwV = p3d.GeomVertexWriter(gvd, 'vertex')
    gvwN = p3d.GeomVertexWriter(gvd, 'normal')

    # Get the points for an arc
    axis = p3d.Vec3(axis)
    axis.normalize()
    points = GetPointsForArc(degrees, numSegs, True)
    zPoints = GetPointsForArc(180, numSegs / 2, True)
    for z in range(1, len(zPoints) - 2):
        rad1 = zPoints[z][1] * radius
        rad2 = zPoints[z + 1][1] * radius
        offset1 = axis * zPoints[z][0] * radius
        offset2 = axis * zPoints[z + 1][0] * radius

        for i in range(len(points) - 1):

            # Get points
            p1 = p3d.Point3(points[i][0], points[i][1], 0) * rad1
            p2 = p3d.Point3(points[i + 1][0], points[i + 1][1], 0) * rad1
            p3 = p3d.Point3(points[i + 1][0], points[i + 1][1], 0) * rad2
            p4 = p3d.Point3(points[i][0], points[i][1], 0) * rad2

            # Rotate the points around the desired axis
            p1, p2, p3, p4 = [
                RotatePoint3(p, p3d.Vec3(0, 0, 1), axis)
                for p in [p1, p2, p3, p4]
            ]

            a = p1 + offset1 - origin
            b = p2 + offset1 - origin
            c = p3 + offset2 - origin
            d = p4 + offset2 - origin

            # Quad
            gvwV.addData3f(d)
            gvwV.addData3f(b)
            gvwV.addData3f(a)
            gvwV.addData3f(d)
            gvwV.addData3f(c)
            gvwV.addData3f(b)

            # Normals
            cross = (b - c).cross(a - c)
            for j in range(6):
                gvwN.addData3f(cross)

    # Get points
    rad1 = zPoints[1][1] * radius
    for m in [1, -2]:
        offset1 = axis * zPoints[m][0] * radius

        clampedM = max(-1, min(m, 1)) * radius

        for i in range(len(points) - 1):
            p1 = p3d.Point3(points[i][0], points[i][1], 0) * rad1
            p2 = p3d.Point3(points[i + 1][0], points[i + 1][1], 0) * rad1

            # Rotate the points around the desired axis
            p1, p2 = [
                RotatePoint3(p, p3d.Vec3(0, 0, 1), axis)
                for p in [p1, p2]
            ]

            a = p1 + offset1 - origin
            b = p2 + offset1 - origin
            c = -axis * clampedM

            # Quad
            if clampedM > 0:
                gvwV.addData3f(a)
                gvwV.addData3f(b)
                gvwV.addData3f(c)
            else:
                gvwV.addData3f(c)
                gvwV.addData3f(b)
                gvwV.addData3f(a)

            # Normals
            cross = (b - c).cross(a - c)
            for k in range(3):
                gvwN.addData3f(cross * -m)

    geom = p3d.Geom(gvd)
    for i in range(0, gvwV.getWriteRow(), 3):
        # Create and add triangle
        geom.addPrimitive(GetGeomTriangle(i, i + 1, i + 2))

    # Return the cylinder GeomNode
    geomNode = p3d.GeomNode('cylinder')
    geomNode.addGeom(geom)
    return geomNode


def Box(width=1, depth=1, height=1, origin=p3d.Point3(0, 0, 0)):
    """Return a geom node representing a box."""
    # Create vetex data format
    gvf = p3d.GeomVertexFormat.getV3n3()
    gvd = p3d.GeomVertexData('vertexData', gvf, p3d.Geom.UHStatic)

    # Create vetex writers for each type of data we are going to store
    gvwV = p3d.GeomVertexWriter(gvd, 'vertex')
    gvwN = p3d.GeomVertexWriter(gvd, 'normal')

    # Write out all points
    for p in GetPointsForBox(width, depth, height):
        gvwV.addData3f(p3d.Point3(p) - origin)

    # Write out all the normals
    for n in ((-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)):
        for i in range(4):
            gvwN.addData3f(n)

    geom = p3d.Geom(gvd)
    for i in range(0, gvwV.getWriteRow(), 4):
        # Create and add both triangles
        geom.addPrimitive(GetGeomTriangle(i, i + 1, i + 2))
        geom.addPrimitive(GetGeomTriangle(i, i + 2, i + 3))

    # Return the box GeomNode
    geomNode = p3d.GeomNode('box')
    geomNode.addGeom(geom)
    return geomNode


def Line(start, end, thickness=1.0):
    """Return a geom node representing a simple line."""
    # Create line segments
    ls = p3d.LineSegs()
    ls.setThickness(thickness)
    ls.drawTo(p3d.Point3(start))
    ls.drawTo(p3d.Point3(end))

    # Return the geom node
    return ls.create()


def QuadWireframe(egg):
    def RecursePoly(node, geo):

        if isinstance(node, p3d.EggPolygon):

            # Get each vert position
            poss = []
            for vert in node.getVertices():
                pos3 = vert.getPos3()
                pos = p3d.Point3(pos3.getX(), pos3.getY(), pos3.getZ())
                poss.append(pos)

            # Build lines
            geo.combineWith(Line(poss[0], poss[1]))
            geo.combineWith(Line(poss[1], poss[2]))
            geo.combineWith(Line(poss[2], poss[3]))
            geo.combineWith(Line(poss[3], poss[0]))

        # Recurse down hierarchy
        if hasattr(node, 'getChildren'):
            for child in node.getChildren():
                RecursePoly(child, geo)

        return geo

    return RecursePoly(egg, p3d.GeomNode('quadWireframe'))


def Axes(thickness=1, length=25):
    """Class representing the viewport camera axes."""
    # Build line segments
    ls = p3d.LineSegs()
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


class Arc(p3d.NodePath):
    """NodePath class representing a wire arc."""

    def __init__(self, radius=1.0, numSegs=16, degrees=360, axis=p3d.Vec3(1, 0, 0),
                 thickness=1.0, origin=p3d.Point3(0, 0, 0)):
        # Create line segments
        self.ls = p3d.LineSegs()
        self.ls.setThickness(thickness)

        # Get the points for an arc
        for p in GetPointsForArc(degrees, numSegs):
            # Draw the point rotated around the desired axis
            p = p3d.Point3(p[0], p[1], 0) - origin
            p = RotatePoint3(p, p3d.Vec3(0, 0, 1), p3d.Vec3(axis))
            self.ls.drawTo(p * radius)

        # Init the node path, wrapping the lines
        node = self.ls.create()
        p3d.NodePath.__init__(self, node)


class Polygon(p3d.NodePath):
    def __init__(self, points, label="Polygon", normals=None, texcoords=None,
                 origin=p3d.Point3(0, 0, 0)):

        # Create vetex data format
        gvf = p3d.GeomVertexFormat.getV3n3t2()
        gvd = p3d.GeomVertexData('vertexData', gvf, p3d.Geom.UHStatic)

        # Create vetex writers for each type of data we are going to store
        gvwV = p3d.GeomVertexWriter(gvd, 'vertex')
        gvwN = p3d.GeomVertexWriter(gvd, 'normal')
        gvwT = p3d.GeomVertexWriter(gvd, 'texcoord')

        # Write out all points and normals
        for i, point in enumerate(points):
            p = p3d.Point3(point) - origin
            gvwV.addData3f(p)

            # Calculate tex coords if none specified
            if texcoords is None:
                gvwT.addData2f(p.x, p.y)
            else:
                gvwT.addData2f(texcoords[i])

            # Calculate normals if none specified
            if normals is None:
                prevPoint = (points[-1] if i == 0 else points[i - 1])
                nextPoint = (points[0] if i == len(points) - 1 else points[i + 1])
                cross = (nextPoint - point).cross(prevPoint - point)
                cross.normalize()
                gvwN.addData3f(cross)
            else:
                gvwN.addData3f(normals[i])

        geom = p3d.Geom(gvd)
        for i in range(len(points) - 1):
            # Create and add both triangles
            geom.addPrimitive(GetGeomTriangle(0, i, i + 1))

        # Init the node path, wrapping the polygon
        geomNode = p3d.GeomNode(label)
        geomNode.addGeom(geom)
        p3d.NodePath.__init__(self, geomNode)


class GeomUtils:
    @staticmethod
    def invert_normals(node_path):
        geom_node = node_path.node()
        current_thread = p3d.Thread.getCurrentThread()

        for i in range(geom_node.getNumGeoms()):
            geom = geom_node.getGeom(i)
            vdata = geom.getVertexData()
        
            # Create a GeomVertexRewriter to invert the normals
            normal_rewriter = p3d.GeomVertexRewriter(vdata,
                                                     p3d.InternalName.getNormal(),
                                                     current_thread)
            while not normal_rewriter.isAtEnd():
                normal = normal_rewriter.getData3f()
                normal_rewriter.setData3f(-normal)

            # Set the modified vertex data back to the geom
            geom.setVertexData(vdata)
