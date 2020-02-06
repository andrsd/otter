import os
import sys
import importlib
from PyQt5 import QtWidgets, QtCore
from gui.OtterResultWindow import OtterResultWindow
from gui.OtterMediaTab import OtterMediaTab
from gui.OtterViewportsTab import OtterViewportsTab
from gui.OtterColorbarsTab import OtterColorbarsTab
from gui.OtterAnnotationsTab import OtterAnnotationsTab
from gui.OtterAboutDialog import OtterAboutDialog
from otter import config

class OtterMainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(OtterMainWindow, self).__init__()
        self.file = QtCore.QFile()
        self.modified = False
        self.windowResult = None
        self.ctlObjType = None
        self._about_dlg = None

        self.setupWidgets()
        self.setupMenuBar()
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
        self._about_box_action = fileMenu.addAction("About", self.onAboutApplication)

        # Adding '\u200C' so that Mac OS X does not add items I do not want in View menu
        viewMenu = menubar.addMenu("View" + '\u200C')
        self._media_tab_action = viewMenu.addAction("Media", lambda: self.onActivateTab(0), "Ctrl+1")
        self._media_tab_action.setCheckable(True)
        self._viewports_tab_action = viewMenu.addAction("Viewports", lambda: self.onActivateTab(1), "Ctrl+2")
        self._viewports_tab_action.setCheckable(True)
        self._colorbars_tab_action = viewMenu.addAction("Color bars", lambda: self.onActivateTab(2), "Ctrl+3")
        self._colorbars_tab_action.setCheckable(True)
        self._annotations_tab_action = viewMenu.addAction("Annotations", lambda: self.onActivateTab(3), "Ctrl+4")
        self._annotations_tab_action.setCheckable(True)

        self._tab_group_windows = QtWidgets.QActionGroup(self)
        self._tab_group_windows.addAction(self._media_tab_action)
        self._tab_group_windows.addAction(self._viewports_tab_action)
        self._tab_group_windows.addAction(self._colorbars_tab_action)
        self._tab_group_windows.addAction(self._annotations_tab_action)

        windowMenu = menubar.addMenu("Window")
        self._minimize = windowMenu.addAction("Minimize", self.onMinimize, "Ctrl+M")
        windowMenu.addSeparator()
        self._bring_all_to_front = windowMenu.addAction("Bring All to Front", self.onBringAllToFront)
        windowMenu.addSeparator()
        self._main_window = windowMenu.addAction("Main window - " + self.title(), self.onShowMainWindow)
        self._main_window.setCheckable(True)
        self._result_window = windowMenu.addAction(self.windowResult.windowTitle(), self.onShowChiggerWindow)
        self._result_window.setCheckable(True)

        self._action_group_windows = QtWidgets.QActionGroup(self)
        self._action_group_windows.addAction(self._main_window)
        self._action_group_windows.addAction(self._result_window)

    def updateMenuBar(self):
        qapp = QtWidgets.QApplication.instance()
        active_window = qapp.activeWindow()
        if active_window == self:
            self._main_window.setChecked(True)
        elif active_window == self.windowResult:
            self._result_window.setChecked(True)

        if self.ctlObjType != None:
            tabs = [
                self._media_tab_action,
                self._viewports_tab_action,
                self._colorbars_tab_action,
                self._annotations_tab_action
            ]
            idx = self.ctlObjType.currentIndex()
            tabs[idx].setChecked(True)

    def setupWidgets(self):
        self.windowResult = OtterResultWindow(self)

        w = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout()

        self.ctlObjType = QtWidgets.QTabWidget(self)

        self.tabMedia = OtterMediaTab(self, self.windowResult)
        self.tabMedia.modified.connect(self.setModified)
        self.tabMedia.timeChanged.connect(self.onTimeChanged)
        self.tabMedia.timeUnitChanged.connect(self.onTimeUnitChanged)
        self.ctlObjType.addTab(self.tabMedia, "Media")

        self.tabViewports = OtterViewportsTab(self, self.windowResult)
        self.tabViewports.modified.connect(self.setModified)
        self.tabViewports.resultAdded.connect(self.onResultAdded)

        self.ctlObjType.addTab(self.tabViewports, self.tabViewports.name())

        self.tabColorBars = OtterColorbarsTab(self, self.windowResult)
        self.tabColorBars.modified.connect(self.setModified)
        self.ctlObjType.addTab(self.tabColorBars, self.tabColorBars.name())

        self.tabAnnotations = OtterAnnotationsTab(self, self.windowResult)
        self.tabAnnotations.modified.connect(self.setModified)
        self.ctlObjType.addTab(self.tabAnnotations, self.tabAnnotations.name())

        layout.addWidget(self.ctlObjType)
        self.ctlObjType.currentChanged.connect(self.updateMenuBar)

        w.setLayout(layout)
        self.setCentralWidget(w)

        qapp = QtWidgets.QApplication.instance()
        self.windowResult.setGeometry(
            QtWidgets.QStyle.alignedRect(QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter, self.windowResult.size(), qapp.desktop().availableGeometry()))
        self.windowResult.show()

    def setModified(self):
        self.modified = True
        self.setTitle()

    def onTimeChanged(self, time):
        self.tabViewports.onTimeChanged(time)
        self.tabAnnotations.onTimeChanged(time)

    def onTimeUnitChanged(self, time_unit):
        self.tabAnnotations.onTimeUnitChanged(time_unit)

    def onResultAdded(self):
        self.tabColorBars.onResultAdded()

    def title(self):
        if self.file.fileName():
            title = os.path.basename(self.file.fileName())
        else:
            title = "Untitled"
        if self.modified:
            title += " *"
        return title

    def exodusResults(self):
        return self.tabViewports.exodusResults;

    def setTitle(self):
        self.setWindowTitle(self.title())

    def onNewInputFile(self):
        pass

    def onOpenInputFile(self):
        # TODO: save file if there are unsaved changes

        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        if file_name[0]:
            self.loadFromFile(file_name[0])

    def onSaveInputFile(self):
        if self.file.fileName() == "":
            file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
            if file_name[0]:
                self.saveToFile(file_name[0])
            else:
                # what error state could this be?
                return
        else:
            self.saveToFile(self.file.fileName())

    def onSaveInputFileAs(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File As')
        if file_name[0]:
            self.saveToFile(file_name[0])

    def onMinimize(self):
        qapp = QtWidgets.QApplication.instance()
        qapp.activeWindow().showMinimized()

    def onBringAllToFront(self):
        self.windowResult.showNormal()
        self.showNormal()

    def onShowMainWindow(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def onShowChiggerWindow(self):
        self.windowResult.showNormal()
        self.windowResult.activateWindow()
        self.windowResult.raise_()

    def onActivateTab(self, tab):
        self.ctlObjType.setCurrentIndex(tab)

    def onAboutApplication(self):
        if self._about_dlg == None:
            self._about_dlg = OtterAboutDialog(self)
        self._about_dlg.show()

    def event(self, e):
        if (e.type() == QtCore.QEvent.WindowActivate):
            self.updateMenuBar()
        return super(OtterMainWindow, self).event(e);

    def saveToFile(self, file_name):
        file = QtCore.QFile(file_name)
        if file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            out = QtCore.QTextStream(file)

            out << "#!/usr/bin/env python\n"
            out << "\n"
            out << "import otter\n"
            out << "import numpy\n"
            if config.HAVE_RELAP7:
                out << "import relap7\n"
            out << "\n"
            out << self.tabViewports.toText()
            out << "\n"
            out << self.tabColorBars.toText()
            out << "\n"
            out << self.tabAnnotations.toText()
            out << "\n"
            out << self.tabMedia.toText()

            file.flush()
            file.close()

            self.file.setFileName(file_name)
            self.modified = False
            self.setTitle()
        else:
            mb = QtWidgets.QMessageBox.information(
                self,
                "Information",
                "Failed to save '{}'.".format(file_name))

    def loadFromFile(self, file_name):
        file = QtCore.QFile(file_name)
        if file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            file.close()

            dir = os.path.dirname(file_name)
            module_name = os.path.splitext(os.path.basename(file_name))[0]
            sys.path.append(dir)
            temp = importlib.__import__(module_name, None, None, ['viewports', 'colorbars', 'annotations', 'image', 'movie'])
            sys.path.remove(dir)

            if hasattr(temp, 'movie'):
                self.tabMedia.selectObjectType("Movie")
                self.tabMedia.setObjectParams(temp.movie)
            elif hasattr(temp, 'image') != None:
                self.tabMedia.selectObjectType("Image")
                self.tabMedia.setObjectParams(temp.image)
            else:
                mb = QtWidgets.QMessageBox.information(
                    self,
                    "Information",
                    "Did not find 'image' or 'movie' in your otter script.  Nothing was loaded.")
                # TODO: set defaults everywhere (?)
                return

            self.tabViewports.populate(temp.viewports)
            self.tabColorBars.populate(temp.colorbars)
            self.tabAnnotations.populate(temp.annotations)

            self.file.setFileName(file_name)
            self.modified = False
            self.setTitle()
        else:
            mb = QtWidgets.QMessageBox.information(
                self,
                "Information",
                "Failed to open '{}'.".format(file_name))
