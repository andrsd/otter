from PyQt5 import QtWidgets, QtCore


class PluginWindowBase(QtWidgets.QMainWindow):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

        self._menubar = QtWidgets.QMenuBar()
        self.setMenuBar(self._menubar)

        geom = self.plugin.settings.value("window/geometry")
        default_size = QtCore.QSize(1000, 700)
        if geom is None:
            self.resize(default_size)
        else:
            if not self.restoreGeometry(geom):
                self.resize(default_size)

    @property
    def menubar(self):
        return self._menubar

    def event(self, event):
        """
        Event handler
        """
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

    def closeEvent(self, event):
        self.plugin.settings.setValue("window/geometry", self.saveGeometry())
        event.accept()

    def onClose(self):
        self.plugin.close()
