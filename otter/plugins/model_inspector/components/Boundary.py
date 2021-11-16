import vtk
from .Component import Component


class Boundary(Component):
    """
    Component that represents a boundary
    """

    SIZE = 0.04
    COLOR = [0.8, 0.8, 0.8]

    def __init__(self, reader, name, params):
        super().__init__(reader, name, params)
        self._center = None
        self._mapper = None
        self._actor = None
        self._silhouette_actor = None
        self._connection = self.parseConnection(params['input'])

    @property
    def type(self):
        return "Boundary"

    def create(self):
        comp = self._reader.getComponent(self._connection['name'])

        pos = comp.getPoint(self._connection['type'])
        ori = comp.getOrientation(self._connection['type'])
        if self._connection['type'] == 'in':
            self._center = [pos[0] - ori[0] * 0.5 * Boundary.SIZE,
                            pos[1] - ori[1] * 0.5 * Boundary.SIZE,
                            pos[2] - ori[2] * 0.5 * Boundary.SIZE]
        elif self._connection['type'] == 'out':
            self._center = [pos[0] + ori[0] * 0.5 * Boundary.SIZE,
                            pos[1] + ori[1] * 0.5 * Boundary.SIZE,
                            pos[2] + ori[2] * 0.5 * Boundary.SIZE]
        else:
            self._center = pos

        source = vtk.vtkCubeSource()
        source.SetCenter(self._center)
        source.SetXLength(Boundary.SIZE)
        source.SetYLength(Boundary.SIZE)
        source.SetZLength(Boundary.SIZE)

        self._mapper = vtk.vtkPolyDataMapper()
        self._mapper.SetInputConnection(source.GetOutputPort())

        self._actor = vtk.vtkActor()
        self._actor.SetMapper(self._mapper)

        self._silhouette = vtk.vtkPolyDataSilhouette()
        self._silhouette.SetInputData(self._mapper.GetInput())

        self._silhouette_mapper = vtk.vtkPolyDataMapper()
        self._silhouette_mapper.SetInputConnection(
            self._silhouette.GetOutputPort())

        self._silhouette_actor = vtk.vtkActor()
        self._silhouette_actor.SetMapper(self._silhouette_mapper)

        self._caption_actor = self._createCaptionActor()
        self._caption_actor.SetAttachmentPoint(self._center)

    def getActor(self):
        return self._actor

    def getSilhouetteActor(self):
        return self._silhouette_actor

    def setSilhouetteCamera(self, camera):
        self._silhouette.SetCamera(camera)

    def getPoint(self):
        return self._center
