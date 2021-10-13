import vtk
from .Component import Component


class Junction(Component):
    """
    Component that represents a junction
    """

    SIZE = 0.04
    COLOR = [0.6, 0.6, 0.6]

    def __init__(self, reader, name, params):
        super().__init__(reader, name, params)

        self._source = None
        self.__connections = []

        connections = params['connections'].split(" ")
        for c in connections:
            self.__connections.append(self.parseConnection(c))

    @property
    def type(self):
        return "Junction"

    def create(self):
        center = self.__computeCenter(self.__connections)
        bounds = self.__computeBounds(center)

        source = vtk.vtkCubeSource()
        source.SetCenter(center)
        source.SetBounds(bounds)

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

    def __computeCenter(self, connections):
        center = [0, 0, 0]
        n = len(connections)
        for conn in connections:
            comp = self._reader.getComponent(conn['name'])
            pt = comp.getPoint(conn['type'])
            center[0] += pt[0]
            center[1] += pt[1]
            center[2] += pt[2]
        center[0] /= n
        center[1] /= n
        center[2] /= n
        return center

    def __computeBounds(self, center):
        xmin = center[0] - Junction.SIZE
        xmax = center[0] + Junction.SIZE
        ymin = center[1] - Junction.SIZE
        ymax = center[1] + Junction.SIZE
        zmin = center[2] - Junction.SIZE
        zmax = center[2] + Junction.SIZE
        for conn in self.__connections:
            comp = self._reader.getComponent(conn['name'])
            pt = comp.getPoint(conn['type'])
            if pt[0] - Junction.SIZE < xmin:
                xmin = pt[0] - Junction.SIZE
            if pt[0] + Junction.SIZE > xmax:
                xmax = pt[0] + Junction.SIZE
            if pt[1] - Junction.SIZE < ymin:
                ymin = pt[1] - Junction.SIZE
            if pt[1] + Junction.SIZE > ymax:
                ymax = pt[1] + Junction.SIZE
            if pt[2] - Junction.SIZE < zmin:
                zmin = pt[2] - Junction.SIZE
            if pt[2] + Junction.SIZE > zmax:
                zmax = pt[2] + Junction.SIZE
        return [xmin, xmax, ymin, ymax, zmin, zmax]
