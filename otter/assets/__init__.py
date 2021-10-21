import os
import platform
from PyQt5 import QtGui


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

        icons = {
            'app': 'otter.svg',
            'graph': 'graph.svg',
            'movie': 'movie.svg',
            'render-mode': 'render-mode.svg'
        }
        self.icons = {}

        for name, file_name in icons.items():
            self.icons[name] = QtGui.QIcon(os.path.join(icons_dir, file_name))
