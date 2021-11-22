from PyQt5 import QtWidgets, QtGui


class ColorButton(QtWidgets.QPushButton):
    """
    Button that dsiplays a rectangle with a color
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlat(True)
        self.setFixedHeight(25)
        self.setFixedWidth(45)
        self.setStyleSheet("""
            border: 1px solid #888;
            background-color: #eee;
            """)
        self._qcolor = QtGui.QColor("#eee")

    def setColor(self, qcolor):
        self._qcolor = qcolor
        self.repaint()

    def color(self):
        return self._qcolor

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self._qcolor)))
        painter.setPen(QtGui.QPen(QtGui.QColor("#000")))
        rect = self.rect()
        rect.adjust(4, 4, -4, -4)
        painter.drawRect(rect)
