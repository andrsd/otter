"""
Plugin.py
"""

from PyQt5 import QtWidgets

class Plugin:
    """
    Base class for plug-ins
    """

    def __init__(self, parent):
        self.parent = parent
        self.file_name = None
        self.windows = []
        self.menus = []
        self.actions = []
        self._show_window = {}
        self.menubar = parent.menubar

    @staticmethod
    def name():
        """
        Return the name of the plugin (used in the GUI)
        """
        return None

    @staticmethod
    def icon():
        """
        Return the icon for this plugin (as QIcon)
        """
        return None

    def getFileName(self):
        """
        Get file name
        """
        return self.file_name

    def setFileName(self, file_name):
        """
        Set file name
        @param file_name File name
        """
        self.file_name = file_name

    def params(self):
        """
        Return parameters
        """
        # pylint: disable=no-self-use
        return []

    def registerWindow(self, window):
        """
        Call to register created window
        @param window[QWindow] Qt window
        """
        self.windows.append(window)

        action = self.parent.window_menu.addAction(window.windowTitle(),
            lambda : self.onShowWindow(window))
        action.setCheckable(True)
        self.parent.action_group_windows.addAction(action)
        self._show_window[window] = action

    def create(self):
        """
        Create the plugin
        """
        self.showMenu(True)
        self.onCreate()
        self.showWindow()

    def showMenu(self, state):
        """
        Show menu
        @param state[bool] True to show enabled, False for disabled
        """
        for mnu in self.menus:
            mnu.menuAction().setVisible(state)
        for act in self.actions:
            act.setVisible(state)

    def close(self):
        """
        Close the plugin
        """
        for (window, action) in self._show_window.items():
            window.close()
            self.parent.action_group_windows.removeAction(action)
        self.windows = []
        self._show_window = {}

    def minimize(self):
        """
        Minimize the plug-in
        """
        for window in self.windows:
            window.showMinimized()

    def bringAllToFront(self):
        """
        Bring plugin window(s) to front
        """
        for window in self.windows:
            window.showNormal()

    def showWindow(self):
        """
        Show plugin window(s)
        """
        for window in self.windows:
            window.show()

    def setWindowVisible(self, visible):
        """
        Set window visibility
        """
        for (unused_window, action) in self._show_window.items():
            action.setVisible(visible)
        for mnu in self.menus:
            mnu.menuAction().setVisible(visible)

    def onShowWindow(self, window):
        """
        Show plugin window
        @param window[QWindow] Window to show
        """
        window.showNormal()
        window.activateWindow()
        window.raise_()
        self.updateMenuBar()

    def addMenu(self, menu, text):
        """
        Add plugin-specific menu
        @param menu
        @param text
        """
        new_menu = menu.addMenu(text)
        new_menu.menuAction().setVisible(False)
        self.menus.append(new_menu)
        return new_menu

    def addMenuSeparator(self, menu):
        """
        Add separator to plugin-specific menu
        """
        action = menu.addSeparator()
        action.setVisible(False)
        self.actions.append(action)
        return action

    def addMenuAction(self, menu, string, method, keysequece = 0):
        """
        Add action to plugin-specific menu
        """
        action = menu.addAction(string, method, keysequece)
        action.setVisible(False)
        self.actions.append(action)
        return action

    def updateMenuBar(self):
        """
        Update menu bar
        """
        qapp = QtWidgets.QApplication.instance()
        active_window = qapp.activeWindow()
        if active_window in self._show_window:
            self._show_window[active_window].setChecked(True)

    def setupFromYml(self, yml):
        """
        Setup pluing from YML file
        """

    def onCreate(self):
        """
        Callback when create happens
        """
