import globs
from PyQt5 import QtCore, QtWidgets, uic

"""
About dialog
"""
class AboutDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)

        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)

        self.Layout = QtWidgets.QVBoxLayout()
        self.Layout.addSpacing(8)

        icon = QtWidgets.QApplication.windowIcon()
        self.Icon = QtWidgets.QLabel()
        self.Icon.setPixmap(icon.pixmap(64, 64))
        self.Layout.addWidget(self.Icon, 0, QtCore.Qt.AlignHCenter)

        self.Title = QtWidgets.QLabel("Otter")
        font = self.Title.font()
        font.setBold(True)
        font.setPointSize(int(1.2 * font.pointSize()))
        self.Title.setFont(font)
        self.Title.setAlignment(QtCore.Qt.AlignHCenter)
        self.Layout.addWidget(self.Title)

        self.Text = QtWidgets.QLabel(
            "Version {}\n"
            "\n"
            "Powered by chigger\n"
            "\n"
            "Application icon by partimonio design\n"
            "\n"
            "{}".format(globs.VERSION, globs.COPYRIGHT)
        )
        font = self.Text.font()
        font.setPointSize(int(0.9 * font.pointSize()))
        self.Text.setFont(font)
        self.Text.setAlignment(QtCore.Qt.AlignHCenter)
        self.Layout.addWidget(self.Text)

        self.setLayout(self.Layout)
