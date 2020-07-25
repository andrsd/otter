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

        self.file_list = OListView(self)
        self.file_list.setEmptyMessage("No recent files")
        main_layout.addWidget(self.file_list)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.new_button = QtWidgets.QPushButton("New", self)
        self.new_button.setContentsMargins(0, 0, 10, 0)
        button_layout.addWidget(self.new_button)

        button_layout.addStretch()

        self.browse_button = QtWidgets.QPushButton("Browse Documents", self)
        button_layout.addWidget(self.browse_button)

        self.open_button = QtWidgets.QPushButton("Open", self)
        button_layout.addWidget(self.open_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.new_button.clicked.connect(self.onNew)
        self.browse_button.clicked.connect(self.onBrowseDocuments)
        self.open_button.clicked.connect(self.onOpen)

        self.updateWidgets()

    def updateWidgets(self):
        if len(self.file_list.selectedIndexes()) == 1:
            self.open_button.setEnabled()
        else:
            self.open_button.setEnabled(False)

    def onNew(self):
        self.main_window.onNewFile()

    def onBrowseDocuments(self):
        pass

    def onOpen(self):
        pass
