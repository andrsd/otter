"""
CSVPlotterPlugin.py
"""

import os
# pylint: disable=import-error
from Plugin import Plugin
from PyQt5 import QtGui
from CSVPlotterWindow import CSVPlotterWindow

class CSVPlotterPlugin(Plugin):
    """
    Plug-in for CVS plotting
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.window = None
        file_menu = self.menubar.menus["File"]
        self.addMenuSeparator(file_menu)
        self._export_menu = self.addMenu(file_menu, "Export")
        self._export_png = self.addMenuAction(self._export_menu, "PNG...", self.onExportPng)
        self._export_pdf = self.addMenuAction(self._export_menu, "PDF...", self.onExportPdf)
        self._export_gnuplot = self.addMenuAction(self._export_menu, "gnuplot...",
            self.onExportGnuplot)

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
        otter_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        icon_dir = os.path.join(otter_dir, "icons")
        icon_file_name = os.path.join(icon_dir, "graph.svg")
        return QtGui.QIcon(icon_file_name)

    def onCreate(self):
        """
        Create handler
        """
        self.window = CSVPlotterWindow(self)
        self.registerWindow(self.window)

    def onExportPdf(self):
        """
        Export PDF handler
        """
        self.window.onExport("pdf")

    def onExportPng(self):
        """
        Export PNG handler
        """
        self.window.onExport("png")

    def onExportGnuplot(self):
        """
        Export gnuplot handler
        """
        self.window.onExport("gnuplot")
