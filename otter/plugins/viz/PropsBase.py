from PyQt5.QtWidgets import QVBoxLayout, QDialog
from PyQt5.QtCore import Qt, QPoint


class PropsBase(QDialog):
    """
    Base class for properties pages
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._vtk_renderer = parent.getVtkRenderer()
        self._vtk_interactor = parent.getVtkInteractor()
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

    def show(self):
        render_wnd = self.parentWidget()
        geom = render_wnd._params_window.geometry()
        pt = QPoint(geom.right() + 8, geom.top() + 1)
        pt = render_wnd.mapToGlobal(pt)
        self.move(pt.x(), pt.y())
        super().show()
