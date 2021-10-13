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
        self._connection = self.parseConnection(params['input'])

    @property
    def type(self):
        return "Boundary"

    def create(self):
        comp = self._reader.getComponent(self._connection['name'])

        pos = comp.getPoint(self._connection['type'])
        ori = comp.getOrientation(self._connection['type'])
        if self._connection['type'] == 'in':
            center = [pos[0] - ori[0] * 0.5 * Boundary.SIZE,
                      pos[1] - ori[1] * 0.5 * Boundary.SIZE,
                      pos[2] - ori[2] * 0.5 * Boundary.SIZE]
        elif self._connection['type'] == 'out':
            center = [pos[0] + ori[0] * 0.5 * Boundary.SIZE,
                      pos[1] + ori[1] * 0.5 * Boundary.SIZE,
                      pos[2] + ori[2] * 0.5 * Boundary.SIZE]
        else:
            center = pos

        source = vtk.vtkCubeSource()
        source.SetCenter(center)
        source.SetXLength(Boundary.SIZE)
        source.SetYLength(Boundary.SIZE)
        source.SetZLength(Boundary.SIZE)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())

        self._actor = vtk.vtkActor()
        self._actor.SetMapper(mapper)

        property = self._actor.GetProperty()
        property.SetColor(Boundary.COLOR)
        property.SetEdgeVisibility(False)
