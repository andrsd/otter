import os
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5 import QtWidgets, QtCore
from otter.plugins.common.OSplitter import OSplitter
from otter.plugins.PluginWindowBase import PluginWindowBase
from otter.plugins.viz.ParamsWindow import ParamsWindow


class RenderWindow(PluginWindowBase):
    """
    Window for displaying the result
    """

    def __init__(self, plugin):
        super().__init__(plugin)
        self._file_name = None
        self._vtk_renderer = vtk.vtkRenderer()

        self.setupWidgets()
        self.setupMenuBar()
        self.updateWindowTitle()

        state = self.plugin.settings.value("splitter/state")
        if state is not None:
            self._splitter.restoreState(state)

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

    def setupWidgets(self):
        self._splitter = OSplitter(QtCore.Qt.Horizontal, self)

        self._params_window = ParamsWindow(self)
        self._params_window.show()
        self._splitter.addWidget(self._params_window)
        self._splitter.setCollapsible(0, True)

        frame = QtWidgets.QFrame(self)
        self._vtk_widget = QVTKRenderWindowInteractor(frame)

        self._vtk_widget.GetRenderWindow().AddRenderer(self._vtk_renderer)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._vtk_widget)

        frame.setLayout(self._layout)
        frame.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                            QtWidgets.QSizePolicy.Expanding)

        self._splitter.addWidget(frame)
        self._splitter.setCollapsible(1, False)
        self._splitter.setStretchFactor(1, 10)

        self.setCentralWidget(self._splitter)

    def setupMenuBar(self):
        file_menu = self._menubar.addMenu("File")
        self._new_action = file_menu.addAction(
            "New", self.onNewFile, "Ctrl+N")
        self._open_action = file_menu.addAction(
            "Open", self.onOpenFile, "Ctrl+O")
        self._recent_menu = file_menu.addMenu("Open Recent")
        self.buildRecentFilesMenu()
        file_menu.addSeparator()
        self._close_action = file_menu.addAction(
            "Close", self.onClose, "Ctrl+W")
        file_menu.addSeparator()
        self._render_action = file_menu.addAction(
            "Render", self.onRender, "Ctrl+Shift+R")

    def updateWindowTitle(self):
        title = "Viz"
        if self._file_name is None:
            self.setWindowTitle(title)
        else:
            self.setWindowTitle("{} \u2014 {}".format(
                title, os.path.basename(self._file_name)))

    def _updateViewModeLocation(self):
        pass

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

    def closeEvent(self, event):
        self.plugin.settings.setValue(
            "splitter/state", self._splitter.saveState())
        super().closeEvent(event)

    def clear(self):
        self._params_window.clear()

    def onUpdateWindow(self):
        self._vtk_render_window.Render()

    def loadFile(self, file_name):
        self._params_window.loadFile(file_name)

    def onClose(self):
        self.close()

    def onNewFile(self):
        self.clear()

    def onOpenFile(self):
        file_name, f = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open File',
            "",
            "ExodusII files (*.e *.exo)")
        if file_name:
            self.loadFile(file_name)

    def onRender(self):
        pass
