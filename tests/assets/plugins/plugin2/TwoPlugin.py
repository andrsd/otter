from PyQt5 import QtGui
from unittest.mock import MagicMock


class TwoPlugin(MagicMock):

    @staticmethod
    def name():
        return "Two"

    @staticmethod
    def icon():
        return QtGui.QIcon()
