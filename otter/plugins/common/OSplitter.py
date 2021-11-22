from PyQt5 import QtWidgets, QtCore


class OSplitter(QtWidgets.QSplitter):

    COLLAPSE_BTN_SIZE = 32

    def __init__(self, orientation, parent=None):
        super().__init__(parent)
        self.setHandleWidth(3)
        self.setStyleSheet("""
            QSplitter::handle {
                image: url(none);
            }
            """)

        self._collapse_btn = QtWidgets.QPushButton("\u25C0\u25B6", parent)
        self._collapse_btn.setFixedSize(self.COLLAPSE_BTN_SIZE,
                                        self.COLLAPSE_BTN_SIZE)
        self._collapse_btn.setFlat(True)
        self._collapse_btn.setStyleSheet("""
            QPushButton{
                border-right: 1px solid #888;
                border-top: 1px solid #888;
                border-bottom: 1px solid #888;
                background-color: #eee;
            }
            QPushButton:hover {
                background-color: #ccc;
            }
            """)
        self._collapse_btn.show()

        self._collapse_btn.clicked.connect(self.onCollapse)
        self.splitterMoved.connect(self.onSplitterMoved)

    def onCollapse(self):
        geom = self.widget(0).geometry()
        if geom.left() < 0:
            my_geom = self.geometry()
            geom0 = self.widget(0).geometry()
            self.setSizes([geom0.width(), my_geom.width() - geom0.width()])
        else:
            geom = self.geometry()
            self.setSizes([-1, geom.width()])
        self._setCollapseButtonGeometry()
        QtCore.QTimer.singleShot(1, self._collapse_btn.repaint)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._setCollapseButtonGeometry()

    def _setCollapseButtonGeometry(self):
        g = self.widget(1).geometry()
        len = self.COLLAPSE_BTN_SIZE
        self._collapse_btn.move(g.left(),
                                g.top() + int(g.height() / 2) - int(len / 2))
        self.parent()._updateViewModeLocation()

    def onSplitterMoved(self):
        self._setCollapseButtonGeometry()
