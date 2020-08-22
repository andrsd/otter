"""
AboutDialog.py
"""

from PyQt5 import QtCore, QtWidgets
import consts

class AboutDialog(QtWidgets.QDialog):
    """ About dialog """

    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addSpacing(8)

        icon = QtWidgets.QApplication.windowIcon()
        self.icon = QtWidgets.QLabel()
        self.icon.setPixmap(icon.pixmap(64, 64))
        self.layout.addWidget(self.icon, 0, QtCore.Qt.AlignHCenter)

        self.title = QtWidgets.QLabel("Otter")
        font = self.title.font()
        font.setBold(True)
        font.setPointSize(int(1.2 * font.pointSize()))
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.title)

        self.text = QtWidgets.QLabel(
            "Version {}\n"
            "\n"
            "Powered by chigger\n"
            "\n"
            "Application icon by partimonio design\n"
            "\n"
            "{}".format(consts.VERSION, consts.COPYRIGHT)
        )
        font = self.text.font()
        font.setPointSize(int(0.9 * font.pointSize()))
        self.text.setFont(font)
        self.text.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.text)

        self.setLayout(self.layout)
