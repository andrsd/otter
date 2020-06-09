from PyQt5 import QtWidgets, QtCore

class ParamsWindow(QtWidgets.QMainWindow):

    def __init__(self, parent = None):
        super(ParamsWindow, self).__init__(parent)

        self.setWindowTitle("Untitled")
        self.show()
