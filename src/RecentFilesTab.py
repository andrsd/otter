from PyQt5 import QtWidgets, QtCore, QtGui
from OListView import OListView

"""
List of recent file that show on the MainWindow
"""
class RecentFilesTab(QtWidgets.QWidget):

    def __init__(self, parent):
        super(RecentFilesTab, self).__init__(parent)

        self.main_window = parent

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 0)

        self.FileList = OListView(self)
        self.FileList.setEmptyMessage("No recent files")
        main_layout.addWidget(self.FileList)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.NewButton = QtWidgets.QPushButton("New", self)
        self.NewButton.setContentsMargins(0, 0, 10, 0)
        button_layout.addWidget(self.NewButton)

        button_layout.addStretch()

        self.BrowseButton = QtWidgets.QPushButton("Browse Documents", self)
        button_layout.addWidget(self.BrowseButton)

        self.OpenButton = QtWidgets.QPushButton("Open", self)
        button_layout.addWidget(self.OpenButton)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.NewButton.clicked.connect(self.onNew)
        self.BrowseButton.clicked.connect(self.onBrowseDocuments)
        self.OpenButton.clicked.connect(self.onOpen)

        self.updateWidgets()

    def updateWidgets(self):
        if len(self.FileList.selectedIndexes()) == 1:
            self.OpenButton.setEnabled()
        else:
            self.OpenButton.setEnabled(False)

    def onNew(self):
        self.main_window.onNewFile()

    def onBrowseDocuments(self):
        pass

    def onOpen(self):
        pass
