from otter.assets import Assets
from otter.plugins.Plugin import Plugin
from otter.plugins.movie.ResultWindow import ResultWindow
from otter.plugins.movie.ParamsWindow import ParamsWindow


class MoviePlugin(Plugin):
    """
    Plugin for rendering movies
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._params_window = None
        self._result_window = None

    @staticmethod
    def name():
        return "Movie"

    @staticmethod
    def icon():
        return Assets().icons['movie']

    def onCreate(self):
        self._params_window = ParamsWindow(self)
        self.registerWindow(self._params_window)
        self._result_window = ResultWindow(self)
        self.registerWindow(self._result_window)
