from PyQt5 import QtCore, QtWidgets

class ResultWindow(QtWidgets.QMainWindow):

    def __init__(self, parent = None):
        super(ResultWindow, self).__init__(parent)

        self.frame = QtWidgets.QFrame()
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.frame.setLayout(self.layout)
        self.setCentralWidget(self.frame)
        self.setWindowTitle("Result")
        self.show()
