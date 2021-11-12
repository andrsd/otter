import vtk
import collections
import otter.plugins.common as common


BlockInformation = collections.namedtuple(
    'BlockInformation', [
        'name', 'object_type', 'object_index', 'number', 'multiblock_index'
    ])


class ExodusIIReader:
    """
    ExodusII file reader
    """

    def __init__(self, file_name):
        self._file_name = file_name
        self._reader = None
        # BlockInformation objects
        self._block_info = dict()

    def load(self):
        self._reader = vtk.vtkExodusIIReader()

        with common.lock_file(self._file_name):
            self._reader.SetFileName(self._file_name)
            self._reader.UpdateInformation()
            self._reader.Update()

            self._readBlockInfo()
            for obj_type, data in self._block_info.items():
                for info in data.values():
                    self._reader.SetObjectStatus(
                        info.object_type, info.object_index, 1)

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

    def getReader(self):
        return self._reader

    def getVtkOutputPort(self):
        return self._reader.GetOutputPort(0)

    def getBlocks(self):
        return self._block_info[vtk.vtkExodusIIReader.ELEM_BLOCK].values()

    def getSideSets(self):
        return self._block_info[vtk.vtkExodusIIReader.SIDE_SET].values()

    def getNodeSets(self):
        return self._block_info[vtk.vtkExodusIIReader.NODE_SET].values()

    def getFileName(self):
        return self._file_name
