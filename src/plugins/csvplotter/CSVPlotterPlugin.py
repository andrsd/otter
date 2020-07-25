import os
from Plugin import Plugin
from PyQt5 import QtCore, QtWidgets, QtGui
from CSVPlotterWindow import CSVPlotterWindow

class CSVPlotterPlugin(Plugin):

    def __init__(self):
        super(CSVPlotterPlugin, self).__init__()
        self.window = None

    def name(self):
        return "CSV Plotter"

    def icon(self):
        otter_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
        icon_dir = os.path.join(otter_dir, "icons")
        icon_file_name = os.path.join(icon_dir, "graph.svg")
        return QtGui.QIcon(icon_file_name)

    def create(self, parent):
        super(CSVPlotterPlugin, self).create(parent)
        self._show_window = parent._windowMenu.addAction("CSV Plotter", self.onShowWindow)
        self._show_window.setCheckable(True)
        parent._action_group_windows.addAction(self._show_window)
        if self.window == None:
            self.window = CSVPlotterWindow(self)

        self.file = QtCore.QFile()

    def onCloseFile(self):
        super(CSVPlotterPlugin, self).onCloseFile()
        self.window.close()
        self.window = None
        self.parent._action_group_windows.removeAction(self._show_window)
        self._show_window = None

    def onMinimize(self):
        self.window.showMinimized()

    def onBringAllToFront(self):
        self.window.showNormal()

    def showWindow(self):
        self.window.show()

    def setWindowVisible(self, visible):
        self._show_window.setVisible(visible)

    def updateMenuBar(self):
        pass

    def onShowWindow(self):
        self.window.showNormal()
        self.window.activateWindow()
        self.window.raise_()
        self.updateMenuBar()
