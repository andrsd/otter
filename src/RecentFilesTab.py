import os
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

        self.model = QtGui.QStandardItemModel()

        self.file_list = OListView(self)
        self.file_list.setEmptyMessage("No recent files")
        self.file_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.file_list.setModel(self.model)
        self.fillFileList()
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
        self.file_list.selectionModel().selectionChanged.connect(self.onFileChanged)
        self.file_list.doubleClicked.connect(self.onOpen)

        self.updateControls()

    def addFileItem(self, file_name):
        qapp = QtWidgets.QApplication.instance()
        icon = qapp.windowIcon()

        path, base_name = os.path.split(file_name)
        file = QtCore.QFile(file_name)
        file_time = file.fileTime(QtCore.QFileDevice.FileModificationTime)

        si = QtGui.QStandardItem(base_name)
        si.setData(file_name)
        si.setData(file_time, QtCore.Qt.UserRole + 2)
        si.setIcon(icon)
        self.model.appendRow(si)

    def fillFileList(self):
        settings = QtCore.QSettings()

        settings.beginGroup("MainWindow")
        recent_files = settings.value("recentFiles", [])
        settings.endGroup()

        self.model.clear()
        for file_name in reversed(recent_files):
            self.addFileItem(file_name)

    def updateControls(self):
        if len(self.file_list.selectedIndexes()) == 1:
            self.open_button.setEnabled(True)
        else:
            self.open_button.setEnabled(False)

    def onNew(self):
        self.main_window.onNewFile()

    def onBrowseDocuments(self):
        pass

    def onFileChanged(self, si):
        self.updateControls()

    def onOpen(self):
        sel_idx = self.file_list.selectedIndexes()[0]
        si = self.model.itemFromIndex(sel_idx)
        file_name = si.data()
        self.main_window.openFile(file_name)

    def clear(self):
        self.model.clear()
