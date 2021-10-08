"""
ChiggerPluginBase.py
"""

from Plugin import Plugin
from ResultWindow import ResultWindow
from ParamsWindow import ParamsWindow


class ChiggerPluginBase(Plugin):
    """
    Base class for chigger plugins
    """

    def __init__(self, parent):
        super().__init__(parent)
        file_menu = self.menubar.menus["File"]
        self.addMenuSeparator(file_menu)
        self.addMenuAction(file_menu, "Render", self.onRender, "Ctrl+Shift+R")

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
