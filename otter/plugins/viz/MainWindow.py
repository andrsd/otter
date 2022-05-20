import os
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5.QtWidgets import QToolBar, QProgressDialog, QMessageBox, \
    QFileDialog
from PyQt5.QtCore import QThread, QTimer, Qt
from otter.plugins.common.LoadFileEvent import LoadFileEvent
from otter.plugins.common.ExodusIIReader import ExodusIIReader
from otter.plugins.common.VTKReader import VTKReader
from otter.plugins.common.PetscHDF5Reader import PetscHDF5Reader
from otter.plugins.common.OtterInteractorStyle3D import OtterInteractorStyle3D
from otter.plugins.common.OtterInteractorStyle2D import OtterInteractorStyle2D
from otter.plugins.PluginWindowBase import PluginWindowBase
from otter.plugins.viz.ParamsWindow import ParamsWindow
from otter.plugins.viz.BackgroundProps import BackgroundProps
from otter.plugins.viz.FileProps import FileProps
from otter.plugins.viz.TextProps import TextProps


class LoadThread(QThread):
    """ Worker thread for loading data set files """

    def __init__(self, file_name):
        super().__init__()
        if file_name.endswith('.e') or file_name.endswith('.exo'):
            self._reader = ExodusIIReader(file_name)
        elif file_name.endswith('.vtk'):
            self._reader = VTKReader(file_name)
        elif file_name.endswith('.h5'):
            self._reader = PetscHDF5Reader(file_name)
        else:
            self._reader = None

    def run(self):
        self._reader.load()

    def getReader(self):
        return self._reader


class MainWindow(PluginWindowBase):
    """
    Window for displaying the result
    """

    def __init__(self, plugin):
        super().__init__(plugin)
        self._props = []
        self._file_name = None
        self._vtk_renderer = vtk.vtkRenderer()
        self._load_thread = None
        self._progress = None

        self.setupWidgets()
        self.setupMenuBar()
        self.setupToolBar()
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
        self.updateMenuBar()

        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self.onUpdateWindow)
        self._update_timer.start(250)

    def setupWidgets(self):
        self._vtk_widget = QVTKRenderWindowInteractor(self)
        self._vtk_widget.GetRenderWindow().AddRenderer(self._vtk_renderer)
        self.setCentralWidget(self._vtk_widget)

        self._params_window = ParamsWindow(self)

        self._bkgnd_props = BackgroundProps(self._vtk_renderer, self)

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

        view_menu = self._menubar.addMenu("View")
        self._view_objects_action = view_menu.addAction(
            "Objects", self.onViewObjects)
        self._view_objects_action.setCheckable(True)

    def updateMenuBar(self):
        self._view_objects_action.setChecked(self._params_window.isVisible())

    def setupToolBar(self):
        self._toolbar = QToolBar()
        self._toolbar.setMovable(False)
        self._toolbar.setFloatable(False)
        self._toolbar.setFixedHeight(32)
        self._toolbar.setStyleSheet("""
            border: none;
            """)
        self._toolbar.addAction("O", self.onOpenFile)
        self._toolbar.addSeparator()
        self._toolbar.addAction("T", self.onAddText)

    def updateWindowTitle(self):
        title = "Viz"
        if self._file_name is None:
            self.setWindowTitle(title)
        else:
            self.setWindowTitle("{} \u2014 {}".format(
                title, os.path.basename(self._file_name)))

    def _updateViewModeLocation(self):
        pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateParamsWindowGeometry()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            file_names = []
            for url in event.mimeData().urls():
                file_names.append(url.toLocalFile())
            if len(file_names) > 0:
                self.loadFile(file_names[0])
        else:
            event.ignore()

    def event(self, e):
        if e.type() == LoadFileEvent.TYPE:
            self.loadFile(e.fileName())
            return True
        else:
            return super().event(e)

    def closeEvent(self, event):
        super().closeEvent(event)

    def clear(self):
        # todo: remove actors and free them prop dialogs
        self._params_window.clear()
        self._params_window.addPipelineItem(self._bkgnd_props)

    def onUpdateWindow(self):
        self._vtk_render_window.Render()

    def loadFile(self, file_name):
        self._load_thread = LoadThread(file_name)
        if self._load_thread.getReader() is not None:
            self._progress = QProgressDialog(
                "Loading {}...".format(os.path.basename(file_name)),
                None, 0, 0, self)
            self._progress.setWindowModality(Qt.WindowModal)
            self._progress.setMinimumDuration(0)
            self._progress.show()

            self._load_thread.finished.connect(self.onFileLoadFinished)
            self._load_thread.start(QThread.IdlePriority)
        else:
            self._load_thread = None
            QMessageBox.critical(
                None,
                "Unsupported file format",
                "Selected file in not in a supported format.\n"
                "We support the following formats:\n"
                "  ExodusII, VTK Unstructured Grid, HDF5 (PETSc)")

    def onFileLoadFinished(self):
        reader = self._load_thread.getReader()

        self._progress.hide()
        self._progress = None

        if reader.getDimensionality() == 3:
            style = OtterInteractorStyle3D(self)
        else:
            style = OtterInteractorStyle2D(self)
        self._vtk_interactor.SetInteractorStyle(style)

        file_name = reader.getFileName()
        self.addToRecentFiles(file_name)
        self._file_name = file_name
        self.updateWindowTitle()

        file_props = FileProps(reader, self)
        file_props.setWindowTitle("File")
        self._params_window.addPipelineItem(file_props)
        file_props.show()

        actors = file_props.getVtkActor()
        if isinstance(actors, list):
            for act in actors:
                self._vtk_renderer.AddViewProp(act)
        self.resetCamera()

    def onClose(self):
        self.close()

    def onNewFile(self):
        self.clear()

    def onOpenFile(self):
        file_name, f = QFileDialog.getOpenFileName(
            self,
            'Open File',
            "",
            "ExodusII files (*.e *.exo)"
            "HDF5 PETSc files (*.h5);;"
            "VTK Unstructured Grid files (*.vtk)")
        if file_name:
            self.loadFile(file_name)

    def onRender(self):
        pass

    def onAddText(self):
        props = TextProps(self)
        props.setWindowTitle("Text")
        self._params_window.addPipelineItem(props)
        props.show()

        actor = props.getVtkActor()
        if actor is not None:
            self._vtk_renderer.AddViewProp(actor)

    def onAddFile(self):
        file_name, f = QFileDialog.getOpenFileName(
            self,
            'Open File',
            "",
            "ExodusII files (*.e *.exo)"
            "HDF5 PETSc files (*.h5);;"
            "VTK Unstructured Grid files (*.vtk)")
        if file_name:
            self.loadFile(file_name)

    def updateParamsWindowGeometry(self):
        self._params_window.adjustSize()
        margin = 10
        height = self.geometry().height() - (2 * margin)
        left = margin
        top = margin
        self._params_window.setGeometry(
            left, top, self._params_window.width(), height)

    def onViewObjects(self):
        if self._params_window.isVisible():
            self._params_window.hide()
        else:
            self._params_window.show()
        self.updateMenuBar()

    def resetCamera(self):
        camera = self._vtk_renderer.GetActiveCamera()
        focal_point = camera.GetFocalPoint()
        camera.SetPosition(focal_point[0], focal_point[1], 1)
        camera.SetRoll(0)
        self._vtk_renderer.ResetCamera()

    def onClicked(self, pt):
        pass
