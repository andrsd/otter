import os
from Plugin import Plugin
from PyQt5 import QtCore, QtWidgets, QtGui
from common.ResultWindow import ResultWindow
from common.ParamsWindow import ParamsWindow

class ChiggerPluginBase(Plugin):

    def __init__(self, parent):
        super(ChiggerPluginBase, self).__init__(parent)
        fileMenu = self.menubar.menus["File"]
        self.addMenuSeparator(fileMenu)
        self.addMenuAction(fileMenu, "Render", self.onRender, "Ctrl+Shift+R")

    def onCreate(self):
        params_window = ParamsWindow(self)
        self.registerWindow(params_window)
        result_window = ResultWindow(self)
        self.registerWindow(result_window)

    def onRender(self):
        pass
