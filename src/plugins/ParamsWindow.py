from PyQt5 import QtWidgets, QtCore

class ParamsWindow(QtWidgets.QMainWindow):

    def __init__(self, plugin):
        super(ParamsWindow, self).__init__()
        self.plugin = plugin

        self.setWindowTitle("Untitled")
        self.show()

    def event(self, e):
        if (e.type() == QtCore.QEvent.WindowActivate):
            self.plugin.updateMenuBar()
        return super(ParamsWindow, self).event(e);
