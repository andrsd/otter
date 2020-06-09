import os
from PyQt5 import QtWidgets, QtCore
from AboutDialog import AboutDialog
from RecentFilesTab import RecentFilesTab
from TemplatesTab import TemplatesTab
from ResultWindow import ResultWindow
from ParamsWindow import ParamsWindow

"""
Main window
"""
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.AboutDlg = None
        self.result_window = None
        self.params_window = None
        self.file = None

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.CustomizeWindowHint)

        self.setupWidgets()
        self.setupMenuBar()

        self.setFixedHeight(475)
        self.setFixedWidth(750)

        self.updateMenuBar()

    def setupWidgets(self):
        w = QtWidgets.QWidget(self)
        w.setContentsMargins(0, 0, 0 ,0)
        layout = QtWidgets.QHBoxLayout()

        self.LeftPane = QtWidgets.QWidget(self)
        self.LeftPane.setFixedWidth(220)

        left_layout = QtWidgets.QVBoxLayout()

        icon = QtWidgets.QApplication.windowIcon()
        self.Icon = QtWidgets.QLabel()
        self.Icon.setPixmap(icon.pixmap(96, 96))
        left_layout.addWidget(self.Icon, 0, QtCore.Qt.AlignHCenter)

        self.Title = QtWidgets.QLabel("Otter")
        font = self.Title.font()
        font.setBold(True)
        font.setPointSize(int(1.2 * font.pointSize()))
        self.Title.setFont(font)
        self.Title.setAlignment(QtCore.Qt.AlignHCenter)
        left_layout.addWidget(self.Title)

        left_layout.addStretch()

        self.LeftPane.setLayout(left_layout)

        layout.addWidget(self.LeftPane)

        self.RightPane = QtWidgets.QTabWidget(self)

        self.RecentTab = RecentFilesTab(self)
        self.RightPane.addTab(self.RecentTab, "Recent")

        self.TemplateTab = TemplatesTab(self)
        self.RightPane.addTab(self.TemplateTab, "Templates")

        layout.addWidget(self.RightPane)

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

        windowMenu = menubar.addMenu("Window")
        self._minimize = windowMenu.addAction("Minimize", self.onMinimize, "Ctrl+M")
        windowMenu.addSeparator()
        self._bring_all_to_front = windowMenu.addAction("Bring All to Front", self.onBringAllToFront)

    def updateMenuBar(self):
        have_file = self.file != None
        self._save_action.setEnabled(have_file)
        self._close_action.setEnabled(have_file)
        self._render_action.setEnabled(have_file)

    def onNewFile(self):
        if self.params_window == None:
            self.params_window = ParamsWindow(self)
        if self.result_window == None:
            self.result_window = ResultWindow(self)

        self.hide()
        self.result_window.show()
        self.params_window.show()

        self.file = QtCore.QFile()
        self.updateMenuBar()

    def onOpenFile(self):
        pass

    def onCloseFile(self):
        if self.file != None:
            self.result_window.close()
            self.params_window.close()

            self.result_window = None
            self.params_window = None
            self.file = None
            self.show()

        self.updateMenuBar()

    def onSaveFile(self):
        pass

    def onRender(self):
        pass

    def onAbout(self):
        if self.AboutDlg == None:
            self.AboutDlg = AboutDialog(self)
        self.AboutDlg.show()

    def onMinimize(self):
        if self.file != None:
            self.result_window.showMinimized()
            self.params_window.showMinimized()
        else:
            self.showMinimized()

    def onBringAllToFront(self):
        if self.file != None:
            self.result_window.showNormal()
            self.params_window.showNormal()
        else:
            self.showNormal()
