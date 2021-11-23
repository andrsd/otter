from PyQt5 import QtWidgets, QtGui, QtCore


class OItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    List view item delegate
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._tree_view = parent

    def paint(self, painter, option, index):
        """
        Paint
        """
        super().paint(painter, option, index)


class OTreeView(QtWidgets.QTreeView):
    """
    Tree view class that show an message when empty (i.e. has no items)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.empty_message = "No items"
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

        fnt = self.font()
        fnt.setPointSizeF(fnt.pointSizeF() * 0.9)
        # The view is empty
        painter = QtGui.QPainter(self.viewport())
        painter.setFont(fnt)
        rect = self.rect()
        rect.adjust(0, 10, 0, 0)
        painter.drawText(rect,
                         int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop),
                         self.empty_message)
