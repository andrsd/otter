from PyQt5 import QtWidgets


class PropsBase(QtWidgets.QWidget):
    """
    Base class for properties pages
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._actor = None

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

        self._title = QtWidgets.QLabel("Properties")
        font = self._title.font()
        font.setBold(True)
        self._title.setFont(font)
        self._layout.addWidget(self._title)

    def setFocus(self):
        pass

    def buildVtkActor(self):
        return self._actor
