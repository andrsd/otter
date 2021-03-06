"""
MoviePlugin.py
"""

import os
# pylint: disable=no-name-in-module,import-error
from ChiggerPluginBase import ChiggerPluginBase
from PyQt5 import QtGui

class MoviePlugin(ChiggerPluginBase):
    """
    Plugin for chigger movies
    """

    def __init__(self, parent):
        # pylint: disable=useless-super-delegation
        super().__init__(parent)

    @staticmethod
    def name():
        """
        Name of the plug-in
        """
        return "Movie"

    @staticmethod
    def icon():
        """
        Icon of the plug-in
        """
        otter_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        icon_dir = os.path.join(otter_dir, "icons")
        icon_file_name = os.path.join(icon_dir, "movie.svg")
        return QtGui.QIcon(icon_file_name)
