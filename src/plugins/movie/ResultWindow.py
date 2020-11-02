"""
ResultWindow.py
"""

from PyQt5 import QtCore, QtWidgets

class ResultWindow(QtWidgets.QMainWindow):
    """
    Window for displaying the result
    """

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

        self.frame = QtWidgets.QFrame()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.frame.setLayout(self.layout)
        self.setCentralWidget(self.frame)
        self.setWindowTitle("Result")
        self.show()

    def event(self, event):
        """
        Event callback
        """
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)
