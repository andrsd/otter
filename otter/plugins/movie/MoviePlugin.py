"""
MoviePlugin.py
"""

import os
from ChiggerPluginBase import ChiggerPluginBase
from PyQt5 import QtGui
from otter.assets import Assets

class MoviePlugin(ChiggerPluginBase):
    """
    Plugin for chigger movies
    """

    def __init__(self, parent):
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
        return Assets().movie_icon
