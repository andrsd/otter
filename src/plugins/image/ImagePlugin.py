import os
from Plugin import Plugin
from PyQt5 import QtCore, QtWidgets, QtGui
from ResultWindow import ResultWindow
from ParamsWindow import ParamsWindow

class ImagePlugin(Plugin):

    def __init__(self):
        super(ImagePlugin, self).__init__()
        self.params_window = None
        self.result_window = None

    def name(self):
        return "Image"

    def icon(self):
        otter_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
        icon_dir = os.path.join(otter_dir, "icons")
        icon_file_name = os.path.join(icon_dir, "picture.svg")
        return QtGui.QIcon(icon_file_name)

    def create(self, parent):
        super(ImagePlugin, self).create(parent)
        self._show_params_window = parent._windowMenu.addAction("Parameters", self.onShowParamsWindow)
        self._show_params_window.setCheckable(True)
        self._show_result_window = parent._windowMenu.addAction("Result", self.onShowResultWindow)
        self._show_result_window.setCheckable(True)

        parent._action_group_windows.addAction(self._show_params_window)
        parent._action_group_windows.addAction(self._show_result_window)

        if self.params_window == None:
            self.params_window = ParamsWindow(parent)
        if self.result_window == None:
            self.result_window = ResultWindow(parent)
        self.file = QtCore.QFile()

    def onCloseFile(self):
        super(ImagePlugin, self).onCloseFile()
        self.result_window.close()
        self.params_window.close()

        self.result_window = None
        self.params_window = None

        self.parent._action_group_windows.removeAction(self._show_params_window)
        self.parent._action_group_windows.removeAction(self._show_result_window)
        self._show_params_window = None
        self._show_result_window = None

    def onMinimize(self):
        self.result_window.showMinimized()
        self.params_window.showMinimized()

    def onBringAllToFront(self):
        self.result_window.showNormal()
        self.params_window.showNormal()

    def showWindow(self):
        self.result_window.show()
        self.params_window.show()

    def setWindowVisible(self, visible):
        self._show_params_window.setVisible(visible)
        self._show_result_window.setVisible(visible)

    def onShowParamsWindow(self):
        self.params_window.showNormal()
        self.params_window.activateWindow()
        self.params_window.raise_()
        self.updateMenuBar()

    def onShowResultWindow(self):
        self.result_window.showNormal()
        self.result_window.activateWindow()
        self.result_window.raise_()
        self.updateMenuBar()

    def updateMenuBar(self):
        qapp = QtWidgets.QApplication.instance()
        active_window = qapp.activeWindow()
        if active_window == self.params_window:
            self._show_params_window.setChecked(True)
        elif active_window == self.result_window:
            self._show_result_window.setChecked(True)
