import os
from Plugin import Plugin
from PyQt5 import QtCore, QtWidgets, QtGui
from ResultWindow import ResultWindow
from ParamsWindow import ParamsWindow

class ImagePlugin(Plugin):

    def __init__(self, parent):
        super(ImagePlugin, self).__init__(parent)
        self.params_window = None
        self.result_window = None

    @staticmethod
    def name():
        return "Image"

    @staticmethod
    def icon():
        otter_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        icon_dir = os.path.join(otter_dir, "icons")
        icon_file_name = os.path.join(icon_dir, "picture.svg")
        return QtGui.QIcon(icon_file_name)

    def create(self):
        if self.params_window == None:
            self.params_window = ParamsWindow(self)
            self.registerWindow(self.params_window)
        if self.result_window == None:
            self.result_window = ResultWindow(self)
            self.registerWindow(self.result_window)
