import collections


BlockInformation = collections.namedtuple(
    'BlockInformation', [
        'name', 'object_type', 'object_index', 'number', 'multiblock_index'
    ])

VariableInformation = collections.namedtuple(
    'VariableInformation', [
        'name', 'object_type', 'num_components'
    ])


class Reader:
    """
    Base class for readers
    """

    def __init__(self, file_name):
        self._file_name = file_name

    def load(self):
        pass

    def getVtkOutputPort(self):
        return None

    def getBlocks(self):
        return None

    def getSideSets(self):
        return None

    def getNodeSets(self):
        return None

    def getFileName(self):
        return self._file_name

    def getVariableInfo(self):
        return None

    def getTotalNumberOfElements(self):
        return None

    def getTotalNumberOfNodes(self):
        return None
