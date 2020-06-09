import os
from PyQt5 import QtWidgets, QtCore
from AboutDialog import AboutDialog
from RecentFilesTab import RecentFilesTab
from TemplatesTab import TemplatesTab

"""
Main window
"""
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.AboutDlg = None

        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.CustomizeWindowHint)

        self.setupWidgets()
        self.setupMenuBar()

        self.setFixedHeight(475)
        self.setFixedWidth(750)

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

    def onNewFile(self):
        pass

    def onOpenFile(self):
        pass

    def onCloseFile(self):
        pass

    def onSaveFile(self):
        pass

    def onRender(self):
        pass

    def onAbout(self):
        if self.AboutDlg == None:
            self.AboutDlg = AboutDialog(self)
        self.AboutDlg.show()

    def onMinimize(self):
        qapp = QtWidgets.QApplication.instance()
        qapp.activeWindow().showMinimized()

    def onBringAllToFront(self):
        pass
