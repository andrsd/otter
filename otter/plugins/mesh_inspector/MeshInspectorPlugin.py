from otter.assets import Assets
from otter.plugins.Plugin import Plugin
from otter.plugins.mesh_inspector.MeshWindow import MeshWindow
from otter.plugins.mesh_inspector.InfoWindow import InfoWindow


class MeshInspectorPlugin(Plugin):
    """
    Plugin for inspecting meshes
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mesh_window = None
        self.info_window = None

    @staticmethod
    def name():
        return "Mesh Inspector"

    @staticmethod
    def icon():
        return Assets().icons['movie']

    def onCreate(self):
        self.info_window = InfoWindow(self)
        self.mesh_window = MeshWindow(self)
        self.registerWindow(self.mesh_window)

        if self.parent is not None and hasattr(self.parent, 'window_menu'):
            if hasattr(self.mesh_window, 'menuBar'):
                self.mesh_window.menuBar().addMenu(self.parent.window_menu)

        self.mesh_window.fileLoaded.connect(self.info_window.onFileLoaded)
        self.mesh_window.boundsChanged.connect(
            self.info_window.onBoundsChanged)
        self.info_window.blockVisibilityChanged.connect(
            self.mesh_window.onBlockVisibilityChanged)
        self.info_window.blockColorChanged.connect(
            self.mesh_window.onBlockColorChanged)
        self.info_window.sidesetVisibilityChanged.connect(
            self.mesh_window.onSidesetVisibilityChanged)
        self.info_window.nodesetVisibilityChanged.connect(
            self.mesh_window.onNodesetVisibilityChanged)
        self.info_window.dimensionsStateChanged.connect(
            self.mesh_window.onCubeAxisVisibilityChanged)
        self.info_window.orientationMarkerStateChanged.connect(
            self.mesh_window.onOrientationmarkerVisibilityChanged)

    def onClose(self):
        self.info_window.close()
        self.mesh_window.close()
