import os
from PyQt5 import QtWidgets, QtCore


class PluginWindowBase(QtWidgets.QMainWindow):

    MAX_RECENT_FILES = 10

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self._recent_menu = None
        self.recent_files = []
        self._clear_recent_file = None

        self._menubar = QtWidgets.QMenuBar()
        self.setMenuBar(self._menubar)

        geom = self.plugin.settings.value("window/geometry")
        default_size = QtCore.QSize(1000, 700)
        if geom is None:
            self.resize(default_size)
        else:
            if not self.restoreGeometry(geom):
                self.resize(default_size)
        self.recent_files = self.plugin.settings.value("recent_files", [])

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
        self.plugin.settings.setValue("recent_files", self.recent_files)
        event.accept()

    def onClose(self):
        self.plugin.close()

    def buildRecentFilesMenu(self):
        """
        Build recent files submenu
        """
        if self._recent_menu is None:
            return

        self._recent_menu.clear()
        if len(self.recent_files) > 0:
            for f in reversed(self.recent_files):
                unused_path, file_name = os.path.split(f)
                action = self._recent_menu.addAction(file_name,
                                                     self.onOpenRecentFile)
                action.setData(f)
            self._recent_menu.addSeparator()
        self._clear_recent_file = self._recent_menu.addAction(
            "Clear Menu", self.onClearRecentFiles)

    def addToRecentFiles(self, file_name):
        """
        Add file to recent files
        @param file_name[str] Name of the file
        """
        self.recent_files = [f for f in self.recent_files if f != file_name]
        self.recent_files.append(file_name)
        if len(self.recent_files) > self.MAX_RECENT_FILES:
            del self.recent_files[0]
        self.buildRecentFilesMenu()

    def loadFile(self, file_menu):
        # no-op method in cacse the child is not using recent files
        pass

    def onOpenRecentFile(self):
        """
        Called when opening a file from 'Recent files' submenu
        """
        action = self.sender()
        file_name = action.data()
        self.loadFile(file_name)

    def onClearRecentFiles(self):
        """
        Called when activating 'Clear' in 'Recent files' submenu
        """
        self.recent_files = []
        self.buildRecentFilesMenu()
