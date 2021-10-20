import os
from PyQt5 import QtCore, QtWidgets


class ResultWindow(QtWidgets.QMainWindow):
    """
    Window for displaying the result
    """

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self._file_name = None

        self.frame = QtWidgets.QFrame()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.frame.setLayout(self.layout)

        self.setCentralWidget(self.frame)
        self.updateWindowTitle()

        geom = self.plugin.settings.value("window/geometry")
        default_size = QtCore.QSize(700, 500)
        if geom is None:
            self.resize(default_size)
        else:
            if not self.restoreGeometry(geom):
                self.resize(default_size)

        self.setupMenuBar()
        self.show()

    def setupMenuBar(self):
        self._menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self._menubar)

        file_menu = self._menubar.addMenu("File")
        self._new_action = file_menu.addAction(
            "New", self.onNewFile, "Ctrl+N")
        self._open_action = file_menu.addAction(
            "Open", self.onOpenFile, "Ctrl+O")
        file_menu.addSeparator()
        self._close_action = file_menu.addAction(
            "Close", self.onClose, "Ctrl+W")
        file_menu.addSeparator()
        self._render_action = file_menu.addAction(
            "Render", self.onRender, "Ctrl+Shift+R")

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

    def closeEvent(self, event):
        self.plugin.settings.setValue("window/geometry", self.saveGeometry())
        event.accept()

    def updateWindowTitle(self):
        title = "Result"
        if self._file_name is None:
            self.setWindowTitle(title)
        else:
            self.setWindowTitle("{} \u2014 {}".format(
                title, os.path.basename(self._file_name)))

    def onNewFile(self):
        pass

    def onOpenFile(self):
        pass

    def onRender(self):
        pass

    def onClose(self):
        self.plugin.close()
