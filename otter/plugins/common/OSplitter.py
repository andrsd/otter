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

        self._collapse_btn = QtWidgets.QPushButton(">", parent)
        self._collapse_btn.setFixedSize(self.COLLAPSE_BTN_SIZE,
                                        self.COLLAPSE_BTN_SIZE)
        self._collapse_btn.setFlat(True)
        self._collapse_btn.setStyleSheet("""
            border-left: 1px solid #888;
            border-top: 1px solid #888;
            border-bottom: 1px solid #888;
            background-color: #eee;
            """)
        self._collapse_btn.show()

        self._collapse_btn.clicked.connect(self.onCollapse)
        self.splitterMoved.connect(self.onSplitterMoved)

    def onCollapse(self):
        geom = self.widget(1).geometry()
        if geom.left() > 0:
            geom = self.geometry()
            self.setSizes([geom.width(), -1])
        else:
            my_geom = self.geometry()
            geom1 = self.widget(1).geometry()
            self.setSizes([my_geom.width() - geom1.width(), geom1.width()])
        self._setCollapseButtonGeometry()
        QtCore.QTimer.singleShot(1, self._collapse_btn.repaint)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._setCollapseButtonGeometry()

    def _setCollapseButtonGeometry(self):
        g = self.widget(0).geometry()
        len = self.COLLAPSE_BTN_SIZE
        self._collapse_btn.move(g.right() - len + 1,
                                g.top() + (g.height() / 2) - (len / 2))
        self.parent()._updateViewModeLocation()

    def onSplitterMoved(self):
        self._setCollapseButtonGeometry()
