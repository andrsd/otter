import contextlib
import fcntl
import vtk
from PyQt5 import QtCore, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


@contextlib.contextmanager
def lock_file(filename):
    """
    Locks a file so that the exodus reader can safely read
    a file without something else writing to it while we do it.
    """
    with open(filename, "a+") as f:
        fcntl.flock(f, fcntl.LOCK_SH)
        yield
        fcntl.flock(f, fcntl.LOCK_UN)


class LoadThread(QtCore.QThread):
    """ Worker thread for loading ExodusII files """

    def __init__(self, file_name):
        super().__init__()
        self._file_name = file_name
        self._reader = None

    def run(self):
        self._reader = vtk.vtkExodusIIReader()

        with lock_file(self._file_name):
            self._reader.SetFileName(self._file_name)
            self._reader.UpdateInformation()
            self._reader.Update()

    def getReader(self):
        return self._reader


class MeshWindow(QtWidgets.QMainWindow):
    """
    Window for displaying the mesh
    """

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self._load_thread = None

        self._frame = QtWidgets.QFrame(self)
        self._vtk_widget = QVTKRenderWindowInteractor(self._frame)

        self._vtk_renderer = vtk.vtkRenderer()
        self._vtk_widget.GetRenderWindow().AddRenderer(self._vtk_renderer)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._vtk_widget)

        self._frame.setLayout(self._layout)

        self.setAcceptDrops(True)
        self.setCentralWidget(self._frame)
        self.setWindowTitle("Mesh")

        self._vtk_render_window = self._vtk_widget.GetRenderWindow()
        self._vtk_interactor = self._vtk_render_window.GetInteractor()

        self._vtk_interactor.SetInteractorStyle(
            vtk.vtkInteractorStyleTrackballCamera())

        # TODO: set background from preferences/templates
        self._vtk_renderer.SetGradientBackground(True)
        self._vtk_renderer.SetBackground([0.321, 0.3411, 0.4313])
        self._vtk_renderer.SetBackground2([0.321, 0.3411, 0.4313])
        # set anti-aliasing on
        self._vtk_renderer.SetUseFXAA(True)
        self._vtk_render_window.SetMultiSamples(1)

        self._vtk_widget.AddObserver('StartInteractionEvent',
                                     self.onStartInteraction)
        self._vtk_widget.AddObserver('EndInteractionEvent',
                                     self.onEndInteraction)

        self._vtk_interactor.Initialize()
        self._vtk_interactor.Start()

        self.show()

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

    def onStartInteraction(self, obj, event):
        pass

    def onEndInteraction(self, obj, event):
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
                self.loadFile(file_names[0])
        else:
            event.ignore()

    def loadFile(self, file_name):
        self._load_thread = LoadThread(file_name)
        self._load_thread.finished.connect(self.onLoadFinished)
        self._load_thread.start()

    def onLoadFinished(self):
        reader = self._load_thread.getReader()

        self._geometry = vtk.vtkCompositeDataGeometryFilter()
        self._geometry.SetInputConnection(0, reader.GetOutputPort(0))
        self._geometry.Update()

        self._mapper = vtk.vtkPolyDataMapper()
        self._mapper.SetInputConnection(self._geometry.GetOutputPort())
        self._mapper.SetScalarModeToUsePointFieldData()
        self._mapper.InterpolateScalarsBeforeMappingOn()

        self._vtk_actor = vtk.vtkActor()
        self._vtk_actor.SetMapper(self._mapper)
        property = self._vtk_actor.GetProperty()
        property.SetRepresentationToSurface()
        property.SetColor([1, 1, 0])
        property.SetEdgeVisibility(True)
        property.SetEdgeColor([0.1, 0.1, 0.4])

        self._vtk_renderer.AddViewProp(self._vtk_actor)
        self._vtk_renderer.ResetCamera()
        self._vtk_renderer.GetActiveCamera().Zoom(1.5)

        self._vtk_render_window.Render()
