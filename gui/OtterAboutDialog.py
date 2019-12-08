import otter
from PyQt5 import QtCore, QtWidgets

class OtterAboutDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super(OtterAboutDialog, self).__init__(parent)
        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addSpacing(8)

        icon = QtWidgets.QApplication.windowIcon()
        self.lblIcon = QtWidgets.QLabel()
        self.lblIcon.setPixmap(icon.pixmap(64, 64))
        self.layout.addWidget(self.lblIcon, 0, QtCore.Qt.AlignHCenter)

        self.lblTitle = QtWidgets.QLabel("Otter")
        font = self.lblTitle.font()
        font.setBold(True)
        font.setPointSize(int(1.2 * font.pointSize()))
        self.lblTitle.setFont(font)
        self.lblTitle.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.lblTitle)

        self.lblText = QtWidgets.QLabel(
            "Version {}\n"
            "\n"
            "Powered by chigger\n"
            "\n"
            "Application icon by partimonio design\n"
            "\n"
            "(c) 2019 David Andrs. All rights reserved.".format(otter.VERSION)
        )
        font = self.lblText.font()
        font.setPointSize(int(0.9 * font.pointSize()))
        self.lblText.setFont(font)
        self.lblText.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.lblText)

        self.setLayout(self.layout)
