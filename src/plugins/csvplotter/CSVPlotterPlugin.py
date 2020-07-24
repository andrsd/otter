import os
from Plugin import Plugin
from PyQt5 import QtCore, QtWidgets, QtGui

class CSVPlotterPlugin(Plugin):

    def __init__(self):
        super(CSVPlotterPlugin, self).__init__()
        pass

    def name(self):
        return "CSV Plotter"

    def icon(self):
        otter_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
        icon_dir = os.path.join(otter_dir, "icons")
        icon_file_name = os.path.join(icon_dir, "graph.svg")
        return QtGui.QIcon(icon_file_name)

    def create(self, parent):
        super(CSVPlotterPlugin, self).create(parent)

    def onCloseFile(self):
        super(CSVPlotterPlugin, self).onCloseFile()

    def onMinimize(self):
        pass

    def onBringAllToFront(self):
        pass

    def showWindow(self):
        pass

    def setWindowVisible(self, visible):
        pass

    def updateMenuBar(self):
        pass
