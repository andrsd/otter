import vtk
from PyQt5 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from model_inspector.InputReader import InputReader
import common


class LoadThread(QtCore.QThread):
    """ Worker thread for loading ExodusII files """

    def __init__(self, file_name):
        super().__init__()
        self._file_name = file_name
        self._componets = None

    def run(self):
        reader = InputReader()
        self._componets = reader.load(self._file_name)

    def getComponents(self):
        return self._componets


class ModelWindow(QtWidgets.QMainWindow):
    """
    Window for displaying the model
    """

    fileLoaded = QtCore.pyqtSignal(object)
    boundsChanged = QtCore.pyqtSignal(list)

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self._load_thread = None
        self._components = None
        self._component_bounds = {}

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
        self.setWindowTitle("Model")

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

        self._vtk_interactor.Initialize()
        self._vtk_interactor.Start()

        self._setupOrientationMarker()

        self.show()

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

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
        self._components = self._load_thread.getComponents()

        bnds = self._computeBounds()
        self.boundsChanged.emit(bnds)
        self._cube_axes_actor = vtk.vtkCubeAxesActor()
        self._cube_axes_actor.SetBounds(*bnds)
        self._cube_axes_actor.SetCamera(self._vtk_renderer.GetActiveCamera())
        self._cube_axes_actor.SetGridLineLocation(
            vtk.vtkCubeAxesActor.VTK_GRID_LINES_ALL)
        self._cube_axes_actor.SetFlyMode(
            vtk.vtkCubeAxesActor.VTK_FLY_OUTER_EDGES)

        self._vtk_renderer.ResetCamera()
        self._vtk_renderer.GetActiveCamera().Zoom(1.5)

        self.fileLoaded.emit(self._components.values())

        self._vtk_render_window.Render()

    def _computeBounds(self):
        for comp in self._components.values():
            bounds = self._getComponentBounds(comp)
            self._component_bounds[comp.name] = bounds

        gmin = QtGui.QVector3D(float('inf'), float('inf'), float('inf'))
        gmax = QtGui.QVector3D(float('-inf'), float('-inf'), float('-inf'))
        for bnd in self._component_bounds.values():
            bmin, bmax = bnd
            gmin = common.point_min(bmin, gmin)
            gmax = common.point_max(bmax, gmax)
        return [gmin.x(), gmax.x(), gmin.y(), gmax.y(), gmin.z(), gmax.z()]

    def _getComponentActor(self, component_name):
        if component_name in self._components:
            return self._components[component_name].getActor()
        else:
            return None

    def _setupOrientationMarker(self):
        axes = vtk.vtkAxesActor()
        self._ori_marker = vtk.vtkOrientationMarkerWidget()
        self._ori_marker.SetOrientationMarker(axes)
        self._ori_marker.SetViewport(0.8, 0, 1.0, 0.2)
        self._ori_marker.SetInteractor(self._vtk_interactor)
        self._ori_marker.SetEnabled(1)
        self._ori_marker.SetInteractive(False)

    def onComponentVisibilityChanged(self, component_name, visible):
        actors = self._getComponentActor(component_name)
        if visible:
            for a in actors:
                self._vtk_renderer.AddViewProp(a)
        else:
            for a in actors:
                self._vtk_renderer.RemoveViewProp(a)
        self._vtk_render_window.Render()

    def onComponentColorChanged(self, component_name, qcolor):
        actors = self._getComponentActor(component_name)
        for a in actors:
            property = a.GetProperty()
            clr = [qcolor.redF(), qcolor.greenF(), qcolor.blueF()]
            property.SetColor(clr)

    def _getComponentBounds(self, comp):
        glob_min = QtGui.QVector3D(float('inf'), float('inf'), float('inf'))
        glob_max = QtGui.QVector3D(float('-inf'), float('-inf'), float('-inf'))
        actors = comp.getActor()
        for a in actors:
            bnd = a.GetBounds()
            bnd_min = QtGui.QVector3D(bnd[0], bnd[2], bnd[4])
            bnd_max = QtGui.QVector3D(bnd[1], bnd[3], bnd[5])
            glob_min = common.point_min(bnd_min, glob_min)
            glob_max = common.point_max(bnd_max, glob_max)

        return (glob_min, glob_max)

    def onCubeAxisVisibilityChanged(self, visible):
        if visible:
            self._vtk_renderer.AddViewProp(self._cube_axes_actor)
        else:
            self._vtk_renderer.RemoveViewProp(self._cube_axes_actor)
        self._vtk_render_window.Render()

    def onOrientationmarkerVisibilityChanged(self, visible):
        if visible:
            self._ori_marker.EnabledOn()
        else:
            self._ori_marker.EnabledOff()
        self._vtk_render_window.Render()
