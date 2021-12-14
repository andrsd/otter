import contextlib
import fcntl
from PyQt5 import QtGui


@contextlib.contextmanager
def lock_file(filename):
    """
    Locks a file so that the exodus reader can safely read
    a file without something else writing to it while we do it.
    """
    with open(filename, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        yield
        fcntl.flock(f, fcntl.LOCK_UN)


def point_min(pt1, pt2):
    x = min(pt1.x(), pt2.x())
    y = min(pt1.y(), pt2.y())
    z = min(pt1.z(), pt2.z())
    return QtGui.QVector3D(x, y, z)


def point_max(pt1, pt2):
    x = max(pt1.x(), pt2.x())
    y = max(pt1.y(), pt2.y())
    z = max(pt1.z(), pt2.z())
    return QtGui.QVector3D(x, y, z)


def qcolor2vtk(qcolor):
    return [
        qcolor.redF(),
        qcolor.greenF(),
        qcolor.blueF()
    ]
