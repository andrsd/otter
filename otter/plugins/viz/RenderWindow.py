import os
from PyQt5 import QtWidgets
from otter.plugins.PluginWindowBase import PluginWindowBase


class RenderWindow(PluginWindowBase):
    """
    Window for displaying the result
    """

    def __init__(self, plugin):
        super().__init__(plugin)
        self._file_name = None

        self.frame = QtWidgets.QFrame()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.frame.setLayout(self.layout)

        self.setCentralWidget(self.frame)
        self.updateWindowTitle()

        self.setupMenuBar()
        self.show()

    def setupMenuBar(self):
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
