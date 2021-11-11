from PyQt5 import QtWidgets


class ColorButton(QtWidgets.QPushButton):
    """
    Button that dsiplays a rectangle with a color
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    def setColor(self, qcolor):
        self.setStyleSheet("""
            QPushButton {{
                border: 1px solid #000;
                background-color: {};
            }}
            QPushButton::menu-indicator {{
                width: 0px
            }}
            """.format(qcolor.name()))
