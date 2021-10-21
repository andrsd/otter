import math
import vtk
from .Component import Component


class FlowChannel(Component):
    """
    Component that represents a 1D flow channel
    """

    RADIUS = 0.02
    RESOLUTION = 15
    COLOR = [0.7, 0.7, 0.7]

    def __init__(self, reader, name, params):
        super().__init__(reader, name, params)
        self._mapper = None
        self._actor = None
        self._silhouette_actor = None

        self._source = None
        position = self.toArray(params['position'])

        ori = self.toArray(params['orientation'])
        r = math.sqrt(math.pow(ori[0], 2) +
                      math.pow(ori[1], 2) +
                      math.pow(ori[2], 2))

        # normalized orientation vector
        self._ori = [ori[0] / r, ori[1] / r, ori[2] / r]

        self._length = float(params['length'])
        if 'offset' in params:
            position[0] += params['offset'][0]
            position[1] += params['offset'][1]
            position[2] += params['offset'][2]

        # orientation for VTK (3 angles - rotation about x, y, z axes)
        theta = math.acos(ori[2] / r)
        aphi = math.atan2(ori[1], ori[0])
        self._vtk_orientation = [
            90 + (theta * 180. / math.pi),
            0,
            90 + (aphi * 180. / math.pi)
        ]

        self._start_point = [position[0], position[1], position[2]]
        self._end_point = [position[0] + self._ori[0] * self._length,
                           position[1] + self._ori[1] * self._length,
                           position[2] + self._ori[2] * self._length]
        self._position = [(self._start_point[0] + self._end_point[0]) / 2,
                          (self._start_point[1] + self._end_point[1]) / 2,
                          (self._start_point[2] + self._end_point[2]) / 2]

    @property
    def type(self):
        return "FlowChannel"

    def create(self):
        source = vtk.vtkCubeSource()
        source.SetXLength(1.5 * FlowChannel.RADIUS)
        source.SetYLength(self._length)
        source.SetZLength(1.5 * FlowChannel.RADIUS)

        self._mapper = vtk.vtkPolyDataMapper()
        self._mapper.SetInputConnection(source.GetOutputPort())

        self._actor = vtk.vtkActor()
        self._actor.SetMapper(self._mapper)
        self._actor.SetPosition(self._position)
        self._actor.SetOrientation(self._vtk_orientation)

        self._silhouette = vtk.vtkPolyDataSilhouette()
        self._silhouette.SetInputData(self._mapper.GetInput())

        self._silhouette_mapper = vtk.vtkPolyDataMapper()
        self._silhouette_mapper.SetInputConnection(
            self._silhouette.GetOutputPort())

        self._silhouette_actor = vtk.vtkActor()
        self._silhouette_actor.SetMapper(self._silhouette_mapper)
        self._silhouette_actor.SetPosition(self._position)
        self._silhouette_actor.SetOrientation(self._vtk_orientation)

        self._caption_actor = self._createCaptionActor()
        self._caption_actor.SetAttachmentPoint(self._position)

    def getActor(self):
        return self._actor

    def getSilhouetteActor(self):
        return self._silhouette_actor

    def setSilhouetteCamera(self, camera):
        self._silhouette.SetCamera(camera)

    def getPoint(self, ptype):
        """
        Return the flow channel input or output points.

        Args:
            ptype[str]: Must be "in" or "out", representing the type of point
                        to return
        """
        if ptype == 'in':
            return self._start_point
        elif ptype == 'out':
            return self._end_point
        else:
            return None

    def getOrientation(self, *args):
        return self._ori
