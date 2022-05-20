from PyQt5 import QtCore
from otter.assets import Assets
from otter.plugins.Plugin import Plugin
from otter.plugins.common.LoadFileEvent import LoadFileEvent
from otter.plugins.viz.MainWindow import MainWindow


class VizPlugin(Plugin):
    """
    Plugin for visualization
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._main_window = None

    @staticmethod
    def name():
        return "Viz"

    @staticmethod
    def icon():
        return Assets().icons['movie']

    def onCreate(self):
        self._main_window = MainWindow(self)
        self.registerWindow(self._main_window)

        if self.parent is not None and hasattr(self.parent, 'window_menu'):
            if hasattr(self._main_window, 'menuBar'):
                self._main_window.menuBar().addMenu(self.parent.window_menu)

    def onClose(self):
        self._main_window.close()

    def loadFile(self, file_name):
        event = LoadFileEvent(file_name)
        QtCore.QCoreApplication.postEvent(self._main_window, event)
