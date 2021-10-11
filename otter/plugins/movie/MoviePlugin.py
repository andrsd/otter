from otter.assets import Assets
from Plugin import Plugin
from ResultWindow import ResultWindow
from ParamsWindow import ParamsWindow


class MoviePlugin(Plugin):
    """
    Plugin for movies
    """

    def __init__(self, parent):
        super().__init__(parent)
        file_menu = self.menubar.menus["File"]
        self.addMenuSeparator(file_menu)
        self.addMenuAction(file_menu, "Render", self.onRender, "Ctrl+Shift+R")

    @staticmethod
    def name():
        """
        Name of the plug-in
        """
        return "Movie"

    @staticmethod
    def icon():
        """
        Icon of the plug-in
        """
        return Assets().icons['movie']

    def onCreate(self):
        """
        Called when plug-in created
        """
        params_window = ParamsWindow(self)
        self.registerWindow(params_window)
        result_window = ResultWindow(self)
        self.registerWindow(result_window)

    def onRender(self):
        """
        Called when rendering is triggered
        """
