import vtk


class SideSetObject:
    """
    Object that encapualates VTK around a side set
    """

    def __init__(self, eb):
        do = eb.GetOutput()
        self._info = {
            'cells': do.GetNumberOfCells(),
            'points': do.GetNumberOfPoints()
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
        self._actor.VisibilityOff()

        self._property = self._actor.GetProperty()
        self._property.SetRepresentationToSurface()

    @property
    def actor(self):
        return self._actor

    @property
    def info(self):
        return self._info

    @property
    def property(self):
        return self._property

    def setVisible(self, visible):
        if visible:
            self._actor.VisibilityOn()
        else:
            self._actor.VisibilityOff()
