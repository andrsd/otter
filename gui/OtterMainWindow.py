#!/usr/bin/env python2

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMenu, QTabWidget, QFileDialog
from PyQt5.QtCore import QFile, QTextStream
from OtterObjectTypeTab import OtterObjectTypeTab
from OtterViewportsTab import OtterViewportsTab
from OtterColorbarsTab import OtterColorbarsTab
from OtterAnnotationsTab import OtterAnnotationsTab
import os

class OtterMainWindow(QMainWindow):

    def __init__(self):
        super(OtterMainWindow, self).__init__()
        self.file = QFile()
        self.setupMenuBar()
        self.setupWidgets()
        self.setTitle()
        self.setMinimumSize(300, 400)

    def setupMenuBar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        self._new_action = fileMenu.addAction("New", self.onNewInputFile, "Ctrl+N")
        self._open_action = fileMenu.addAction("Open", self.onOpenInputFile, "Ctrl+O")
        fileMenu.addSeparator()
        self._save_action = fileMenu.addAction("Save", self.onSaveInputFile, "Ctrl+S")
        self._save_as_action = fileMenu.addAction("Save As", self.onSaveInputFileAs, "Ctrl+Shift+S")

    def setupWidgets(self):
        w = QWidget(self)
        layout = QVBoxLayout()

        self.ctlObjType = QTabWidget(self)

        self.tabType = OtterObjectTypeTab(self)
        self.ctlObjType.addTab(self.tabType, "Type")

        self.tabViewports = OtterViewportsTab(self)
        self.ctlObjType.addTab(self.tabViewports, self.tabViewports.name())

        self.tabColorBars = OtterColorbarsTab(self)
        self.ctlObjType.addTab(self.tabColorBars, self.tabColorBars.name())

        self.tabAnnotations = OtterAnnotationsTab(self)
        self.ctlObjType.addTab(self.tabAnnotations, self.tabAnnotations.name())

        layout.addWidget(self.ctlObjType)

        w.setLayout(layout)
        self.setCentralWidget(w)

    def setTitle(self):
        if self.file.fileName():
            title = os.path.basename(self.file.fileName())
        else:
            title = "Untitled"
        self.setWindowTitle(title)

    def onNewInputFile(self):
        pass

    def onOpenInputFile(self):
        pass

    def onSaveInputFile(self):
        if self.file.fileName() == "":
            file_name = QFileDialog.getSaveFileName(self, 'Save File')
            if file_name[0]:
                self.file.setFileName(file_name[0])
                self.setTitle()
            else:
                return
        self.saveIntoFile()

    def onSaveInputFileAs(self):
        file_name = QFileDialog.getSaveFileName(self, 'Save File As')
        if file_name[0]:
            self.file.setFileName(file_name[0])
            self.setTitle()
            self.saveIntoFile()

    def saveIntoFile(self):
        if self.file.open(QFile.WriteOnly | QFile.Text):
            out = QTextStream(self.file)

            out << "#!/usr/bin/env python2\n"
            out << "\n"
            out << "import otter\n"
            out << "import numpy\n"
            out << "import relap7\n"
            out << "\n"
            out << self.tabViewports.toText()
            out << "\n"
            out << self.tabColorBars.toText()
            out << "\n"
            out << self.tabAnnotations.toText()
            out << "\n"
            out << self.tabType.toText()

            self.file.flush()
            self.file.close()
