from otter.assets import Assets
from Plugin import Plugin
from model_inspector.ModelWindow import ModelWindow
from model_inspector.InfoWindow import InfoWindow


class ModelInspectorPlugin(Plugin):
    """
    Plugin for inspecting system level models
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_window = None

    @staticmethod
    def name():
        return "Model Inspector"

    @staticmethod
    def icon():
        return Assets().icons['movie']

    def onCreate(self):
        self.info_window = InfoWindow(self)
        self.registerWindow(self.info_window)
        self.model_window = ModelWindow(self)
        self.registerWindow(self.model_window)

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
        self.info_window.renderModeChanged.connect(
            self.model_window.onRenderModeChanged)
        self.info_window.showLabels.connect(
            self.model_window.onShowLabels)
