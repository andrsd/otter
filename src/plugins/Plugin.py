class Plugin:

    def __init__(self):
        self.file = None
        self.parent = None

    """
    Return the name of the plugin (used in the GUI)
    """
    def name(self):
        return None

    """
    Return the icon for this plugin (as QIcon)
    """
    def icon(self):
        return None

    def create(self, parent):
        self.parent = parent

    def onCloseFile(self):
        self.file = None

    def setWindowVisible(self, visible):
        pass

    def updateMenuBar(self):
        pass
