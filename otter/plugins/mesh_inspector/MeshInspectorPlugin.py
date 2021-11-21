from PyQt5 import QtCore
from otter.assets import Assets
from otter.plugins.Plugin import Plugin
from otter.plugins.common.LoadFileEvent import LoadFileEvent
from otter.plugins.mesh_inspector.MeshWindow import MeshWindow


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
        self.mesh_window = MeshWindow(self)
        self.registerWindow(self.mesh_window)

        if self.parent is not None and hasattr(self.parent, 'window_menu'):
            if hasattr(self.mesh_window, 'menuBar'):
                self.mesh_window.menuBar().addMenu(self.parent.window_menu)

    def onClose(self):
        self.mesh_window.close()

    def loadFile(self, file_name):
        event = LoadFileEvent(file_name)
        QtCore.QCoreApplication.postEvent(self.mesh_window, event)
