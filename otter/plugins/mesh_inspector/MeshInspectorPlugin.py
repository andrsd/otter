from PyQt5 import QtCore, QtWidgets
from otter.assets import Assets
from Plugin import Plugin
from MeshWindow import MeshWindow
from InfoWindow import InfoWindow


class MeshInspectorPlugin(Plugin):
    """
    Plugin for inspecting meshes
    """

    def __init__(self, parent):
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
        self.info_window = InfoWindow(self)
        self.registerWindow(self.info_window)

        screen_rc = QtWidgets.QApplication.desktop().screenGeometry()
        left_wd = 0.8 * screen_rc.width()
        mesh_rc = QtCore.QRect(screen_rc.left(),
                               screen_rc.top(),
                               left_wd,
                               screen_rc.height())
        info_rc = QtCore.QRect(left_wd,
                               screen_rc.top(),
                               screen_rc.width() - left_wd,
                               screen_rc.height())

        mesh_rc.adjust(60, 70, -5, -40)
        self.mesh_window.setGeometry(mesh_rc)
        info_rc.adjust(5, 70, -10, -40)
        self.info_window.setGeometry(info_rc)