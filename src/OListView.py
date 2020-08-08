from PyQt5 import QtWidgets, QtGui, QtCore

class OItemDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent):
        super(OItemDelegate, self).__init__(parent)
        self._list_view = parent

    def paint(self, painter, option, index):
        super(OItemDelegate, self).paint(painter, option, index)

    def sizeHint(self, option, index):
        return QtCore.QSize(400, 50)

class OListView(QtWidgets.QListView):

    def __init__(self, parent):
        super(OListView, self).__init__(parent)
        self.empty_message = "No items"
        self.setIconSize(QtCore.QSize(32, 32))
        self.setItemDelegate(OItemDelegate(self))

    def setEmptyMessage(self, msg):
        self.empty_message = msg

    def paintEvent(self, e):
        super(OListView, self).paintEvent(e)

        if self.model() and self.model().rowCount(self.rootIndex()) > 0:
            return

        # The view is empty
        p = QtGui.QPainter(self.viewport())
        rect = self.rect()
        rect.adjust(0, 10, 0, 0)
        p.drawText(rect, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop, self.empty_message)
