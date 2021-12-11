from PyQt5 import QtWidgets


class HLine(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setContentsMargins(0, 10, 0, 10)
        self.setFixedHeight(10)
        self.setStyleSheet("""
            color: #D3D3D3;
            """)
