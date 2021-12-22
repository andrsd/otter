import vtk


class Selection(object):
    """
    Handles selection of entities like cells and points
    """

    def __init__(self, data):
        """
        @param data vtkDataObject that will be "filtered" to extract the
                    selection
        """
        self._extract_selection = vtk.vtkExtractSelection()
        self._extract_selection.SetInputData(0, data)

        self._selected = vtk.vtkUnstructuredGrid()

        self._mapper = vtk.vtkDataSetMapper()
        self._mapper.SetInputData(self._selected)

        self._actor = vtk.vtkActor()
        self._actor.SetMapper(self._mapper)

    def getActor(self):
        return self._actor

    def clear(self):
        self._selected.Initialize()
        self._mapper.SetInputData(self._selected)

    def selectCell(self, cell_id):
        ids = vtk.vtkIdTypeArray()
        ids.SetNumberOfComponents(1)
        ids.InsertNextValue(cell_id)

        selection_node = vtk.vtkSelectionNode()
        selection_node.SetFieldType(vtk.vtkSelectionNode.CELL)
        selection_node.SetContentType(vtk.vtkSelectionNode.INDICES)
        selection_node.SetSelectionList(ids)

        self._setSelection(selection_node)

    def selectPoint(self, point_id):
        ids = vtk.vtkIdTypeArray()
        ids.SetNumberOfComponents(1)
        ids.InsertNextValue(point_id)

        selection_node = vtk.vtkSelectionNode()
        selection_node.SetFieldType(vtk.vtkSelectionNode.POINT)
        selection_node.SetContentType(vtk.vtkSelectionNode.INDICES)
        selection_node.SetSelectionList(ids)

        self._setSelection(selection_node)

    def _setSelection(self, selection_node):
        self._selection = vtk.vtkSelection()
        self._selection.AddNode(selection_node)

        self._extract_selection.SetInputData(1, self._selection)
        self._extract_selection.Update()

        self._selected = vtk.vtkUnstructuredGrid()
        self._selected.ShallowCopy(self._extract_selection.GetOutput())

        self._mapper.SetInputData(self._selected)
