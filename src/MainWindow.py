import os
import globs
from PyQt5 import QtWidgets, QtCore
from AboutDialog import AboutDialog
from ProjectTypeDialog import ProjectTypeDialog
from RecentFilesTab import RecentFilesTab
from TemplatesTab import TemplatesTab

"""
Main window
"""
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.about_dlg = None
        self.result_window = None
        self.params_window = None
        self.plugin = None

        self.project_type_dlg = ProjectTypeDialog(self)

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.CustomizeWindowHint)

        self.setupWidgets()
        self.setupMenuBar()

        self.setFixedHeight(475)
        self.setFixedWidth(750)

        self.updateMenuBar()

        self.project_type_dlg.finished.connect(self.onCreateProject)

    def setupWidgets(self):
        w = QtWidgets.QWidget(self)
        w.setContentsMargins(0, 0, 0 ,0)
        layout = QtWidgets.QHBoxLayout()

        self.left_pane = QtWidgets.QWidget(self)
        self.left_pane.setFixedWidth(220)

        left_layout = QtWidgets.QVBoxLayout()

        icon = QtWidgets.QApplication.windowIcon()
        self.icon = QtWidgets.QLabel()
        self.icon.setPixmap(icon.pixmap(96, 96))
        left_layout.addWidget(self.icon, 0, QtCore.Qt.AlignHCenter)

        self.title = QtWidgets.QLabel("Otter")
        font = self.title.font()
        font.setBold(True)
        font.setPointSize(int(1.2 * font.pointSize()))
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignHCenter)
        left_layout.addWidget(self.title)

        self.version = QtWidgets.QLabel("Version " + str(globs.VERSION))
        font = self.version.font()
        font.setBold(True)
        font.setPointSize(int(0.9 * font.pointSize()))
        self.version.setFont(font)
        self.version.setStyleSheet("QLabel { color: #888; }")
        self.version.setAlignment(QtCore.Qt.AlignHCenter)
        left_layout.addWidget(self.version)

        left_layout.addStretch()

        self.left_pane.setLayout(left_layout)

        layout.addWidget(self.left_pane)

        self.right_pane = QtWidgets.QTabWidget(self)

        self.recent_tab = RecentFilesTab(self)
        self.right_pane.addTab(self.recent_tab, "Recent")

        self.template_tab = TemplatesTab(self)
        self.right_pane.addTab(self.template_tab, "Templates")

        layout.addWidget(self.right_pane)

        w.setLayout(layout)
        self.setCentralWidget(w)

    def setupMenuBar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        self._new_action = fileMenu.addAction("New", self.onNewFile, "Ctrl+N")
        self._open_action = fileMenu.addAction("Open", self.onOpenFile, "Ctrl+O")
        fileMenu.addSeparator()
        self._close_action = fileMenu.addAction("Close", self.onCloseFile, "Ctrl+W")
        self._save_action = fileMenu.addAction("Save", self.onSaveFile, "Ctrl+S")
        fileMenu.addSeparator()
        self._render_action = fileMenu.addAction("Render", self.onRender, "Ctrl+Shift+R")
        fileMenu.addSeparator()
        self._about_box_action = fileMenu.addAction("About", self.onAbout)

        self._windowMenu = menubar.addMenu("Window")
        self._minimize = self._windowMenu.addAction("Minimize", self.onMinimize, "Ctrl+M")
        self._windowMenu.addSeparator()
        self._bring_all_to_front = self._windowMenu.addAction("Bring All to Front", self.onBringAllToFront)

        self._windowMenu.addSeparator()
        self._show_main_window = self._windowMenu.addAction("Otter", self.onShowMainWindow)
        self._show_main_window.setCheckable(True)

        self._action_group_windows = QtWidgets.QActionGroup(self)
        self._action_group_windows.addAction(self._show_main_window)

    def updateMenuBar(self):
        qapp = QtWidgets.QApplication.instance()
        active_window = qapp.activeWindow()
        if active_window == self:
            self._show_main_window.setChecked(True)

        if self.plugin != None:
            have_file = self.plugin.file != None
            if have_file:
                self.plugin.updateMenuBar()
                self.plugin.setWindowVisible(have_file)
            self._show_main_window.setVisible(not have_file)
        else:
            have_file = False
            self._show_main_window.setVisible(True)

        self._save_action.setEnabled(have_file)
        self._close_action.setEnabled(have_file)
        self._render_action.setEnabled(have_file)

    def onNewFile(self):
        self.project_type_dlg.open()

    def onCreateProject(self):
        if self.project_type_dlg.result() == QtWidgets.QDialog.Accepted:
            self.plugin = self.project_type_dlg.plugin(self)
            self.plugin.create()
            self.hide()
            self.plugin.showWindow()
            self.updateMenuBar()

    def onOpenFile(self):
        pass

    def onCloseFile(self):
        if self.plugin != None:
            self.plugin.onCloseFile()
            self.show()

        self.updateMenuBar()

    def onSaveFile(self):
        pass

    def onRender(self):
        pass

    def onAbout(self):
        if self.about_dlg == None:
            self.about_dlg = AboutDialog(self)
        self.about_dlg.show()

    def onMinimize(self):
        if self.plugin.file != None:
            self.plugin.onMinimize()
        else:
            self.showMinimized()

    def onBringAllToFront(self):
        if self.plugin.file != None:
            self.plugin.onBringAllToFront()
        else:
            self.showNormal()

    def onShowMainWindow(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()
        self.updateMenuBar()

    def event(self, e):
        if (e.type() == QtCore.QEvent.WindowActivate):
            self.updateMenuBar()
        return super(MainWindow, self).event(e);
