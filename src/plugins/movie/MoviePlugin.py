import os
from common.ChiggerPluginBase import ChiggerPluginBase
from PyQt5 import QtCore, QtWidgets, QtGui

class MoviePlugin(ChiggerPluginBase):

    def __init__(self, parent):
        super(MoviePlugin, self).__init__(parent)

    @staticmethod
    def name():
        return "Movie"

    @staticmethod
    def icon():
        otter_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        icon_dir = os.path.join(otter_dir, "icons")
        icon_file_name = os.path.join(icon_dir, "movie.svg")
        return QtGui.QIcon(icon_file_name)
