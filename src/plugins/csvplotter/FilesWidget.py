"""
FilesWidget.py
"""

import os
import glob
from PyQt5 import QtWidgets, QtCore

class FilesComboBox(QtWidgets.QComboBox):
    """
    A ComboBox that disables filenames if they do not exist using glob.

    NOTE: glob is used so that this will work with MultiApps when that is added.
    """

    def showPopup(self):
        """
        Override to enable/disable files based on existence.
        """
        for i in range(self.count()):
            self.model().item(i).setEnabled(bool(glob.glob(self.itemData(i))))
        super().showPopup()

    def hasItem(self, full_file):
        """
        Return true if the file already exists.
        """
        return full_file in [self.itemData(i) for i in range(self.count())]

    def itemIndex(self, full_file):
        """
        Return the index given the full filename.
        """
        return [self.itemData(i) for i in range(self.count())].index(full_file)


class FilesWidget(QtWidgets.QWidget):
    """
    Widget for selecting and opening files
    """

    loadFile = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        self.setMinimumWidth(300)
        self.setContentsMargins(0, 0, 0, 0)

        self.open_files = QtWidgets.QPushButton("+")
        self.open_files.setEnabled(True)
        self.open_files.clicked.connect(self.onOpenFiles)
        # FIXME: enable the icon again
        # self.open_files.setIcon("")
        self.open_files.setIconSize(QtCore.QSize(16, 16))
        self.open_files.setFixedSize(self.open_files.iconSize())
        self.open_files.setToolTip("Select a file to open.")
        self.open_files.setStyleSheet("QPushButton {border:none}")

        self.file_list = FilesComboBox()
        self.file_list.currentIndexChanged.connect(self.onFileListIndexChanged)

        self.layout_main = QtWidgets.QHBoxLayout()
        self.layout_main.setSpacing(10)
        self.layout_main.addWidget(self.file_list)
        self.layout_main.addWidget(self.open_files)
        self.layout_main.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout_main)

        self.open_file_caption = ""
        self.open_file_filter = "All files (*)"

        self.updateControls()

    def currentFileName(self):
        """
        Get current file name
        """
        index = self.file_list.currentIndex()
        file_name = str(self.file_list.itemData(index))
        return file_name

    def updateControls(self):
        """
        Update controls
        """
        if self.file_list.count() > 0:
            self.file_list.setEnabled(True)
        else:
            self.file_list.setEnabled(False)

    def onSetFilenames(self, filenames):
        """
        Updates the list of available files for selection.

        This is the entry point for loading a file via the FilePlugin.

        @param filenames[list]: The filenames to include in the FileList widget.
        """
        self.file_list.clear()

        for full_file in filenames:
            txt = "{} ({})".format(os.path.basename(full_file), os.path.dirname(full_file))
            self.file_list.addItem(txt, full_file)

        self.file_list.blockSignals(True)
        self.file_list.setCurrentIndex(0)
        self.file_list.blockSignals(False)
        self.updateControls()

    def updateFileList(self, filenames):
        """
        Update list of files
        """
        if self.file_list.count() == 0:
            self.onSetFilenames(filenames)

        index = self.file_list.currentIndex()

        self.file_list.blockSignals(True)
        # add the file into the file list, if it does not exist there
        for full_file in filenames:
            if not self.file_list.hasItem(full_file):
                self.file_list.addItem(os.path.basename(full_file), full_file)
            if os.path.exists(full_file):
                index = self.file_list.itemIndex(full_file)

        self.file_list.blockSignals(False)
        if index != self.file_list.currentIndex():
            self.file_list.setCurrentIndex(index)

    def onOpenFiles(self):
        """
        Callback for opening additional file(s)
        """
        (fn, unused_filter) = QtWidgets.QFileDialog.getOpenFileName(self, self.open_file_caption,
            os.getcwd(), self.open_file_filter)
        if fn:
            self.updateFileList([fn])

    def onFileListIndexChanged(self, index):
        """
        Callback for file selection.

        @param index[int]: The index of the selected item.
        """
        file_name = str(self.file_list.itemData(index))
        self.loadFile.emit(file_name)
