from PyQt5 import QtWidgets, QtCore


class OSplitter(QtWidgets.QSplitter):

    COLLAPSE_BTN_SIZE = 32

    COLLAPSE_BTN_SIDE_RIGHT = 0
    COLLAPSE_BTN_SIDE_LEFT = 1

    def __init__(self, orientation, parent=None):
        super().__init__(parent)
        self._handle_side = self.COLLAPSE_BTN_SIDE_RIGHT
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

    def setHandleSide(self, side):
        self._handle_side = side
        self._setCollapsibleButtonStyle()

    def _setCollapsibleButtonStyle(self):
        if self._handle_side == self.COLLAPSE_BTN_SIDE_RIGHT:
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
        else:
            self._collapse_btn.setStyleSheet("""
                QPushButton{
                    border-left: 1px solid #888;
                    border-top: 1px solid #888;
                    border-bottom: 1px solid #888;
                    background-color: #eee;
                }
                QPushButton:hover {
                    background-color: #ccc;
                }
                """)

    def onCollapse(self):
        if self._handle_side == self.COLLAPSE_BTN_SIDE_RIGHT:
            geom = self.widget(0).geometry()
            if geom.left() < 0:
                my_geom = self.geometry()
                geom0 = self.widget(0).geometry()
                self.setSizes([geom0.width(), my_geom.width() - geom0.width()])
            else:
                geom = self.geometry()
                self.setSizes([-1, geom.width()])
        else:
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
        if self._handle_side == self.COLLAPSE_BTN_SIDE_RIGHT:
            g = self.widget(1).geometry()
            len = self.COLLAPSE_BTN_SIZE
            self._collapse_btn.move(g.left(),
                                    g.top() + int(g.height() / 2) -
                                    int(len / 2))
        else:
            g = self.widget(0).geometry()
            len = self.COLLAPSE_BTN_SIZE
            self._collapse_btn.move(g.right() - len + 1,
                                    g.top() + (g.height() / 2) - (len / 2))
        self.parent()._updateViewModeLocation()

    def onSplitterMoved(self):
        self._setCollapseButtonGeometry()
