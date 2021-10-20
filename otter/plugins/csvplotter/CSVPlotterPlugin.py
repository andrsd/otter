"""
CSVPlotterPlugin.py
"""

from otter.plugins.Plugin import Plugin
from otter.assets import Assets
from otter.plugins.csvplotter.CSVPlotterWindow import CSVPlotterWindow


class CSVPlotterPlugin(Plugin):
    """
    Plug-in for CVS plotting
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.window = None

    @staticmethod
    def name():
        return "CSV Plotter"

    @staticmethod
    def icon():
        return Assets().icons['graph']

    def onCreate(self):
        self.window = CSVPlotterWindow(self)
        if self.parent is not None and hasattr(self.parent, 'window_menu'):
            if hasattr(self.window, 'menuBar'):
                self.window.menuBar().addMenu(self.parent.window_menu)
        self.registerWindow(self.window)

    def onClose(self):
        self.window.close()
