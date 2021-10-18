"""
CSVPlotterPlugin.py
"""

from Plugin import Plugin
from otter.assets import Assets
from csvplotter.CSVPlotterWindow import CSVPlotterWindow


class CSVPlotterPlugin(Plugin):
    """
    Plug-in for CVS plotting
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.window = None

    @staticmethod
    def name():
        """
        Name of the plug-in
        """
        return "CSV Plotter"

    @staticmethod
    def icon():
        """
        Icon of the plug-in
        """
        return Assets().icons['graph']

    def onCreate(self):
        """
        Create handler
        """
        self.window = CSVPlotterWindow(self)
        self.registerWindow(self.window)
