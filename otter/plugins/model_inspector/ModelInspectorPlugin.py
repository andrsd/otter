import os
from PyQt5 import QtCore
from otter.assets import Assets
from otter.plugins.Plugin import Plugin
from otter.plugins.common.LoadFileEvent import LoadFileEvent
from otter.plugins.model_inspector.InputReader import InputReader
from otter.plugins.model_inspector.ModelWindow import ModelWindow
from otter.plugins.model_inspector.InfoWindow import InfoWindow


class ModelInspectorPlugin(Plugin):
    """
    Plugin for inspecting system level models
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_window = None

        here = os.path.dirname(os.path.realpath(__file__))
        InputReader.loadSyntax(os.path.join(here, 'thm-components.py'))

    @staticmethod
    def name():
        return "Model Inspector"

    @staticmethod
    def icon():
        return Assets().icons['movie']

    def onCreate(self):
        self.info_window = InfoWindow(self)
        self.model_window = ModelWindow(self)
        self.registerWindow(self.model_window)

        if self.parent is not None and hasattr(self.parent, 'window_menu'):
            if hasattr(self.model_window, 'menuBar'):
                self.model_window.menuBar().addMenu(self.parent.window_menu)

        self.model_window.fileLoaded.connect(self.info_window.onFileLoaded)
        self.model_window.boundsChanged.connect(
            self.info_window.onBoundsChanged)
        self.model_window.componentSelected.connect(
            self.info_window.onComponentSelected)

        self.info_window.componentVisibilityChanged.connect(
            self.model_window.onComponentVisibilityChanged)
        self.info_window.componentColorChanged.connect(
            self.model_window.onComponentColorChanged)
        self.info_window.dimensionsStateChanged.connect(
            self.model_window.onCubeAxisVisibilityChanged)
        self.info_window.orientationMarkerStateChanged.connect(
            self.model_window.onOrientationmarkerVisibilityChanged)
        self.info_window.showLabels.connect(
            self.model_window.onShowLabels)
        self.info_window.showPPS.connect(
            self.model_window.onShowPPS)

    def onClose(self):
        self.info_window.close()
        self.model_window.close()

    def loadFile(self, file_name):
        event = LoadFileEvent(file_name)
        QtCore.QCoreApplication.postEvent(self.model_window, event)
