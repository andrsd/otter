from PyQt5 import QtWidgets, QtGui
from gui.OtterParams import *

class OtterParameterModel(QtGui.QStandardItemModel):

    def __init__(self, rows, cols, parent):
        super(OtterParameterModel, self).__init__(rows, cols, parent)

    def canDropMimeData(self, data, action, row, column, parent):
        if not data.hasFormat('text/uri-list') and not data.hasFormat('application/x-color'):
            return False

        index = self.index(row, column, parent)
        item = self.itemFromIndex(index)
        if item != None:
            if isinstance(item.data(), OtterParamFilePicker):
                otter_param = item.data()
                if otter_param.load_save() == 'open':
                    return True
            elif isinstance(item.data(), OtterParamColorPicker):
                return True

        return False


class OtterParameterView(QtWidgets.QTreeView):

    def __init__(self, parent):
        super(OtterParameterView, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dragEnterEvent(self, event):
        md = event.mimeData()
        if md.hasUrls() or md.hasColor():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            file_name = mime_data.urls()[0].toLocalFile()
            index = self.indexAt(event.pos())
            item = self.model().itemFromIndex(index)
            item.setText(file_name)
        elif mime_data.hasColor():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()

            index = self.indexAt(event.pos())
            item = self.model().itemFromIndex(index)

            qclr = mime_data.colorData()
            s = "[{:.2}, {:.2}, {:.2}]".format(qclr.redF(), qclr.greenF(), qclr.blueF())
            item.setText(s)
        else:
            event.ignore()
