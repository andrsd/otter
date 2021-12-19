from PyQt5 import QtWidgets, QtCore


class SelectedMeshEntityInfoWidget(QtWidgets.QWidget):
    """
    Display information about selected mesh entity (like node or element)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            border-radius: 3px;
            background-color: #222;
            color: #fff;
            font-size: 14px;
            """)
        self._opacity = QtWidgets.QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(0.8)
        self.setGraphicsEffect(self._opacity)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(15, 8, 15, 8)

        self._text = QtWidgets.QLabel()
        self._layout.addWidget(self._text)

        self.setLayout(self._layout)

    def setText(self, text):
        self._text.setText(text)

    def clear(self):
        self._text.setText("")

    def setNodeInfo(self, node):
        text = "Node ID: 1234, X: 0.0, Y: 0.0, Z: 0.0".format()
        self.setText(text)

    def setElementInfo(self, element):
        text = "Element ID: 1234, type: tetrahedra".format()
        self.setText(text)

    def setBlockInfo(self, blk_id, info):
        text = "Block: {}".format(blk_id)
        text += self._formatInfo(info)
        self.setText(text)

    def setSidesetInfo(self, sideset_id, info):
        text = "Side set: {}".format(sideset_id)
        text += self._formatInfo(info)
        self.setText(text)

    def setNodesetInfo(self, nodeset_id, info):
        text = "Node set: {}".format(nodeset_id)
        text += self._formatInfo(info)
        self.setText(text)

    def _formatInfo(self, info):
        text = ""
        if 'cells' in info:
            text += "\nElements: {}".format(info['cells'])
        if 'points' in info:
            text += "\nNodes: {}".format(info['points'])
        if 'bounds' in info:
            bmin, bmax = info['bounds']
            text += "\nRange:"
            text += "\n  X: {:.5f}..{:.5f}".format(bmin.x(), bmax.x())
            text += "\n  Y: {:.5f}..{:.5f}".format(bmin.y(), bmax.y())
            text += "\n  Z: {:.5f}..{:.5f}".format(bmin.z(), bmax.z())
        return text
