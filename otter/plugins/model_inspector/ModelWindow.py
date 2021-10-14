import vtk
from PyQt5 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from model_inspector.InputReader import InputReader
import common
from common.OtterInteractorStyle import OtterInteractorStyle


class LoadThread(QtCore.QThread):
    """ Worker thread for loading input files """

    def __init__(self, file_name):
        super().__init__()
        self._file_name = file_name
        self._components = None

    def run(self):
        reader = InputReader()
        self._components = reader.load(self._file_name)

    def getComponents(self):
        return self._components


class ModelWindow(QtWidgets.QMainWindow):
    """
    Window for displaying the model
    """

    fileLoaded = QtCore.pyqtSignal(object)
    boundsChanged = QtCore.pyqtSignal(list)
    componentSelected = QtCore.pyqtSignal(object)

    SHADED = 0
    SILHOUETTE = 1

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self._load_thread = None
        self._components = None
        self._component_color = {}
        self._component_bounds = {}
        self._actors = {}
        self._silhouette_actors = {}
        self._caption_actors = {}
        self._show_captions = False
        self._actor_to_comp_name = {}
        self._render_mode = self.SHADED

        self._last_picked_actor = None
        self._last_picked_property = vtk.vtkProperty()

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

        self._style = OtterInteractorStyle(self)
        self._style.SetDefaultRenderer(self._vtk_renderer)
        self._vtk_interactor.SetInteractorStyle(self._style)

        # TODO: set background from preferences/templates
        self._vtk_renderer.SetBackground([0.98, 0.98, 0.98])
        # set anti-aliasing on
        self._vtk_renderer.SetUseFXAA(True)
        self._vtk_render_window.SetMultiSamples(1)

        self._vtk_interactor.Initialize()
        self._vtk_interactor.Start()

        self._setupOrientationMarker()

        self.show()

    def setRenderMode(self, mode):
        self._render_mode = mode

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

        self._actor_to_comp_name = {}
        for name, comp in self._components.items():
            actor = comp.getActor()
            self._actors[name] = actor
            if self._render_mode == self.SILHOUETTE:
                property = actor.GetProperty()
                property.LightingOff()
                self._setPropertyColor(property, QtGui.QColor(255, 255, 255))
            self._vtk_renderer.AddViewProp(actor)

            silhouette_actor = comp.getSilhouetteActor()
            if self._render_mode == self.SHADED:
                silhouette_actor.VisibilityOff()
            self._silhouette_actors[name] = silhouette_actor
            self._vtk_renderer.AddViewProp(silhouette_actor)
            comp.setSilhouetteCamera(self._vtk_renderer.GetActiveCamera())
            property = silhouette_actor.GetProperty()
            property.SetColor([0, 0, 0])
            property.SetLineWidth(2)

            caption_actor = comp.getCaptionActor()
            caption_actor.SetVisibility(self._show_captions)
            caption_actor.GetProperty().SetColor([0, 0, 0])
            self._caption_actors[name] = caption_actor
            text_actor = caption_actor.GetTextActor()
            text_actor.SetTextScaleModeToViewport()

            property = caption_actor.GetCaptionTextProperty()
            property.SetColor([0, 0, 0])
            property.BoldOff()
            property.ItalicOff()
            property.SetFontSize(3)
            property.ShadowOff()
            caption_actor.SetCaptionTextProperty(property)
            self._vtk_renderer.AddViewProp(caption_actor)

            self._actor_to_comp_name[actor] = name

        bnds = self._computeBounds()
        self.boundsChanged.emit(bnds)
        self._cube_axes_actor = self._setupCubeAxisActor(bnds)

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

    def _getComponentSilhouetteActor(self, component_name):
        if component_name in self._components:
            return self._components[component_name].getSilhouetteActor()
        else:
            return None

    def _getComponentMapper(self, component_name):
        if component_name in self._components:
            return self._components[component_name].getMapper()
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
        if visible:
            actor = self._getComponentActor(component_name)
            actor.VisibilityOn()

            if self._render_mode == self.SILHOUETTE:
                actor = self._getComponentSilhouetteActor(component_name)
                actor.VisibilityOn()
        else:
            actor = self._getComponentActor(component_name)
            actor.VisibilityOff()

            if self._render_mode == self.SILHOUETTE:
                actor = self._getComponentSilhouetteActor(component_name)
                actor.VisibilityOff()

        self._vtk_render_window.Render()

    def onComponentColorChanged(self, component_name, qcolor):
        self._component_color[component_name] = qcolor

        if self._render_mode == self.SHADED:
            actor = self._getComponentActor(component_name)
            property = actor.GetProperty()
            self._setPropertyColor(property, qcolor)
            self._vtk_render_window.Render()

    def _setPropertyColor(self, property, qcolor):
        clr = [qcolor.redF(), qcolor.greenF(), qcolor.blueF()]
        property.SetColor(clr)

    def _getComponentBounds(self, comp):
        glob_min = QtGui.QVector3D(float('inf'), float('inf'), float('inf'))
        glob_max = QtGui.QVector3D(float('-inf'), float('-inf'), float('-inf'))
        actor = self._getComponentActor(comp.name)
        bnd = actor.GetBounds()
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

    def onClicked(self, pos):
        picker = vtk.vtkPicker()
        picker.Pick(pos.x(), pos.y(), 0, self._vtk_renderer)

        picked_actor = picker.GetActor()
        if picked_actor is None:
            if self._last_picked_actor is not None:
                self._last_picked_actor.GetProperty().SetColor(
                    self._last_picked_property.GetColor())
            self.componentSelected.emit(None)
        elif picked_actor != self._last_picked_actor:
            property = picked_actor.GetProperty()
            if self._last_picked_actor is not None:
                self._last_picked_actor.GetProperty().SetColor(
                    self._last_picked_property.GetColor())

            self._last_picked_property.SetColor(property.GetColor())

            # FIXME: set color from preferences
            property.SetColor([1, 1, 1])
            property.SetDiffuse(1.0)
            property.SetSpecular(0.0)

            comp_name = self._actor_to_comp_name[picked_actor]
            self.componentSelected.emit(comp_name)

        self._vtk_render_window.Render()
        self._last_picked_actor = picked_actor

    def onRenderModeChanged(self, mode):
        self.setRenderMode(mode)

        for actor in self._actors.values():
            actor.VisibilityOn()
            if mode == self.SHADED:
                property = actor.GetProperty()
                property.LightingOn()
                comp_name = self._actor_to_comp_name[actor]
                qcolor = self._component_color[comp_name]
                self._setPropertyColor(property, qcolor)
            elif mode == self.SILHOUETTE:
                property = actor.GetProperty()
                property.LightingOff()
                self._setPropertyColor(property, QtGui.QColor(255, 255, 255))

        for actor in self._silhouette_actors.values():
            if mode == self.SHADED:
                actor.VisibilityOff()
            elif mode == self.SILHOUETTE:
                actor.VisibilityOn()
                property = actor.GetProperty()
                self._setPropertyColor(property, QtGui.QColor(0, 0, 0))
                property.SetLineWidth(3)

        self._vtk_render_window.Render()

    def _setupCubeAxisActor(self, bnds):
        actor = vtk.vtkCubeAxesActor()
        actor.SetBounds(*bnds)
        actor.SetCamera(self._vtk_renderer.GetActiveCamera())
        actor.SetGridLineLocation(vtk.vtkCubeAxesActor.VTK_GRID_LINES_ALL)
        actor.SetFlyMode(vtk.vtkCubeAxesActor.VTK_FLY_OUTER_EDGES)

        color = [0, 0, 0]

        prop = vtk.vtkProperty()
        prop.SetColor(color)

        actor.SetXAxesLinesProperty(prop)
        actor.SetYAxesLinesProperty(prop)
        actor.SetZAxesLinesProperty(prop)

        actor.SetXAxesGridlinesProperty(prop)
        actor.SetYAxesGridlinesProperty(prop)
        actor.SetZAxesGridlinesProperty(prop)

        for axis in [0, 1, 2]:
            actor.GetTitleTextProperty(axis).SetColor(color)
            actor.GetLabelTextProperty(axis).SetColor(color)

        return actor

    def onShowLabels(self, state):
        self._show_captions = state
        for actor in self._caption_actors.values():
            actor.SetVisibility(state)
        self._vtk_render_window.Render()
