import vtk
import h5py
import numpy as np
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
        self._cell_dim = None
        self._labels = {}
        self._graph = {}
        self._multi_idx = 0
        self._cell_connectivity = None
        self._block_info = None
        self._sideset_info = None

    def RequestData(self, request, in_info, out_info):
        self._block_info = {}
        self._sideset_info = {}

        self._output = vtk.vtkMultiBlockDataSet.GetData(out_info)
        self._readFile()

        self._block_idx = 0
        self._multi_idx = 0
        self._buildBlocks()
        self._buildFaceSets()

        return 1

    def _readFile(self):
        f = h5py.File(self._file_name, 'r')

        self._labels = {}
        self._vertices = f['geometry']['vertices']

        cells = np.reshape(f['topology']['cells'], -1)
        cones = np.reshape(f['topology']['cones'], -1)
        self._graph = {}
        i = 0
        j = 0
        for c in cones:
            lst = []
            for k in range(c):
                lst.append(cells[i])
                i += 1
            self._graph[j] = lst
            j += 1

        self._orientation = np.reshape(f['topology']['orientation'], -1)
        labels = f['labels']

        if 'celltype' in labels:
            celltypes = labels['celltype']
            self._cell_types = {}
            self._dim_of_cell = {}
            for ct in celltypes.keys():
                indices = np.reshape(celltypes[ct]['indices'], -1)
                for i in indices:
                    self._dim_of_cell[i] = ct
                self._cell_types[int(ct)] = indices

            self._vertex_idx = {}
            for i, val in enumerate(self._cell_types[0]):
                self._vertex_idx[val] = i

        if 'Face Sets' in labels:
            face_sets = labels['Face Sets']
            self._labels['face_sets'] = {}
            for fs in face_sets.keys():
                indices = face_sets[fs]['indices']
                self._labels['face_sets'][fs] = indices

        if 'vertex_fields' in f:
            self._vertex_fields = f['vertex_fields']
        else:
            self._vertex_fields = {}
        if 'cell_fields' in f:
            self._cell_fields = f['cell_fields']
        else:
            self._cell_fields = {}

        self._cell_connectivity = f['viz']['topology']['cells']

    def _buildBlocks(self):
        block = vtk.vtkUnstructuredGrid()

        dim = self._vertices.shape[1]
        verts = self._cell_types[0]
        n_points = len(verts)
        point_array = vtk.vtkPoints()
        point_array.Allocate(n_points)
        for i in range(n_points):
            pt = [0, 0, 0]
            for j in range(dim):
                pt[j] = self._vertices[i][j]
            point_array.InsertPoint(i, pt)
        block.SetPoints(point_array)

        # FIXME: build this from cells and cones
        n_cell_corners = self._cell_connectivity.attrs['cell_corners']
        self._cell_dim = self._cell_connectivity.attrs['cell_dim']

        c_conn = self._cell_connectivity
        if self._cell_dim == 1:
            if n_cell_corners == 2:
                cell_array = self._buildCells(c_conn, "vtkLine", 2)
                block.SetCells(vtk.VTK_LINE, cell_array)
        elif self._cell_dim == 2:
            if n_cell_corners == 3:
                cell_array = self._buildCells(c_conn, "vtkTriangle", 3)
                block.SetCells(vtk.VTK_TRIANGLE, cell_array)
            elif n_cell_corners == 4:
                cell_array = self._buildCells(c_conn, "vtkQuad", 4)
                block.SetCells(vtk.VTK_QUAD, cell_array)
        elif self._cell_dim == 3:
            if n_cell_corners == 4:
                cell_array = self._buildCells(c_conn, "vtkTetra", 4)
                block.SetCells(vtk.VTK_TETRA, cell_array)
            elif n_cell_corners == 6:
                cell_array = self._buildCells(c_conn, "vtkWedge", 6)
                block.SetCells(vtk.VTK_WEDGE, cell_array)
            elif n_cell_corners == 8:
                cell_array = self._buildCells(c_conn, "vtkHexahedron", 8)
                block.SetCells(vtk.VTK_HEXAHEDRON, cell_array)

        self._readVertexFields(block, self._vertex_fields)
        self._readCellFields(block, self._cell_fields)

        self._output.SetBlock(self._block_idx, block)
        self._block_idx += 1
        binfo = BlockInformation(object_type=0,
                                 name="block",
                                 number=self._multi_idx,
                                 object_index=0,
                                 multiblock_index=self._multi_idx)
        self._block_info[0] = binfo

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

    def _buildFaceSets(self):
        self._multi_idx += 1
        j = 0
        for (id, fs) in self._labels['face_sets'].items():
            self._multi_idx += 1
            block = self._buildFaceSet(fs)
            self._output.SetBlock(self._block_idx, block)
            self._block_idx += 1
            binfo = BlockInformation(object_type=1,
                                     name=str(id),
                                     number=self._multi_idx,
                                     object_index=j,
                                     multiblock_index=self._multi_idx)
            self._sideset_info[id] = binfo
            j += 1

    def _buildFaceSet(self, face_set):
        dim = self._vertices.shape[1]

        if dim == 2:
            block = vtk.vtkUnstructuredGrid()

            edge_ids = np.reshape(face_set, -1)
            pt_ids = {}
            for eid in edge_ids:
                node_ids = self._graph[eid]
                for nid in node_ids:
                    pt_ids[nid] = 1

            point_array = vtk.vtkPoints()
            point_array.Allocate(len(pt_ids))
            for i in pt_ids:
                vert_idx = self._vertex_idx[i]
                pt = [0, 0, 0]
                for j in range(dim):
                    pt[j] = self._vertices[vert_idx][j]
                point_array.InsertPoint(i, pt)
            block.SetPoints(point_array)

            cell_array = vtk.vtkCellArray()
            for eid in edge_ids:
                node_ids = self._graph[eid]
                elem = vtk.vtkLine()
                elem.GetPointIds().SetId(0, node_ids[0])
                elem.GetPointIds().SetId(1, node_ids[1])
                cell_array.InsertNextCell(elem)
            block.SetCells(vtk.VTK_LINE, cell_array)

            return block
        elif dim == 3:
            block = vtk.vtkUnstructuredGrid()

            face_ids = np.reshape(face_set, -1)

            pt_ids = {}
            for fid in face_ids:
                edge_ids = self._graph[fid]
                for eid in edge_ids:
                    node_ids = self._graph[eid]
                    for nid in node_ids:
                        pt_ids[nid] = 1
            point_array = vtk.vtkPoints()
            point_array.Allocate(len(pt_ids))
            for i in pt_ids:
                vert_idx = self._vertex_idx[i]
                pt = [0, 0, 0]
                for j in range(dim):
                    pt[j] = self._vertices[vert_idx][j]
                point_array.InsertPoint(i, pt)
            block.SetPoints(point_array)

            # this assumes all cells in the cell array are of the same type
            cell_array = vtk.vtkCellArray()
            for fid in face_ids:
                pt_idxs = []
                # this works, weirdly
                edge_ids = self._graph[fid]
                for eid in edge_ids:
                    node_ids = self._graph[eid]
                    if node_ids[0] not in pt_idxs:
                        pt_idxs.append(node_ids[0])
                    if node_ids[1] not in pt_idxs:
                        pt_idxs.append(node_ids[1])

                if len(pt_idxs) == 3:
                    elem = vtk.vtkTriangle()
                    for i in range(3):
                        elem.GetPointIds().SetId(i, pt_idxs[i])
                    cell_array.InsertNextCell(elem)
                    type = vtk.VTK_TRIANGLE
                elif len(pt_idxs) == 4:
                    elem = vtk.vtkQuad()
                    for i in range(4):
                        elem.GetPointIds().SetId(i, pt_idxs[i])
                    cell_array.InsertNextCell(elem)
                    type = vtk.VTK_QUAD

            block.SetCells(type, cell_array)

            return block
        else:
            return None

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

    def getBlockInfo(self):
        return self._block_info

    def getSideSetInfo(self):
        return self._sideset_info


class PetscHDF5Reader(Reader):
    """
    PETSc HDF5 file reader
    """

    def __init__(self, file_name):
        super().__init__(file_name)
        self._reader = None
        self._block_info = dict()
        self._sideset_info = dict()
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
        self._readSidesetInfo()
        self._readVariableInfo()

    def _readBlockInfo(self):
        self._block_info = self._reader.getBlockInfo()

    def _readSidesetInfo(self):
        self._sideset_info = self._reader.getSideSetInfo()

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
        return self._sideset_info.values()

    def getNodeSets(self):
        return []

    def getVariableInfo(self):
        return self._variable_info.values()

    def getTotalNumberOfElements(self):
        return self._reader.GetTotalNumberOfElements()

    def getTotalNumberOfNodes(self):
        return self._reader.GetTotalNumberOfNodes()
