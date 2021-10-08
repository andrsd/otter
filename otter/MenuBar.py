from PyQt5 import QtWidgets


class MenuBar(QtWidgets.QMenuBar):
    """
    Menu bar
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.menus = {}

    def addMenu(self, title):
        """
        Add menu to menu bar
        @param title[str] Menu title
        """
        menu = super().addMenu(title)
        self.menus[title] = menu
        return menu
