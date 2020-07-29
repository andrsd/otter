from PyQt5 import QtCore, QtWidgets, QtGui

class Plugin:

    def __init__(self, parent):
        self.file = None
        self.parent = parent
        self.windows = []
        self.actions = []
        self._show_window = {}
        self.menubar = parent.menubar

    """
    Return the name of the plugin (used in the GUI)
    """
    @staticmethod
    def name():
        return None

    """
    Return the icon for this plugin (as QIcon)
    """
    @staticmethod
    def icon():
        return None

    def registerWindow(self, window):
        self.windows.append(window)

        action = self.parent._windowMenu.addAction(window.windowTitle(), lambda : self.onShowWindow(window))
        action.setCheckable(True)
        self.parent._action_group_windows.addAction(action)
        self._show_window[window] = action

    def create(self):
        self.file = QtCore.QFile()
        self.showMenu(True)
        self.onCreate()
        self.showWindow()

    def showMenu(self, state):
        for act in self.actions:
            act.setVisible(state)

    def closeFile(self):
        self.file = None
        for (window, action) in self._show_window.items():
            window.close()
            self.parent._action_group_windows.removeAction(action)
        self.windows = []
        self._show_window = {}

    def minimize(self):
        for window in self.windows:
            window.showMinimized()

    def bringAllToFront(self):
        for window in self.windows:
            window.showNormal()

    def showWindow(self):
        for window in self.windows:
            window.show()

    def setWindowVisible(self, visible):
        for (window, action) in self._show_window.items():
            action.setVisible(visible)

    def onShowWindow(self, window):
        window.showNormal()
        window.activateWindow()
        window.raise_()
        self.updateMenuBar()

    def addMenuSeparator(self, menu):
        action = menu.addSeparator()
        action.setVisible(False)
        self.actions.append(action)

    def addMenuAction(self, menu, string, method, keysequece = 0):
        action = menu.addAction(string, method, keysequece)
        action.setVisible(False)
        self.actions.append(action)

    def updateMenuBar(self):
        qapp = QtWidgets.QApplication.instance()
        active_window = qapp.activeWindow()
        if active_window in self._show_window:
            self._show_window[active_window].setChecked(True)
