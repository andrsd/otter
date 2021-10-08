import os
import platform
from PyQt5 import QtCore, QtGui


class Assets:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.on_new()
        return cls._instance

    def on_new(self):
        if platform.system() == "Darwin":
            path = os.environ.get('RESOURCEPATH', os.path.dirname(__file__))
        else:
            path = os.path.dirname(__file__)

        icons_dir = os.path.join(path, 'icons')

        self.app_icon = QtGui.QIcon(os.path.join(icons_dir, 'otter.svg'))
        self.graph_icon = QtGui.QIcon(os.path.join(icons_dir, 'graph.svg'))
        self.movie_icon = QtGui.QIcon(os.path.join(icons_dir, 'movie.svg'))
