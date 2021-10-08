"""
ParamsWindow.py
"""

from PyQt5 import QtWidgets, QtCore


class ParamsWindow(QtWidgets.QMainWindow):
    """
    Window for entering parameters
    """

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

        self.setWindowTitle("Untitled")
        self.show()

    def event(self, event):
        """
        Event callback
        """
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)
