#!/usr/bin/env python2

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMenu, QTabWidget
from OtterObjectTypeTab import OtterObjectTypeTab
from OtterViewportsTab import OtterViewportsTab
from OtterColorbarsTab import OtterColorbarsTab
from OtterAnnotationsTab import OtterAnnotationsTab

class OtterMainWindow(QMainWindow):

    def __init__(self):
        super(OtterMainWindow, self).__init__()
        self.setupMenuBar()
        self.setupWidgets()
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

    def onNewInputFile(self):
        pass

    def onOpenInputFile(self):
        pass

    def onSaveInputFile(self):
        pass

    def onSaveInputFileAs(self):
        pass
