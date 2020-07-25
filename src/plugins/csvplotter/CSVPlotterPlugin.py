import os
from Plugin import Plugin
from PyQt5 import QtCore, QtWidgets, QtGui
from CSVPlotterWindow import CSVPlotterWindow

class CSVPlotterPlugin(Plugin):

    def __init__(self, parent):
        super(CSVPlotterPlugin, self).__init__(parent)
        self.window = None

    @staticmethod
    def name():
        return "CSV Plotter"

    @staticmethod
    def icon():
        otter_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
        icon_dir = os.path.join(otter_dir, "icons")
        icon_file_name = os.path.join(icon_dir, "graph.svg")
        return QtGui.QIcon(icon_file_name)

    def create(self):
        if self.window == None:
            self.window = CSVPlotterWindow(self)
            self.registerWindow(self.window)
