import math
import vtk
from .Component import Component


class HeatStructure(Component):
    """
    Component that represents a heat structure
    """

    SIZE = 0.04
    COLOR = [0.6, 0.6, 0.6]

    def __init__(self, reader, name, params):
        super(HeatStructure, self).__init__(reader, name, params)

        self._source = None

        position = self.toArray(params['position'])
        if 'offset' in params:
            position[0] += params['offset'][0]
            position[1] += params['offset'][1]
            position[2] += params['offset'][2]
        orientation = self.toArray(params['orientation'])
        if 'rotation' in params:
            self._rotation = float(params['rotation'])
        else:
            self._rotation = 0.

        length = float(params['length'])
        if 'widths' in params:
            width = sum(self.toArray(params['widths']))
        else:
            width = params['width']
        self._depth = HeatStructure.SIZE

        self._bounds = [
            0, length,
            -width, 0,
            -0.5 * HeatStructure.SIZE, 0.5 * HeatStructure.SIZE
        ]
        self._position = [position[0], position[1], position[2]]

        # rotate according to orientation vector
        r = math.sqrt(math.pow(orientation[0], 2) +
                      math.pow(orientation[1], 2) +
                      math.pow(orientation[2], 2))
        theta = math.acos(orientation[2] / r)
        aphi = math.atan2(orientation[1], orientation[0])
        self._orientation = [
            0,
            (theta * 180. / math.pi) - 90,
            (aphi * 180. / math.pi)
        ]

    @property
    def type(self):
        return "HeatStructure"

    def create(self):
        """
        Creates the CubeSource object representing a heat structure.
        """
        source = vtk.vtkCubeSource()
        source.SetBounds(self._bounds)

        self._mapper = vtk.vtkPolyDataMapper()
        self._mapper.SetInputConnection(source.GetOutputPort())

        self._actor = vtk.vtkActor()
        self._actor.SetMapper(self._mapper)
        self._actor.SetPosition(self._position)
        self._actor.SetOrientation(self._orientation)
        self._actor.RotateX(self._rotation)
        self._actor.RotateY(0)
        self._actor.RotateZ(0)

        self._silhouette = vtk.vtkPolyDataSilhouette()
        self._silhouette.SetInputData(self._mapper.GetInput())

        self._silhouette_mapper = vtk.vtkPolyDataMapper()
        self._silhouette_mapper.SetInputConnection(
            self._silhouette.GetOutputPort())

        self._silhouette_actor = vtk.vtkActor()
        self._silhouette_actor.SetMapper(self._silhouette_mapper)
        self._silhouette_actor.SetPosition(self._position)
        self._silhouette_actor.SetOrientation(self._orientation)
        self._silhouette_actor.RotateX(self._rotation)
        self._silhouette_actor.RotateY(0)
        self._silhouette_actor.RotateZ(0)

        self._caption_actor = self._createCaptionActor()
        center = self._actor.GetCenter()
        self._caption_actor.SetAttachmentPoint(center)

    def getActor(self):
        return self._actor

    def getSilhouetteActor(self):
        return self._silhouette_actor

    def setSilhouetteCamera(self, camera):
        self._silhouette.SetCamera(camera)
