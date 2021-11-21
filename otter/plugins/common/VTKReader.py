import vtk
import otter.plugins.common as common
from otter.plugins.common.Reader import Reader
from otter.plugins.common.Reader import BlockInformation, VariableInformation


class VTKReader(Reader):
    """
    VTK file reader
    """

    def __init__(self, file_name):
        super().__init__(file_name)
        self._reader = None
        self._block_info = dict()
        self._variable_info = dict()

    def isValid(self):
        if self._reader.IsFileUnstructuredGrid():
            return True
        else:
            return False

    def load(self):
        self._reader = vtk.vtkUnstructuredGridReader()

        with common.lock_file(self._file_name):
            self._reader.SetFileName(self._file_name)
            self._reader.ReadAllScalarsOn()
            self._reader.Update()

        self._readBlockInfo()
        self._readVariableInfo()

    def _readBlockInfo(self):
        vtkid = 0
        binfo = BlockInformation(object_type=0,
                                 name="block",
                                 number=vtkid,
                                 object_index=0,
                                 multiblock_index=None)
        self._block_info[vtkid] = binfo

    def _readVariableInfo(self):
        var_type = vtk.vtkExodusIIReader.NODAL
        for i in range(self._reader.GetNumberOfScalarsInFile()):
            var_name = self._reader.GetScalarsNameInFile(i)
            vinfo = VariableInformation(name=var_name,
                                        object_type=var_type,
                                        num_components=1)
            self._variable_info[var_name] = vinfo

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
        return self._reader.GetOutput().GetNumberOfCells()

    def getTotalNumberOfNodes(self):
        return self._reader.GetOutput().GetNumberOfPoints()
