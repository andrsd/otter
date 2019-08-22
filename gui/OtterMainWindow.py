#!/usr/bin/env python2

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMenu, QTabWidget, QFileDialog
from PyQt5.QtCore import QFile, QTextStream
from OtterObjectTypeTab import OtterObjectTypeTab
from OtterViewportsTab import OtterViewportsTab
from OtterColorbarsTab import OtterColorbarsTab
from OtterAnnotationsTab import OtterAnnotationsTab
import os
import otter

class OtterMainWindow(QMainWindow):

    def __init__(self):
        super(OtterMainWindow, self).__init__()
        self.file = QFile()
        self.modified = False
        self.setupMenuBar()
        self.setupWidgets()
        self.setTitle()
        self.setMinimumSize(350, 700)

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
        self.tabType.modified.connect(self.setModified)
        self.ctlObjType.addTab(self.tabType, "Type")

        self.tabViewports = OtterViewportsTab(self, self.tabType.chiggerWindow)
        self.tabViewports.modified.connect(self.setModified)
        self.ctlObjType.addTab(self.tabViewports, self.tabViewports.name())

        self.tabColorBars = OtterColorbarsTab(self, self.tabType.chiggerWindow)
        self.tabColorBars.modified.connect(self.setModified)
        self.ctlObjType.addTab(self.tabColorBars, self.tabColorBars.name())

        self.tabAnnotations = OtterAnnotationsTab(self, self.tabType.chiggerWindow)
        self.tabAnnotations.modified.connect(self.setModified)
        self.ctlObjType.addTab(self.tabAnnotations, self.tabAnnotations.name())

        layout.addWidget(self.ctlObjType)

        w.setLayout(layout)
        self.setCentralWidget(w)

    def setModified(self):
        self.modified = True
        self.setTitle()

    def setTitle(self):
        if self.file.fileName():
            title = os.path.basename(self.file.fileName())
            if self.modified:
                title += " *"
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
            else:
                return
        self.saveIntoFile()
        self.modified = False
        self.setTitle()

    def onSaveInputFileAs(self):
        file_name = QFileDialog.getSaveFileName(self, 'Save File As')
        if file_name[0]:
            self.file.setFileName(file_name[0])
            self.saveIntoFile()
            self.modified = False
            self.setTitle()

    def saveIntoFile(self):
        if self.file.open(QFile.WriteOnly | QFile.Text):
            out = QTextStream(self.file)

            out << "#!/usr/bin/env python2\n"
            out << "\n"
            out << "import otter\n"
            out << "import numpy\n"
            if otter.HAVE_RELAP7:
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
