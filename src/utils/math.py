from panda3d.core import Point3, Vec3, Mat4
from direct.directtools.DirectUtil import ROUND_TO


def closest_point_to_line(c, a, b):
    """Returns the closest point online ab to input point c."""
    u = (c[0] - a[0]) * (b[0] - a[0]) + (c[1] - a[1]) * (b[1] - a[1]) + (c[2] - a[2]) * (b[2] - a[2])
    u = u / ((a - b).length() * (a - b).length())

    x = a[0] + u * (b[0] - a[0])
    y = a[1] + u * (b[1] - a[1])
    z = a[2] + u * (b[2] - a[2])

    return Point3(x, y, z)


def get_trs_matrices(xform):
    """
    Return translation, rotation and scale matrices back for the specified
    transform.
    """
    # Get translation and rotation matrices
    rotMat = Mat4()
    xform.getQuat().extractToMatrix(rotMat)
    transMat = Mat4().translateMat(xform.getPos())

    # More care must be taken to get the scale matrix as simply calling
    # Mat4().scaleMat( xform.getScale() ) won't account for shearing or other
    # weird scaling. To get this matrix simply remove the translation and
    # rotation components from the xform.
    invRotMat = Mat4()
    invRotMat.invertFrom(rotMat)
    invTransMat = Mat4()
    invTransMat.invertFrom(transMat)
    scaleMat = xform.getMat() * invTransMat * invRotMat

    return transMat, rotMat, scaleMat


def scale_point(pnt, scl, invert=False):
    """
    Return a new point based on the indicated point xformed by a matrix 
    constructed by the indicated scale. Invert the scale matrix if required.
    """
    sclMat = Mat4().scaleMat(scl)
    if invert:
        sclMat.invertInPlace()
    return sclMat.xformPoint(pnt)


def snap_point(pnt, amt):
    """
    Return a new point based on the indicated point but snapped to the nearest
    indicated amount.
    """
    return Vec3(ROUND_TO(pnt[0], amt),
                ROUND_TO(pnt[1], amt),
                ROUND_TO(pnt[2], amt))
