"""
ComputedVsMeasuredPlugin.py
"""

import os
# pylint: disable=import-error
from Plugin import Plugin
from PyQt5 import QtGui
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
        otter_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        icon_dir = os.path.join(otter_dir, "icons")
        icon_file_name = os.path.join(icon_dir, "graph.svg")
        return QtGui.QIcon(icon_file_name)

    def onCreate(self):
        """
        Create handler
        """
        self.window = ComputedVsMeasuredWindow(self)
        self.registerWindow(self.window)
