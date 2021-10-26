import os
import vtk
import math
from PyQt5 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from otter.plugins.model_inspector.InputReader import InputReader
import otter.plugins.common as common
from otter.plugins.common.OtterInteractorStyle import OtterInteractorStyle
from otter.assets import Assets


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
    SHADED_WITH_EDGES = 2
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
        self._render_mode = self.plugin.settings.value(
            "window/render_mode", self.SHADED)
        self._bnds = None

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
        self._update_timer = QtCore.QTimer()
        self._update_timer.timeout.connect(self.onUpdateWindow)
        self._update_timer.start(250)

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
        self._shaded_with_edges_action = self._view_menu.addAction(
            "Shaded with edges")
        self._shaded_with_edges_action.setCheckable(True)
        self._hidden_edges_removed_action = self._view_menu.addAction(
            "Hidden edges removed")
        self._hidden_edges_removed_action.setCheckable(True)
        if self._render_mode == self.SHADED:
            self._shaded_action.setChecked(True)
        elif self._render_mode == self.SILHOUETTE:
            self._hidden_edges_removed_action.setChecked(True)
        else:
            self._shaded_with_edges_action.setChecked(True)

        self._visual_repr = QtWidgets.QActionGroup(self._view_menu)
        self._visual_repr.addAction(self._shaded_action)
        self._visual_repr.addAction(self._shaded_with_edges_action)
        self._visual_repr.addAction(self._hidden_edges_removed_action)
        self._visual_repr.setExclusive(True)

        self._view_menu.addSeparator()
        self._perspective_action = self._view_menu.addAction("Perspective")
        self._perspective_action.setCheckable(True)
        perspective = self.plugin.settings.value("window/perspective", True)
        self._perspective_action.setChecked(perspective)
        self.onPerspectiveToggled(perspective)

        self._shaded_action.triggered.connect(self.onShadedTriggered)
        self._shaded_with_edges_action.triggered.connect(
            self.onShadedWithEdgesTriggered)
        self._hidden_edges_removed_action.triggered.connect(
            self.onHiddenEdgesRemovedTriggered)
        self._perspective_action.toggled.connect(self.onPerspectiveToggled)

        self._view_mode = QtWidgets.QPushButton(self._frame)
        self._view_mode.setFixedSize(60, 32)
        self._view_mode.setIcon(Assets().icons['render-mode'])
        self._view_mode.setMenu(self._view_menu)
        self._view_mode.setGeometry(10, 10, 80, 25)
        self._view_mode.show()

    def setupMenuBar(self):
        self._menubar = QtWidgets.QMenuBar()
        self.setMenuBar(self._menubar)

        file_menu = self._menubar.addMenu("File")
        self._new_action = file_menu.addAction(
            "New", self.onNewFile, "Ctrl+N")
        self._open_action = file_menu.addAction(
            "Open", self.onOpenFile, "Ctrl+O")
        file_menu.addSeparator()
        self._close_action = file_menu.addAction(
            "Close", self.onClose, "Ctrl+W")

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

    def closeEvent(self, event):
        self.plugin.settings.setValue("window/geometry", self.saveGeometry())
        self.plugin.settings.setValue("window/render_mode", self.renderMode())
        self.plugin.settings.setValue(
            "window/perspective", self._perspective_action.isChecked())
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

    def clear(self):
        self._components = {}
        self._actor_to_comp_name = {}
        self._actors = {}
        self._silhouette_actors = {}
        self._component_bounds = {}
        self._bnds = None
        self._vtk_renderer.RemoveAllViewProps()

    def loadFile(self, file_name):
        self.clear()

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
            render_mode = self.renderMode()
            if actor is not None:
                actor.SetScale(0.99999)
                self._actors[name] = actor
                if render_mode in [self.SILHOUETTE, self.SHADED_WITH_EDGES]:
                    property = actor.GetProperty()
                    property.LightingOff()
                    qclr = QtGui.QColor(255, 255, 255)
                    self._setPropertyColor(property, qclr)
                self._vtk_renderer.AddViewProp(actor)
                self._actor_to_comp_name[actor] = name

            silhouette_actor = comp.getSilhouetteActor()
            if silhouette_actor is not None:
                if render_mode == self.SHADED:
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

        self._bnds = self._computeBounds()
        self.boundsChanged.emit(self._bnds)
        self._cube_axes_actor = self._setupCubeAxisActor(self._bnds)

        self._vtk_renderer.ResetCamera()
        self._vtk_renderer.GetActiveCamera().Zoom(1.5)

        self.fileLoaded.emit(self._components.values())

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

            if self.renderMode() in [self.SILHOUETTE, self.SHADED_WITH_EDGES]:
                actor = self._getComponentSilhouetteActor(component_name)
                actor.VisibilityOn()
        else:
            actor.VisibilityOff()

            if self.renderMode() in [self.SILHOUETTE, self.SHADED_WITH_EDGES]:
                actor = self._getComponentSilhouetteActor(component_name)
                actor.VisibilityOff()

        if self._show_captions:
            actor = self._caption_actors[component_name]
            actor.SetVisibility(visible)

    def onComponentColorChanged(self, component_name, qcolor):
        self._component_color[component_name] = qcolor

        if self.renderMode() in [self.SHADED, self.SHADED_WITH_EDGES]:
            actor = self._getComponentActor(component_name)
            if actor is not None:
                property = actor.GetProperty()
                self._setPropertyColor(property, qcolor)

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

    def onOrientationmarkerVisibilityChanged(self, visible):
        if visible:
            self._ori_marker.EnabledOn()
        else:
            self._ori_marker.EnabledOff()

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

        for comp_name, actor in self._actors.items():
            visible = actor.GetVisibility()
            if visible:
                caption_actor = self._caption_actors[comp_name]
                caption_actor.SetVisibility(state)

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

    def onShadedWithEdgesTriggered(self, checked):
        self._render_mode = self.SHADED_WITH_EDGES

        for actor in self._actors.values():
            property = actor.GetProperty()
            property.LightingOn()
            comp_name = self._actor_to_comp_name[actor]
            qcolor = self._component_color[comp_name]
            self._setPropertyColor(property, qcolor)

            visible = actor.GetVisibility()
            if visible:
                sil_actor = self._getComponentSilhouetteActor(comp_name)
                sil_actor.VisibilityOn()
                property = sil_actor.GetProperty()
                self._setPropertyColor(property, QtGui.QColor(0, 0, 0))
                property.SetLineWidth(3)

    def onHiddenEdgesRemovedTriggered(self, checked):
        self._render_mode = self.SILHOUETTE

        for comp_name, actor in self._actors.items():
            property = actor.GetProperty()
            property.LightingOff()
            self._setPropertyColor(property, QtGui.QColor(255, 255, 255))

            visible = actor.GetVisibility()
            if visible:
                sil_actor = self._getComponentSilhouetteActor(comp_name)
                sil_actor.VisibilityOn()
                property = sil_actor.GetProperty()
                self._setPropertyColor(property, QtGui.QColor(0, 0, 0))
                property.SetLineWidth(3)

    def onPerspectiveToggled(self, checked):
        if checked:
            camera = self._vtk_renderer.GetActiveCamera()
            camera.ParallelProjectionOff()
        else:
            camera = self._vtk_renderer.GetActiveCamera()
            camera.ParallelProjectionOn()

    def updateWindowTitle(self):
        if self._file_name is None:
            self.setWindowTitle("Model Inspector")
        else:
            self.setWindowTitle("Model Inspector \u2014 {}".format(
                os.path.basename(self._file_name)))

    def onNewFile(self):
        self.clear()
        self.fileLoaded.emit(None)
        self.boundsChanged.emit([])
        self._file_name = None
        self.updateWindowTitle()

    def onOpenFile(self):
        file_name, f = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open File',
            "",
            "THM input files (*.i)")
        if file_name:
            self.loadFile(file_name)

    def _setupCamera(self, focal_point, position, view_up):
        camera = self._vtk_renderer.GetActiveCamera()
        camera.SetFocalPoint(focal_point)
        camera.SetPosition(position)
        camera.SetViewUp(view_up)

    def _cameraLocation(self, focal_point, distance, direction):
        # normalize the direction
        d = math.sqrt(direction[0] * direction[0] +
                      direction[1] * direction[1] +
                      direction[2] * direction[2])
        direction = [i / d for i in direction]

        vec = [distance * i for i in direction]
        pos = [
            focal_point[0] + vec[0],
            focal_point[1] + vec[1],
            focal_point[2] + vec[2]
        ]
        return pos

    def _setCameraPostion(self, cam_pos):
        camera = self._vtk_renderer.GetActiveCamera()
        view_angle = camera.GetViewAngle() * math.pi / 180.

        if self._bnds is None:
            focal_pt = [0, 0, 0]
            height_x = 1
            height_y = 1
            height_z = 1
        else:
            focal_pt = [
                (self._bnds[0] + self._bnds[1]) / 2,
                (self._bnds[2] + self._bnds[3]) / 2,
                (self._bnds[4] + self._bnds[5]) / 2
            ]
            height_x = 1.05 * (self._bnds[1] - self._bnds[0])
            height_y = 1.05 * (self._bnds[3] - self._bnds[2])
            height_z = 1.05 * (self._bnds[5] - self._bnds[4])

        if cam_pos == '-x':
            distance = height_z / view_angle
            pos = self._cameraLocation(focal_pt, distance, [-1, 0, 0])
            view_up = [0, 0, 1]
            thickness = distance + height_x
        elif cam_pos == '+x':
            distance = height_z / view_angle
            pos = self._cameraLocation(focal_pt, distance, [1, 0, 0])
            view_up = [0, 0, 1]
            thickness = distance + height_x
        elif cam_pos == '-y':
            distance = height_z / view_angle
            pos = self._cameraLocation(focal_pt, distance, [0, -1, 0])
            view_up = [0, 0, 1]
            thickness = distance + height_y
        elif cam_pos == '+y':
            distance = height_z / view_angle
            pos = self._cameraLocation(focal_pt, distance, [0, 1, 0])
            view_up = [0, 0, 1]
            thickness = distance + height_y
        elif cam_pos == '-z':
            distance = height_y / view_angle
            pos = self._cameraLocation(focal_pt, distance, [0, 0, -1])
            view_up = [0, 1, 0]
            thickness = distance + height_z
        elif cam_pos == '+z':
            distance = height_y / view_angle
            pos = self._cameraLocation(focal_pt, distance, [0, 0, 1])
            view_up = [0, 1, 0]
            thickness = distance + height_z

        self._setupCamera(focal_pt, pos, view_up)
        camera.SetThickness(thickness)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_1:
            self._setCameraPostion("-x")
        elif event.key() == QtCore.Qt.Key_2:
            self._setCameraPostion("+x")
        elif event.key() == QtCore.Qt.Key_3:
            self._setCameraPostion("-y")
        elif event.key() == QtCore.Qt.Key_4:
            self._setCameraPostion("+y")
        elif event.key() == QtCore.Qt.Key_5:
            self._setCameraPostion("-z")
        elif event.key() == QtCore.Qt.Key_6:
            self._setCameraPostion("+z")

    def onUpdateWindow(self):
        self._vtk_render_window.Render()
