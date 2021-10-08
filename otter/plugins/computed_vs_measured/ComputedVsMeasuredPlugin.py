"""
ComputedVsMeasuredPlugin.py
"""

import os
from Plugin import Plugin
from PyQt5 import QtGui
from otter.assets import Assets
from ComputedVsMeasuredWindow import ComputedVsMeasuredWindow

class ComputedVsMeasuredPlugin(Plugin):
    """
    Plug-in for plotting computed vs measured data
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.window = None

    @staticmethod
    def name():
        """
        Name of the plug-in
        """
        return "Computed vs. Measured"

    @staticmethod
    def icon():
        """
        Icon of the plug-in
        """
        return Assets().graph_icon

    def onCreate(self):
        """
        Create handler
        """
        self.window = ComputedVsMeasuredWindow(self)
        self.registerWindow(self.window)
