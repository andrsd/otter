from PyQt5 import QtWidgets, QtGui, QtCore

class OItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    List view item delegate
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._list_view = parent

    def paint(self, painter, option, index):
        """
        Paint
        """
        super().paint(painter, option, index)

    def sizeHint(self, unused_option, unused_index):
        """
        Size hint
        """
        return QtCore.QSize(400, 50)

class OListView(QtWidgets.QListView):
    """
    List view class that show an message when empty (i.e. has no items)
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.empty_message = "No items"
        self.setIconSize(QtCore.QSize(32, 32))
        self.setItemDelegate(OItemDelegate(self))

    def setEmptyMessage(self, msg):
        """
        Set the message displayed when no items in the widget
        @param msg[str] Message to show
        """
        self.empty_message = msg

    def paintEvent(self, event):
        """
        Paint event
        """
        super().paintEvent(event)

        if self.model() and self.model().rowCount(self.rootIndex()) > 0:
            return

        # The view is empty
        painter = QtGui.QPainter(self.viewport())
        rect = self.rect()
        rect.adjust(0, 10, 0, 0)
        painter.drawText(rect, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop, self.empty_message)
