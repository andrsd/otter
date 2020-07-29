import os
from Plugin import Plugin
from PyQt5 import QtCore, QtWidgets, QtGui
from ResultWindow import ResultWindow
from ParamsWindow import ParamsWindow

class ImagePlugin(Plugin):

    def __init__(self, parent):
        super(ImagePlugin, self).__init__(parent)
        fileMenu = self.menubar.menus["File"]
        self.addMenuSeparator(fileMenu)
        self.addMenuAction(fileMenu, "Render", self.onRender, "Ctrl+Shift+R")

    @staticmethod
    def name():
        return "Image"

    @staticmethod
    def icon():
        otter_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        icon_dir = os.path.join(otter_dir, "icons")
        icon_file_name = os.path.join(icon_dir, "picture.svg")
        return QtGui.QIcon(icon_file_name)

    def onCreate(self):
        params_window = ParamsWindow(self)
        self.registerWindow(params_window)
        result_window = ResultWindow(self)
        self.registerWindow(result_window)

    def onRender(self):
        pass
