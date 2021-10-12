from PyQt5 import QtCore
from otter.assets import Assets
from Plugin import Plugin
from mesh_inspector.MeshWindow import MeshWindow
from mesh_inspector.InfoWindow import InfoWindow


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
        self.registerWindow(self.info_window)
        self.mesh_window = MeshWindow(self)
        self.registerWindow(self.mesh_window)

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

        settings = QtCore.QSettings()
        settings.beginGroup(self.name())
        geom = settings.value("mesh_wnd_geometry")
        if geom is None:
            self.mesh_window.resize(700, 500)
        else:
            self.mesh_window.restoreGeometry(geom)
        geom = settings.value("info_wnd_geometry")
        if geom is None:
            self.info_window.resize(350, 700)
        else:
            self.info_window.restoreGeometry(geom)
        settings.endGroup()

    def onClose(self):
        settings = QtCore.QSettings()
        settings.beginGroup(self.name())
        settings.setValue("mesh_wnd_geometry", self.mesh_window.saveGeometry())
        settings.setValue("info_wnd_geometry", self.info_window.saveGeometry())
        settings.endGroup()
