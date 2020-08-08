from PyQt5 import QtWidgets, QtCore

class MenuBar(QtWidgets.QMenuBar):

    def __init__(self, parent = None):
        super(MenuBar, self).__init__(parent)
        self.menus = {}

    def addMenu(self, title):
        menu = super(MenuBar, self).addMenu(title)
        self.menus[title] = menu
        return menu
