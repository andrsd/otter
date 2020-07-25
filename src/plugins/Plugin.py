from PyQt5 import QtCore, QtWidgets, QtGui

class Plugin:

    def __init__(self, parent):
        self.file = None
        self.parent = parent
        self.windows = []
        self._show_window = {}
        self.file = QtCore.QFile()

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
        pass

    def onCloseFile(self):
        self.file = None
        for (window, action) in self._show_window.items():
            window.close()
            self.parent._action_group_windows.removeAction(action)
        self.windows = []
        self._show_window = {}

    def onMinimize(self):
        for window in self.windows:
            window.showMinimized()

    def onBringAllToFront(self):
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

    def updateMenuBar(self):
        qapp = QtWidgets.QApplication.instance()
        active_window = qapp.activeWindow()
        if active_window in self._show_window:
            self._show_window[active_window].setChecked(True)
