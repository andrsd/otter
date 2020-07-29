from PyQt5 import QtCore, QtWidgets

class ResultWindow(QtWidgets.QMainWindow):

    def __init__(self, plugin):
        super(ResultWindow, self).__init__()
        self.plugin = plugin

        self.frame = QtWidgets.QFrame()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.frame.setLayout(self.layout)
        self.setCentralWidget(self.frame)
        self.setWindowTitle("Result")
        self.show()

    def event(self, e):
        if (e.type() == QtCore.QEvent.WindowActivate):
            self.plugin.updateMenuBar()
        return super(ResultWindow, self).event(e);
