from PyQt5 import QtWidgets, QtCore


class ClickableLabel(QtWidgets.QLabel):

    clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def enterEvent(self, event):
        f = self.font()
        f.setUnderline(True)
        self.setFont(f)

    def leaveEvent(self, event):
        f = self.font()
        f.setUnderline(False)
        self.setFont(f)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()
