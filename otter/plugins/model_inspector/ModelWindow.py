import os
import vtk
from PyQt5 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from otter.plugins.model_inspector.InputReader import InputReader
import otter.plugins.common as common
from otter.plugins.common.OtterInteractorStyle import OtterInteractorStyle


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

    def getFileName(self):
        return self._file_name


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
        self._file_name = None
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

        self.setupWidgets()
        self.setupMenuBar()
        self.setAcceptDrops(True)
        self.setCentralWidget(self._frame)
        self.updateWindowTitle()

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

        geom = self.plugin.settings.value("window/geometry")
        default_size = QtCore.QSize(700, 500)
        if geom is None:
            self.resize(default_size)
        else:
            if not self.restoreGeometry(geom):
                self.resize(default_size)

        self.show()

    def setupWidgets(self):
        self._frame = QtWidgets.QFrame(self)
        self._vtk_widget = QVTKRenderWindowInteractor(self._frame)

        self._vtk_renderer = vtk.vtkRenderer()
        self._vtk_widget.GetRenderWindow().AddRenderer(self._vtk_renderer)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._vtk_widget)

        self._frame.setLayout(self._layout)

        self._view_menu = QtWidgets.QMenu()
        self._shaded_action = self._view_menu.addAction("Shaded")
        self._shaded_action.setCheckable(True)
        self._hidden_edges_removed_action = self._view_menu.addAction(
            "Hidden edges removed")
        self._hidden_edges_removed_action.setCheckable(True)
        self._shaded_action.setChecked(True)
        self._render_mode = self.SHADED

        self._visual_repr = QtWidgets.QActionGroup(self._view_menu)
        self._visual_repr.addAction(self._shaded_action)
        self._visual_repr.addAction(self._hidden_edges_removed_action)
        self._visual_repr.setExclusive(True)

        self._shaded_action.triggered.connect(self.onShadedTriggered)
        self._hidden_edges_removed_action.triggered.connect(
            self.onHiddenEdgesRemovedTriggered)

        self._view_mode = QtWidgets.QPushButton(self._frame)
        self._view_mode.setText("View")
        self._view_mode.setMenu(self._view_menu)
        self._view_mode.setGeometry(10, 10, 80, 25)
        self._view_mode.show()

    def setupMenuBar(self):
        self._menubar = QtWidgets.QMenuBar()
        self.setMenuBar(self._menubar)

        file_menu = self._menubar.addMenu("File")
        self._close_action = file_menu.addAction(
            "Close", self.onClose, "Ctrl+W")

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

    def closeEvent(self, event):
        self.plugin.settings.setValue("window/geometry", self.saveGeometry())
        event.accept()

    def resizeEvent(self, event):
        len = 80
        self._view_mode.setGeometry(self.width() - 5 - len, 10, len, 25)

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
        self._file_name = self._load_thread.getFileName()
        self.updateWindowTitle()

        self._components = self._load_thread.getComponents()

        self._actor_to_comp_name = {}
        for name, comp in self._components.items():
            actor = comp.getActor()
            if actor is not None:
                actor.SetScale(0.99999)
                self._actors[name] = actor
                if self.renderMode() == self.SILHOUETTE:
                    property = actor.GetProperty()
                    property.LightingOff()
                    qclr = QtGui.QColor(255, 255, 255)
                    self._setPropertyColor(property, qclr)
                self._vtk_renderer.AddViewProp(actor)
                self._actor_to_comp_name[actor] = name

            silhouette_actor = comp.getSilhouetteActor()
            if silhouette_actor is not None:
                if self.renderMode() == self.SHADED:
                    silhouette_actor.VisibilityOff()
                self._silhouette_actors[name] = silhouette_actor
                self._vtk_renderer.AddViewProp(silhouette_actor)
                comp.setSilhouetteCamera(self._vtk_renderer.GetActiveCamera())
                property = silhouette_actor.GetProperty()
                property.SetColor([0, 0, 0])
                property.SetLineWidth(2)

            caption_actor = comp.getCaptionActor()
            if caption_actor is not None:
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
            if bounds is not None:
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
        actor = self._getComponentActor(component_name)
        if actor is None:
            return

        if visible:
            actor.VisibilityOn()

            if self.renderMode() == self.SILHOUETTE:
                actor = self._getComponentSilhouetteActor(component_name)
                actor.VisibilityOn()
        else:
            actor.VisibilityOff()

            if self.renderMode() == self.SILHOUETTE:
                actor = self._getComponentSilhouetteActor(component_name)
                actor.VisibilityOff()

        self._vtk_render_window.Render()

    def onComponentColorChanged(self, component_name, qcolor):
        self._component_color[component_name] = qcolor

        if self.renderMode() == self.SHADED:
            actor = self._getComponentActor(component_name)
            if actor is not None:
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
        if actor is None:
            return None
        else:
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

    def onClose(self):
        self.plugin.close()

    def renderMode(self):
        return self._render_mode

    def onShadedTriggered(self, checked):
        self._render_mode = self.SHADED

        for actor in self._actors.values():
            property = actor.GetProperty()
            property.LightingOn()
            comp_name = self._actor_to_comp_name[actor]
            qcolor = self._component_color[comp_name]
            self._setPropertyColor(property, qcolor)

        for actor in self._silhouette_actors.values():
            actor.VisibilityOff()

        self._vtk_render_window.Render()

    def onHiddenEdgesRemovedTriggered(self, checked):
        self._render_mode = self.SILHOUETTE

        for actor in self._actors.values():
            property = actor.GetProperty()
            property.LightingOff()
            self._setPropertyColor(property, QtGui.QColor(255, 255, 255))

        for actor in self._silhouette_actors.values():
            actor.VisibilityOn()
            property = actor.GetProperty()
            self._setPropertyColor(property, QtGui.QColor(0, 0, 0))
            property.SetLineWidth(3)

        self._vtk_render_window.Render()

    def updateWindowTitle(self):
        if self._file_name is None:
            self.setWindowTitle("Mesh Inspector")
        else:
            self.setWindowTitle("Mesh Inspector \u2014 {}".format(
                os.path.basename(self._file_name)))
