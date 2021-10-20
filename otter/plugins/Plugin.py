from PyQt5 import QtWidgets, QtCore


class Plugin:
    """
    Base class for plug-ins
    """

    def __init__(self, parent):
        self.parent = parent
        self.file_name = None
        self.windows = []
        self.actions = []
        self._show_window = {}
        if parent is not None:
            self.parent_menubar = parent.menubar
        else:
            self.parent_menubar = None
        self._menu_map = {}

        self._settings = QtCore.QSettings("Otter", self.name())

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

    @property
    def settings(self):
        return self._settings

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
        return []

    def registerWindow(self, window):
        """
        Call to register created window
        @param window[QWindow] Qt window
        """
        self.windows.append(window)

        if hasattr(self.parent, 'window_menu'):
            action = self.parent.window_menu.addAction(
                window.windowTitle(), lambda: self.onShowWindow(window))
            action.setCheckable(True)
            self.parent.action_group_windows.addAction(action)
            self._show_window[window] = action

    def create(self):
        """
        Create the plugin
        """
        self.onCreate()
        self.showWindow()

    def close(self):
        """
        Close the plugin
        """
        self.onClose()
        for (window, action) in self._show_window.items():
            self.parent.action_group_windows.removeAction(action)
        self.windows = []
        self._show_window = {}

        if self.parent is not None:
            self.parent.closePlugin(self)

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

    def onShowWindow(self, window):
        """
        Show plugin window
        @param window[QWindow] Window to show
        """
        window.showNormal()
        window.activateWindow()
        window.raise_()
        self.updateMenuBar()

    def getMenu(self, name):
        if hasattr(self.parent_menubar, 'menus'):
            return self.parent_menubar.menus[name]
        else:
            if name in self._menu_map:
                return self._menu_map[name]
            else:
                menu = self.parent_menubar.addMenu(name)
                self._menu_map[name] = menu
                return menu

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

    def onClose(self):
        """
        Callback when close happens
        """
