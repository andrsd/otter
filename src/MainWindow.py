import os
import io
import yaml
from globals import *
from PyQt5 import QtWidgets, QtCore
from MenuBar import MenuBar
from AboutDialog import AboutDialog
from ProjectTypeDialog import ProjectTypeDialog
from RecentFilesTab import RecentFilesTab
from TemplatesTab import TemplatesTab

"""
Main window
"""
class MainWindow(QtWidgets.QMainWindow):
    MAX_RECENT_FILES = 10

    def __init__(self):
        super(MainWindow, self).__init__()
        self.about_dlg = None
        self.result_window = None
        self.params_window = None
        self.plugin = None
        self.plugin_dir = None
        self.recent_files = []

        self.project_type_dlg = ProjectTypeDialog(self)

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.CustomizeWindowHint)

        self.readSettings()

        self.setupWidgets()
        self.setupMenuBar()

        self.setFixedHeight(475)
        self.setFixedWidth(750)

        self.updateMenuBar()

        self.project_type_dlg.finished.connect(self.onCreateProject)

    def setPluginsDir(self, dir):
        self.project_type_dlg.plugins_dir = dir

    def loadPlugins(self):
        self.project_type_dlg.findPlugins()
        self.project_type_dlg.addProjectTypes()
        self.project_type_dlg.updateControls()

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

        self.version = QtWidgets.QLabel("Version " + str(VERSION))
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
        self.menubar = MenuBar(self)

        fileMenu = self.menubar.addMenu("File")
        self._new_action = fileMenu.addAction("New", self.onNewFile, "Ctrl+N")
        self._open_action = fileMenu.addAction("Open", self.onOpenFile, "Ctrl+O")
        self._recent_menu = fileMenu.addMenu("Open Recent")
        self.buildRecentFilesMenu()
        fileMenu.addSeparator()
        self._close_action = fileMenu.addAction("Close", self.onCloseFile, "Ctrl+W")
        self._save_action = fileMenu.addAction("Save", self.onSaveFile, "Ctrl+S")
        self._save_as_action = fileMenu.addAction("Save As...", self.onSaveFileAs, "Ctrl+Shift+S")

        # The "About" item is fine here, since we assume Mac and that will place the itme into different submenu
        # but this will need to be fixed for linux and windows
        fileMenu.addSeparator()
        self._about_box_action = fileMenu.addAction("About", self.onAbout)

        self._windowMenu = self.menubar.addMenu("Window")
        self._minimize = self._windowMenu.addAction("Minimize", self.onMinimize, "Ctrl+M")
        self._windowMenu.addSeparator()
        self._bring_all_to_front = self._windowMenu.addAction("Bring All to Front", self.onBringAllToFront)

        self._windowMenu.addSeparator()
        self._show_main_window = self._windowMenu.addAction("Otter", self.onShowMainWindow)
        self._show_main_window.setCheckable(True)

        self._action_group_windows = QtWidgets.QActionGroup(self)
        self._action_group_windows.addAction(self._show_main_window)

        self.setMenuBar(self.menubar)

    def updateMenuBar(self):
        qapp = QtWidgets.QApplication.instance()
        active_window = qapp.activeWindow()
        if active_window == self:
            self._show_main_window.setChecked(True)

        have_file = self.plugin != None
        if have_file:
            self.plugin.updateMenuBar()
            self.plugin.setWindowVisible(True)

        self._show_main_window.setVisible(not have_file)
        self._save_action.setEnabled(have_file)
        self._save_as_action.setEnabled(have_file)
        self._close_action.setEnabled(have_file)

    def openFile(self, file_name):
        yml = self.readYml(file_name)
        if "type" in yml:
            self.plugin = self.project_type_dlg.getPluginByType(yml["type"])
            self.plugin.create()
            self.plugin.setupFromYml(yml)
            self.hide()
            self.updateMenuBar()
            self.addToRecentFiles(file_name)
        else:
            mb = QtWidgets.QMessageBox.information(
                self,
                "Information",
                "Failed to open '{}'.".format(file_name))

    def onNewFile(self):
        self.project_type_dlg.open()

    def onCreateProject(self):
        if self.project_type_dlg.result() == QtWidgets.QDialog.Accepted:
            self.plugin = self.project_type_dlg.plugin
            self.plugin.create()
            self.hide()
            self.updateMenuBar()

    def onOpenFile(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        if file_name[0]:
            self.openFile(file_name[0])

    def onCloseFile(self):
        if self.plugin != None:
            self.plugin.close()
            self.plugin.showMenu(False)
            self.show()
            self.plugin = None

        self.updateMenuBar()

    def onSaveFile(self):
        if self.plugin == None:
            return

        if self.plugin.getFileName() == None:
            file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
            if file_name[0]:
                self.writeYml(file_name[0])
            else:
                return
        else:
            self.writeYml(file_name[0])

    def onSaveFileAs(self):
        if self.plugin == None:
            return

        file_name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File As')
        if file_name[0]:
            self.writeYml(file_name[0])

    def onAbout(self):
        if self.about_dlg == None:
            self.about_dlg = AboutDialog(self)
        self.about_dlg.show()

    def onMinimize(self):
        if self.plugin != None:
            self.plugin.minimize()
        else:
            self.showMinimized()

    def onBringAllToFront(self):
        if self.plugin != None:
            self.plugin.bringAllToFront()
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

    def closeEvent(self, event):
        self.writeSettings()
        event.accept()

    def readYml(self, file_name):
        with open(file_name, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                return None

    def writeYml(self, file_name):
        data = {
            "type": self.plugin.__class__.__name__,
            "params": self.plugin.params()
        }
        with io.open(file_name, 'w', encoding = 'utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style = False, allow_unicode = True)
            self.plugin.setFileName(file_name)

    def writeSettings(self):
        settings = QtCore.QSettings()

        settings.beginGroup("MainWindow")
        settings.setValue("recentFiles", self.recent_files)
        settings.endGroup()

    def readSettings(self):
        settings = QtCore.QSettings()

        settings.beginGroup("MainWindow")
        self.recent_files = settings.value("recentFiles", [])
        settings.endGroup()

    def buildRecentFilesMenu(self):
        self._recent_menu.clear()
        if len(self.recent_files) > 0:
            for f in reversed(self.recent_files):
                path, file_name = os.path.split(f)
                action = self._recent_menu.addAction(file_name, self.onOpenRecentFile)
                action.setData(f)
            self._recent_menu.addSeparator()
        self._clear_recent_file = self._recent_menu.addAction("Clear Menu", self.onClearRecentFiles)

    def addToRecentFiles(self, file_name):
        self.recent_files = [f for f in self.recent_files if f != file_name]
        self.recent_files.append(file_name)
        if len(self.recent_files) > self.MAX_RECENT_FILES:
            del self.recent_files[0]
        self.buildRecentFilesMenu()
        self.recent_tab.addFileItem(file_name)

    def onOpenRecentFile(self):
        action = self.sender()
        file_name = action.data()
        self.openFile(file_name)

    def onClearRecentFiles(self):
        self.recent_files = []
        self.buildRecentFilesMenu()
        self.recent_tab.clear()
