from PyQt5 import QtWidgets, QtGui, QtCore

class OListView(QtWidgets.QListView):

    def __init__(self, parent):
        super(OListView, self).__init__(parent)
        self.EmptyMessage = "No items"

    def setEmptyMessage(self, msg):
        self.EmptyMessage = msg

    def paintEvent(self, e):
        super(OListView, self).paintEvent(e)

        if self.model() and self.model().rowCount(self.rootIndex()) > 0:
            return

        # The view is empty
        p = QtGui.QPainter(self.viewport())
        rect = self.rect()
        rect.adjust(0, 10, 0, 0)
        p.drawText(rect, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop, self.EmptyMessage)
