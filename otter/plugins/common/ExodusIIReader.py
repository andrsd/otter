import vtk
import otter.plugins.common as common
from otter.plugins.common.Reader import Reader
from otter.plugins.common.Reader import BlockInformation, VariableInformation


class ExodusIIReader(Reader):
    """
    ExodusII file reader
    """

    def __init__(self, file_name):
        super().__init__(file_name)
        self._reader = None
        # BlockInformation objects
        self._block_info = dict()
        self._variable_info = dict()
        self._times = None

    def load(self):
        self._reader = vtk.vtkExodusIIReader()

        with common.lock_file(self._file_name):
            self._readTimeInfo()

            self._reader.SetFileName(self._file_name)
            if self._times is not None:
                self._reader.SetTimeStep(self._time_steps[-1])
            self._reader.UpdateInformation()
            self._reader.SetAllArrayStatus(vtk.vtkExodusIIReader.NODAL, 1)
            self._reader.SetAllArrayStatus(vtk.vtkExodusIIReader.ELEM_BLOCK, 1)
            self._reader.SetAllArrayStatus(vtk.vtkExodusIIReader.GLOBAL, 1)
            self._reader.Update()

            self._readBlockInfo()
            for obj_type, data in self._block_info.items():
                for info in data.values():
                    self._reader.SetObjectStatus(
                        info.object_type, info.object_index, 1)
            self._readVariableInfo()

    def _readBlockInfo(self):
        object_types = [
            vtk.vtkExodusIIReader.ELEM_BLOCK,
            vtk.vtkExodusIIReader.FACE_BLOCK,
            vtk.vtkExodusIIReader.EDGE_BLOCK,
            vtk.vtkExodusIIReader.ELEM_SET,
            vtk.vtkExodusIIReader.SIDE_SET,
            vtk.vtkExodusIIReader.FACE_SET,
            vtk.vtkExodusIIReader.EDGE_SET,
            vtk.vtkExodusIIReader.NODE_SET
        ]

        # Index to be used with the vtkExtractBlock::AddIndex method
        index = 0
        # Loop over all blocks of the vtk.MultiBlockDataSet
        for obj_type in object_types:
            index += 1
            self._block_info[obj_type] = dict()
            for j in range(self._reader.GetNumberOfObjects(obj_type)):
                index += 1
                name = self._reader.GetObjectName(obj_type, j)
                vtkid = self._reader.GetObjectId(obj_type, j)
                if name.startswith('Unnamed'):
                    name = str(vtkid)

                binfo = BlockInformation(object_type=obj_type,
                                         name=name,
                                         number=vtkid,
                                         object_index=j,
                                         multiblock_index=index)
                self._block_info[obj_type][vtkid] = binfo

    def _readVariableInfo(self):
        var_type = [
            vtk.vtkExodusIIReader.NODAL,
            vtk.vtkExodusIIReader.ELEM_BLOCK
        ]

        for variable_type in var_type:
            for i in range(self._reader.GetNumberOfObjectArrays(
                    variable_type)):
                var_name = self._reader.GetObjectArrayName(variable_type, i)
                if var_name is not None:
                    num = self._reader.GetNumberOfObjectArrayComponents(
                        variable_type, i)
                    vinfo = VariableInformation(name=var_name,
                                                object_type=variable_type,
                                                num_components=num)
                    self._variable_info[var_name] = vinfo

    def _readTimeInfo(self):
        self._reader.SetFileName(self._file_name)
        self._reader.Modified()
        self._reader.UpdateInformation()
        vtkinfo = self._reader.GetExecutive().GetOutputInformation(0)
        steps = range(self._reader.GetNumberOfTimeSteps())
        key = vtk.vtkStreamingDemandDrivenPipeline.TIME_STEPS()
        times = [vtkinfo.Get(key, i) for i in steps]

        if not times:
            self._times = None
            self._time_steps = None
        else:
            self._times = times
            self._time_steps = steps

    def getVtkOutputPort(self):
        return self._reader.GetOutputPort(0)

    def getBlocks(self):
        return self._block_info[vtk.vtkExodusIIReader.ELEM_BLOCK].values()

    def getSideSets(self):
        return self._block_info[vtk.vtkExodusIIReader.SIDE_SET].values()

    def getNodeSets(self):
        return self._block_info[vtk.vtkExodusIIReader.NODE_SET].values()

    def getVariableInfo(self):
        return self._variable_info.values()

    def getTotalNumberOfElements(self):
        return self._reader.GetTotalNumberOfElements()

    def getTotalNumberOfNodes(self):
        return self._reader.GetTotalNumberOfNodes()
