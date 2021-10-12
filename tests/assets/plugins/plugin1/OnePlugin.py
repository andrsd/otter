from PyQt5 import QtGui
from unittest.mock import MagicMock


class OnePlugin(MagicMock):

    @staticmethod
    def name():
        return "One"

    @staticmethod
    def icon():
        return QtGui.QIcon()
