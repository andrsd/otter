from PyQt5 import QtCore


class LoadFileEvent(QtCore.QEvent):
    """
    Custom event to load files. Usually used when we need to open file
    specified on a command line
    """

    TYPE = QtCore.QEvent.registerEventType()

    def __init__(self, file_name):
        super().__init__(self.TYPE)
        self.file_name = file_name

    def fileName(self):
        return self.file_name
