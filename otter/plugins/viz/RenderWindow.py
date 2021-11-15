import os
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5 import QtWidgets, QtCore
from otter.plugins.PluginWindowBase import PluginWindowBase


class RenderWindow(PluginWindowBase):
    """
    Window for displaying the result
    """

    def __init__(self, plugin):
        super().__init__(plugin)
        self._file_name = None

        self.setupWidgets()
        self.setupMenuBar()
        self.updateWindowTitle()

        self.setAcceptDrops(True)

        self._vtk_render_window = self._vtk_widget.GetRenderWindow()
        self._vtk_interactor = self._vtk_render_window.GetInteractor()

        self._vtk_interactor.SetInteractorStyle(
            vtk.vtkInteractorStyleTrackballCamera())

        # set anti-aliasing on
        self._vtk_renderer.SetUseFXAA(True)
        self._vtk_render_window.SetMultiSamples(1)

        self._vtk_interactor.Initialize()
        self._vtk_interactor.Start()

        self.clear()
        self.show()

        self._update_timer = QtCore.QTimer()
        self._update_timer.timeout.connect(self.onUpdateWindow)
        self._update_timer.start(250)

    def getVtkRenderer(self):
        return self._vtk_renderer

    def setupWidgets(self):
        frame = QtWidgets.QFrame(self)
        self._vtk_widget = QVTKRenderWindowInteractor(frame)

        self._vtk_renderer = vtk.vtkRenderer()
        self._vtk_widget.GetRenderWindow().AddRenderer(self._vtk_renderer)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._vtk_widget)

        frame.setLayout(self._layout)

        self.setCentralWidget(frame)

    def setupMenuBar(self):
        file_menu = self._menubar.addMenu("File")
        self._new_action = file_menu.addAction(
            "New", self.plugin.onNewFile, "Ctrl+N")
        self._open_action = file_menu.addAction(
            "Open", self.plugin.onOpenFile, "Ctrl+O")
        file_menu.addSeparator()
        self._close_action = file_menu.addAction(
            "Close", self.plugin.onClose, "Ctrl+W")
        file_menu.addSeparator()
        self._render_action = file_menu.addAction(
            "Render", self.plugin.onRender, "Ctrl+Shift+R")

    def updateWindowTitle(self):
        title = "Result"
        if self._file_name is None:
            self.setWindowTitle(title)
        else:
            self.setWindowTitle("{} \u2014 {}".format(
                title, os.path.basename(self._file_name)))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()

            file_names = []
            for url in event.mimeData().urls():
                file_names.append(url.toLocalFile())
            if len(file_names) > 0:
                self.plugin.loadFile(file_names[0])
        else:
            event.ignore()

    def clear(self):
        pass

    def onUpdateWindow(self):
        self._vtk_render_window.Render()
