from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint


class PropsBase(QWidget):
    """
    Base class for properties pages
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._actor = None

        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(6, 6, 6, 6)
        self._layout.setSpacing(2)
        self.setLayout(self._layout)

        self.setWindowFlag(Qt.Tool)
        self.setWindowFlag(Qt.CustomizeWindowHint)
        self.setWindowFlag(Qt.WindowMinMaxButtonsHint, False)
        self.setWindowFlag(Qt.WindowFullscreenButtonHint, False)

    def buildVtkActor(self):
        return self._actor

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def show(self):
        render_wnd = self.parentWidget()
        geom = render_wnd.geometry()
        pt = QPoint(geom.left() + 1, geom.top() + 1)
        pt = render_wnd.mapToGlobal(pt)
        # TODO factor in the toolbar heigh programatically
        self.move(pt.x(), pt.y() + 32)
        super().show()
