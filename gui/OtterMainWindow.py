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
        self.WindowResult = None
        self.ObjectType = None
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
        fileMenu.addSeparator()
        self._render_action = fileMenu.addAction("Render", self.onRender, "Ctrl+Shift+R")
        fileMenu.addSeparator()
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
        self._result_window = windowMenu.addAction(self.WindowResult.windowTitle(), self.onShowChiggerWindow)
        self._result_window.setCheckable(True)

        self._action_group_windows = QtWidgets.QActionGroup(self)
        self._action_group_windows.addAction(self._main_window)
        self._action_group_windows.addAction(self._result_window)

    def updateMenuBar(self):
        qapp = QtWidgets.QApplication.instance()
        active_window = qapp.activeWindow()
        if active_window == self:
            self._main_window.setChecked(True)
        elif active_window == self.WindowResult:
            self._result_window.setChecked(True)

        if self.ObjectType != None:
            tabs = [
                self._media_tab_action,
                self._viewports_tab_action,
                self._colorbars_tab_action,
                self._annotations_tab_action
            ]
            idx = self.ObjectType.currentIndex()
            tabs[idx].setChecked(True)

        if self.MediaTab != None:
            idx = self.MediaTab.ctlType.currentIndex()
            if idx == OtterMediaTab.IDX_IMAGE:
                args = self.MediaTab.args()
                self._render_action.setEnabled('output' in args)
            elif idx == OtterMediaTab.IDX_MOVIE:
                args = self.MediaTab.args()
                self._render_action.setEnabled('file' in args)

    def setupWidgets(self):
        self.WindowResult = OtterResultWindow(self)

        w = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout()

        self.ObjectType = QtWidgets.QTabWidget(self)

        self.MediaTab = OtterMediaTab(self, self.WindowResult)
        self.MediaTab.modified.connect(self.setModified)
        self.MediaTab.timeChanged.connect(self.onTimeChanged)
        self.MediaTab.timeUnitChanged.connect(self.onTimeUnitChanged)
        self.ObjectType.addTab(self.MediaTab, "Media")

        self.ViewportsTab = OtterViewportsTab(self, self.WindowResult)
        self.ViewportsTab.modified.connect(self.setModified)
        self.ViewportsTab.resultAdded.connect(self.onResultAdded)

        self.ObjectType.addTab(self.ViewportsTab, self.ViewportsTab.name())

        self.ColorBarsTab = OtterColorbarsTab(self, self.WindowResult)
        self.ColorBarsTab.modified.connect(self.setModified)
        self.ObjectType.addTab(self.ColorBarsTab, self.ColorBarsTab.name())

        self.AnnotationsTab = OtterAnnotationsTab(self, self.WindowResult)
        self.AnnotationsTab.modified.connect(self.setModified)
        self.ObjectType.addTab(self.AnnotationsTab, self.AnnotationsTab.name())

        layout.addWidget(self.ObjectType)
        self.ObjectType.currentChanged.connect(self.updateMenuBar)

        w.setLayout(layout)
        self.setCentralWidget(w)

        qapp = QtWidgets.QApplication.instance()
        self.WindowResult.setGeometry(
            QtWidgets.QStyle.alignedRect(QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter, self.WindowResult.size(), qapp.desktop().availableGeometry()))
        self.WindowResult.show()

    def setModified(self):
        self.modified = True
        self.setTitle()
        self.updateMenuBar()

    def onTimeChanged(self, time):
        self.ViewportsTab.onTimeChanged(time)
        self.AnnotationsTab.onTimeChanged(time)

    def onTimeUnitChanged(self, time_unit):
        self.AnnotationsTab.onTimeUnitChanged(time_unit)

    def onResultAdded(self):
        self.ColorBarsTab.onResultAdded()

    def title(self):
        if self.file.fileName():
            title = os.path.basename(self.file.fileName())
        else:
            title = "Untitled"
        if self.modified:
            title += " *"
        return title

    def exodusResults(self):
        return self.ViewportsTab.exodusResults;

    def getChiggerObjects(self):
        objects = []
        objects.extend(self.tabViewports.getChiggerObjects())
        objects.extend(self.tabColorBars.getChiggerObjects())
        objects.extend(self.tabAnnotations.getChiggerObjects())
        return objects

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
        self.WindowResult.showNormal()
        self.showNormal()

    def onShowMainWindow(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def onShowChiggerWindow(self):
        self.WindowResult.showNormal()
        self.WindowResult.activateWindow()
        self.WindowResult.raise_()

    def onActivateTab(self, tab):
        self.ObjectType.setCurrentIndex(tab)

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
            out << self.ViewportsTab.toText()
            out << "\n"
            out << self.ColorBarsTab.toText()
            out << "\n"
            out << self.AnnotationsTab.toText()
            out << "\n"
            out << self.MediaTab.toText()

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
                self.MediaTab.selectObjectType("Movie")
                self.MediaTab.setObjectParams(temp.movie)
            elif hasattr(temp, 'image') != None:
                self.MediaTab.selectObjectType("Image")
                self.MediaTab.setObjectParams(temp.image)
            else:
                mb = QtWidgets.QMessageBox.information(
                    self,
                    "Information",
                    "Did not find 'image' or 'movie' in your otter script.  Nothing was loaded.")
                # TODO: set defaults everywhere (?)
                return

            self.ViewportsTab.populate(temp.viewports)
            self.ColorBarsTab.populate(temp.colorbars)
            self.AnnotationsTab.populate(temp.annotations)

            self.file.setFileName(file_name)
            self.modified = False
            self.setTitle()
        else:
            mb = QtWidgets.QMessageBox.information(
                self,
                "Information",
                "Failed to open '{}'.".format(file_name))

    def closeEvent(self, event):
        if self.modified:
            res = QtWidgets.QMessageBox.question(self,
                "Unsaved changes",
                "You have unsaved changes. Save?",
                QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                QtWidgets.QMessageBox.Yes)
            if res == QtWidgets.QMessageBox.Yes:
                self.onSaveInputFile()
                self.modified = False
                event.accept()
                QtWidgets.QApplication.quit()
            elif res == QtWidgets.QMessageBox.No:
                event.accept()
                QtWidgets.QApplication.quit()
            elif res == QtWidgets.QMessageBox.Cancel:
                event.ignore()
        else:
            event.accept()
            QtWidgets.QApplication.quit()

    def onRender(self):
        self.MediaTab.render()
