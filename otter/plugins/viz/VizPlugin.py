from otter.assets import Assets
from otter.plugins.Plugin import Plugin
from otter.plugins.viz.ResultWindow import ResultWindow
from otter.plugins.viz.ParamsWindow import ParamsWindow


class VizPlugin(Plugin):
    """
    Plugin for visualization
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._params_window = None
        self._result_window = None

    @staticmethod
    def name():
        return "Viz"

    @staticmethod
    def icon():
        return Assets().icons['movie']

    def onCreate(self):
        self._params_window = ParamsWindow(self)
        self._result_window = ResultWindow(self)
        self.registerWindow(self._result_window)

        if self.parent is not None and hasattr(self.parent, 'window_menu'):
            if hasattr(self._result_window, 'menuBar'):
                self._result_window.menuBar().addMenu(self.parent.window_menu)

    def onClose(self):
        self._params_window.close()
        self._result_window.close()
