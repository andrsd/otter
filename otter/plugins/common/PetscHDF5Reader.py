import vtk
import h5py
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
import otter.plugins.common as common
from otter.plugins.common.Reader import Reader
from otter.plugins.common.Reader import BlockInformation, VariableInformation


class PetscHDF5DataSetReader(VTKPythonAlgorithmBase):
    """
    Reader for datasets produced by PETSc
    """

    def __init__(self):
        VTKPythonAlgorithmBase.__init__(
            self,
            nInputPorts=0,
            nOutputPorts=1,
            outputType='vtkMultiBlockDataSet')

        self._file_name = ""
        self._output = None

    def RequestData(self, request, in_info, out_info):
        self._output = vtk.vtkMultiBlockDataSet.GetData(out_info)

        f = h5py.File(self._file_name, 'r')

        block = vtk.vtkUnstructuredGrid()

        points = f['geometry']['vertices']
        n_points = points.shape[0]
        dim = points.shape[1]

        point_array = vtk.vtkPoints()
        point_array.Allocate(n_points)
        for i in range(n_points):
            pt = [0, 0, 0]
            for j in range(dim):
                pt[j] = points[i][j]
            point_array.InsertPoint(i, pt)
        block.SetPoints(point_array)

        cells = f['viz']['topology']['cells']
        n_cell_corners = cells.attrs['cell_corners']
        cell_dim = cells.attrs['cell_dim']

        if cell_dim == 1:
            if n_cell_corners == 2:
                cell_array = self._buildCells(cells, "vtkLine", 2)
                block.SetCells(vtk.VTK_LINE, cell_array)
        elif cell_dim == 2:
            if n_cell_corners == 3:
                cell_array = self._buildCells(cells, "vtkTriangle", 3)
                block.SetCells(vtk.VTK_TRIANGLE, cell_array)
            elif n_cell_corners == 4:
                cell_array = self._buildCells(cells, "vtkQuad", 4)
                block.SetCells(vtk.VTK_QUAD, cell_array)
        elif cell_dim == 3:
            if n_cell_corners == 4:
                cell_array = self._buildCells(cells, "vtkTetra", 4)
                block.SetCells(vtk.VTK_TETRA, cell_array)
            elif n_cell_corners == 6:
                cell_array = self._buildCells(cells, "vtkWedge", 6)
                block.SetCells(vtk.VTK_WEDGE, cell_array)
            elif n_cell_corners == 8:
                cell_array = self._buildCells(cells, "vtkHexahedron", 8)
                block.SetCells(vtk.VTK_HEXAHEDRON, cell_array)

        if 'vertex_fields' in f:
            self._readVertexFields(block, f['vertex_fields'])
        if 'cell_fields' in f:
            self._readCellFields(block, f['cell_fields'])

        self._output.SetBlock(0, block)

        return 1

    def _buildCells(self, cells, class_name, n_vertices):
        n_cells = cells.shape[0]
        cell_array = vtk.vtkCellArray()
        cell_array.Allocate(n_cells)
        for i in range(n_cells):
            connectivity = cells[i]
            ctor = getattr(vtk, class_name)
            elem = ctor()
            for j in range(n_vertices):
                elem.GetPointIds().SetId(j, connectivity[j])
            cell_array.InsertNextCell(elem)
        return cell_array

    def _readVertexFields(self, block, vertex_fields):
        point_data = block.GetPointData()

        for (fname, ds) in vertex_fields.items():
            if ds.attrs['vector_field_type'] == b'scalar':
                arr = vtk.vtkDataArray.CreateDataArray(vtk.VTK_DOUBLE)
                arr.SetName(fname)
                arr.Allocate(ds.shape[0])
                for val in list(ds):
                    arr.InsertNextTuple1(val)
                point_data.AddArray(arr)

    def _readCellFields(self, block, cell_fields):
        cell_data = block.GetCellData()

        for (fname, ds) in cell_fields.items():
            if ds.attrs['vector_field_type'] == b'scalar':
                arr = vtk.vtkDataArray.CreateDataArray(vtk.VTK_DOUBLE)
                arr.SetName(fname)
                arr.Allocate(ds.shape[0])
                for val in list(ds):
                    arr.InsertNextTuple1(val)
                cell_data.AddArray(arr)

    def SetFileName(self, fname):
        if fname != self._file_name:
            self.Modified()
            self._file_name = fname

    def GetFileName(self):
        return self._file_name

    def GetTotalNumberOfElements(self):
        return self._output.GetNumberOfCells()

    def GetTotalNumberOfNodes(self):
        return self._output.GetNumberOfPoints()


class PetscHDF5Reader(Reader):
    """
    PETSc HDF5 file reader
    """

    def __init__(self, file_name):
        super().__init__(file_name)
        self._reader = None
        self._block_info = dict()
        self._variable_info = dict()

    def isValid(self):
        # TODO: check that the file was created by PETSc
        return True

    def load(self):
        self._reader = PetscHDF5DataSetReader()

        with common.lock_file(self._file_name):
            self._reader.SetFileName(self._file_name)
            self._reader.Update()

        self._readBlockInfo()
        self._readVariableInfo()

    def _readBlockInfo(self):
        vtkid = 0
        binfo = BlockInformation(object_type=0,
                                 name="block",
                                 number=vtkid,
                                 object_index=0,
                                 multiblock_index=1)
        self._block_info[vtkid] = binfo

    def _readVariableInfo(self):
        # TODO
        vinfo = VariableInformation(name="sln_u",
                                    object_type=Reader.VAR_NODAL,
                                    num_components=1)
        self._variable_info["sln_u"] = vinfo

    def getVtkOutputPort(self):
        return self._reader.GetOutputPort(0)

    def getBlocks(self):
        return self._block_info.values()

    def getSideSets(self):
        return []

    def getNodeSets(self):
        return []

    def getVariableInfo(self):
        return self._variable_info.values()

    def getTotalNumberOfElements(self):
        return self._reader.GetTotalNumberOfElements()

    def getTotalNumberOfNodes(self):
        return self._reader.GetTotalNumberOfNodes()
