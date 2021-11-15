from PyQt5 import QtWidgets
from otter.assets import Assets
from otter.plugins.Plugin import Plugin
from otter.plugins.viz.RenderWindow import RenderWindow
from otter.plugins.viz.ParamsWindow import ParamsWindow


class VizPlugin(Plugin):
    """
    Plugin for visualization
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._params_window = None
        self._render_window = None

    @staticmethod
    def name():
        return "Viz"

    @staticmethod
    def icon():
        return Assets().icons['movie']

    def onCreate(self):
        self._render_window = RenderWindow(self)
        renderer = self._render_window.getVtkRenderer()
        self._params_window = ParamsWindow(self, renderer)
        self.registerWindow(self._render_window)

        if self.parent is not None and hasattr(self.parent, 'window_menu'):
            if hasattr(self._render_window, 'menuBar'):
                self._render_window.menuBar().addMenu(self.parent.window_menu)

    def onClose(self):
        self._params_window.close()
        self._render_window.close()

    def onNewFile(self):
        self._render_window.clear()
        self._params_window.clear()

    def onOpenFile(self):
        file_name, f = QtWidgets.QFileDialog.getOpenFileName(
            self._render_window,
            'Open File',
            "",
            "ExodusII files (*.e *.exo)")
        if file_name:
            self.loadFile(file_name)

    def loadFile(self, file_name):
        self._params_window.loadFile(file_name)

    def onRender(self):
        pass
