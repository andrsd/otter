from PyQt5 import QtCore, QtWidgets, QtGui

class Plugin:

    def __init__(self, parent):
        self.parent = parent
        self.file_name = None
        self.windows = []
        self.menus = []
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

    def getFileName(self):
        return self.file_name

    def setFileName(self, file_name):
        self.file_name = file_name

    def params(self):
        return []

    def registerWindow(self, window):
        self.windows.append(window)

        action = self.parent._windowMenu.addAction(window.windowTitle(), lambda : self.onShowWindow(window))
        action.setCheckable(True)
        self.parent._action_group_windows.addAction(action)
        self._show_window[window] = action

    def create(self):
        self.showMenu(True)
        self.onCreate()
        self.showWindow()

    def showMenu(self, state):
        for mnu in self.menus:
            mnu.menuAction().setVisible(state)
        for act in self.actions:
            act.setVisible(state)

    def close(self):
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
        for mnu in self.menus:
            mnu.menuAction().setVisible(visible)

    def onShowWindow(self, window):
        window.showNormal()
        window.activateWindow()
        window.raise_()
        self.updateMenuBar()

    def addMenu(self, menu, text):
        new_menu = menu.addMenu(text)
        new_menu.menuAction().setVisible(False)
        self.menus.append(new_menu)
        return new_menu

    def addMenuSeparator(self, menu):
        action = menu.addSeparator()
        action.setVisible(False)
        self.actions.append(action)
        return action

    def addMenuAction(self, menu, string, method, keysequece = 0):
        action = menu.addAction(string, method, keysequece)
        action.setVisible(False)
        self.actions.append(action)
        return action

    def updateMenuBar(self):
        qapp = QtWidgets.QApplication.instance()
        active_window = qapp.activeWindow()
        if active_window in self._show_window:
            self._show_window[active_window].setChecked(True)

    def setupFromYml(self, yml):
        pass
