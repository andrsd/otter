import os
from Plugin import Plugin
from PyQt5 import QtCore, QtWidgets, QtGui
from CSVPlotterWindow import CSVPlotterWindow

class CSVPlotterPlugin(Plugin):

    def __init__(self, parent):
        super(CSVPlotterPlugin, self).__init__(parent)
        self.window = None
        fileMenu = self.menubar.menus["File"]
        self.addMenuSeparator(fileMenu)
        self._export_menu = self.addMenu(fileMenu, "Export")
        self._export_png = self.addMenuAction(self._export_menu, "PNG...", self.onExportPng)
        self._export_pdf = self.addMenuAction(self._export_menu, "PDF...", self.onExportPdf)

    @staticmethod
    def name():
        return "CSV Plotter"

    @staticmethod
    def icon():
        otter_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        icon_dir = os.path.join(otter_dir, "icons")
        icon_file_name = os.path.join(icon_dir, "graph.svg")
        return QtGui.QIcon(icon_file_name)

    def onCreate(self):
        self.window = CSVPlotterWindow(self)
        self.registerWindow(self.window)

    def onExportPdf(self):
        self.window.onExport("pdf")

    def onExportPng(self):
        self.window.onExport("png")
