from PyQt5 import QtWidgets, QtGui
from gui.OtterParams import *

class OtterParameterModel(QtGui.QStandardItemModel):

    def __init__(self, rows, cols, parent):
        super(OtterParameterModel, self).__init__(rows, cols, parent)

    def canDropMimeData(self, data, action, row, column, parent):
        if not data.hasFormat('text/uri-list'):
            return False

        index = self.index(row, column, parent)
        item = self.itemFromIndex(index)
        if item != None:
            if isinstance(item.data(), OtterParamFilePicker):
                otter_param = item.data()
                if otter_param.load_save() == 'open':
                    return True
        return False


class OtterParameterView(QtWidgets.QTreeView):

    def __init__(self, parent):
        super(OtterParameterView, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dragEnterEvent(self, event):
        md = event.mimeData()
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            file_name = event.mimeData().urls()[0].toLocalFile()
            index = self.indexAt(event.pos())
            item = self.model().itemFromIndex(index)
            item.setText(file_name)
        else:
            event.ignore()
