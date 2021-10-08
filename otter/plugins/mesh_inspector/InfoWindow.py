from PyQt5 import QtWidgets, QtCore


class InfoWindow(QtWidgets.QWidget):
    """
    Window for showing mesh info
    """

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

        self.setWindowTitle("Info")
        self.show()

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)
