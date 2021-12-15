from PyQt5 import QtCore
from otter.assets import Assets
from otter.plugins.Plugin import Plugin
from otter.plugins.common.LoadFileEvent import LoadFileEvent
from otter.plugins.viz.RenderWindow import RenderWindow


class VizPlugin(Plugin):
    """
    Plugin for visualization
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._render_window = None

    @staticmethod
    def name():
        return "Viz"

    @staticmethod
    def icon():
        return Assets().icons['movie']

    def onCreate(self):
        self._render_window = RenderWindow(self)
        self.registerWindow(self._render_window)

        if self.parent is not None and hasattr(self.parent, 'window_menu'):
            if hasattr(self._render_window, 'menuBar'):
                self._render_window.menuBar().addMenu(self.parent.window_menu)

    def onClose(self):
        self._render_window.close()

    def loadFile(self, file_name):
        event = LoadFileEvent(file_name)
        QtCore.QCoreApplication.postEvent(self._render_window, event)
