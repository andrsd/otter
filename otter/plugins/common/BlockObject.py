import vtk
from PyQt5 import QtGui
import otter.plugins.common as common


class BlockObject:
    """
    Object that encapualates VTK around a mesh block
    """

    def __init__(self, eb, camera):
        do = eb.GetOutput()
        self._bounds = self._computeBounds(do)

        self._info = {
            'cells': do.GetNumberOfCells(),
            'points': do.GetNumberOfPoints(),
        }

        self._geometry = vtk.vtkCompositeDataGeometryFilter()
        self._geometry.SetInputConnection(0, eb.GetOutputPort(0))
        self._geometry.Update()

        self._mapper = vtk.vtkPolyDataMapper()
        self._mapper.SetInputConnection(self._geometry.GetOutputPort())
        self._mapper.SetScalarModeToUsePointFieldData()
        self._mapper.InterpolateScalarsBeforeMappingOn()

        self._actor = vtk.vtkActor()
        self._actor.SetMapper(self._mapper)
        self._actor.SetScale(0.99999)
        self._actor.VisibilityOn()

        self._property = self._actor.GetProperty()
        self._property.SetRepresentationToSurface()

        self._color = [1, 1, 1]

        bnds = self._actor.GetBounds()
        self._cob = common.centerOfBounds(bnds)

        self._setUpSilhouette(camera)

    def _setUpSilhouette(self, camera):
        self._silhouette = vtk.vtkPolyDataSilhouette()
        self._silhouette.SetInputData(self._mapper.GetInput())
        self._silhouette.SetCamera(camera)

        self._silhouette_mapper = vtk.vtkPolyDataMapper()
        self._silhouette_mapper.SetInputConnection(
            self._silhouette.GetOutputPort())

        self._silhouette_actor = vtk.vtkActor()
        self._silhouette_actor.SetMapper(self._silhouette_mapper)
        self._silhouette_actor.VisibilityOff()

        self._silhouette_property = self._silhouette_actor.GetProperty()
        self._silhouette_property.SetColor([0, 0, 0])
        self._silhouette_property.SetLineWidth(3)

    def setColor(self, color):
        self._color = color

    @property
    def actor(self):
        return self._actor

    @property
    def info(self):
        return self._info

    @property
    def color(self):
        return self._color

    @property
    def cob(self):
        return self._cob

    @property
    def bounds(self):
        return self._bounds

    @property
    def geometry(self):
        return self._geometry

    @property
    def silhouette_actor(self):
        return self._silhouette_actor

    @property
    def silhouette_property(self):
        return self._silhouette_property

    @property
    def visible(self):
        return self._actor.GetVisibility()

    @property
    def property(self):
        return self._property

    def setVisible(self, visible):
        if visible:
            self._actor.VisibilityOn()
        else:
            self._actor.VisibilityOff()

    def setSilhouetteVisible(self, visible):
        if visible:
            self._silhouette_actor.VisibilityOn()
        else:
            self._silhouette_actor.VisibilityOff()

    def _computeBounds(self, data_object):
        glob_min = QtGui.QVector3D(float('inf'), float('inf'), float('inf'))
        glob_max = QtGui.QVector3D(float('-inf'), float('-inf'), float('-inf'))
        for i in range(data_object.GetNumberOfBlocks()):
            current = data_object.GetBlock(i)
            if isinstance(current, vtk.vtkUnstructuredGrid):
                bnd = current.GetBounds()
                bnd_min = QtGui.QVector3D(bnd[0], bnd[2], bnd[4])
                bnd_max = QtGui.QVector3D(bnd[1], bnd[3], bnd[5])
                glob_min = common.point_min(bnd_min, glob_min)
                glob_max = common.point_max(bnd_max, glob_max)

            elif isinstance(current, vtk.vtkMultiBlockDataSet):
                for j in range(current.GetNumberOfBlocks()):
                    bnd = current.GetBlock(j).GetBounds()
                    bnd_min = QtGui.QVector3D(bnd[0], bnd[2], bnd[4])
                    bnd_max = QtGui.QVector3D(bnd[1], bnd[3], bnd[5])
                    glob_min = common.point_min(bnd_min, glob_min)
                    glob_max = common.point_max(bnd_max, glob_max)

        return (glob_min, glob_max)

    # def add(self, vtk_renderer):
    #     vtk_renderer.AddViewProp(self._actor)
    #     vtk_renderer.AddViewProp(self._silhouette_actor)
