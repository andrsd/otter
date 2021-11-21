import os
import vtk
from PyQt5 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from otter.plugins.PluginWindowBase import PluginWindowBase
from otter.plugins.common.ExodusIIReader import ExodusIIReader
from otter.plugins.common.LoadFileEvent import LoadFileEvent
from otter.plugins.common.OSplitter import OSplitter
import otter.plugins.common as common
from otter.assets import Assets
from otter.plugins.mesh_inspector.InfoWindow import InfoWindow


class LoadThread(QtCore.QThread):
    """ Worker thread for loading ExodusII files """

    def __init__(self, file_name):
        super().__init__()
        self._reader = ExodusIIReader(file_name)

    def run(self):
        self._reader.load()

    def getReader(self):
        return self._reader


class MeshWindow(PluginWindowBase):
    """
    Window for displaying the mesh
    """

    fileLoaded = QtCore.pyqtSignal(object)
    boundsChanged = QtCore.pyqtSignal(list)

    SIDESET_CLR = [255/255, 173/255, 79/255]
    SIDESET_EDGE_CLR = [0.1, 0.1, 0.4]
    SIDESET_EDGE_WIDTH = 5
    NODESET_CLR = [168/255, 91/255, 2/255]

    SHADED = 0
    SHADED_WITH_EDGES = 1
    HIDDEN_EDGES_REMOVED = 2
    TRANSLUENT = 3

    def __init__(self, plugin):
        super().__init__(plugin)
        self._load_thread = None
        self._progress = None
        self._file_name = None

        self.setupWidgets()
        self.setupMenuBar()
        self.updateWindowTitle()

        state = self.plugin.settings.value("splitter/state")
        if state is not None:
            self._splitter.restoreState(state)

        self.setAcceptDrops(True)

        self.fileLoaded.connect(self._info_window.onFileLoaded)
        self.boundsChanged.connect(
            self._info_window.onBoundsChanged)
        self._info_window.blockVisibilityChanged.connect(
            self.onBlockVisibilityChanged)
        self._info_window.blockColorChanged.connect(
            self.onBlockColorChanged)
        self._info_window.sidesetVisibilityChanged.connect(
            self.onSidesetVisibilityChanged)
        self._info_window.nodesetVisibilityChanged.connect(
            self.onNodesetVisibilityChanged)
        self._info_window.dimensionsStateChanged.connect(
            self.onCubeAxisVisibilityChanged)
        self._info_window.orientationMarkerStateChanged.connect(
            self.onOrientationmarkerVisibilityChanged)

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

        self._setupOrientationMarker()
        self._setupCubeAxesActor()

        self.clear()
        self.show()

        self._update_timer = QtCore.QTimer()
        self._update_timer.timeout.connect(self.onUpdateWindow)
        self._update_timer.start(250)

        QtCore.QTimer.singleShot(1, self._updateViewModeLocation)

    def setupWidgets(self):
        self._splitter = OSplitter(QtCore.Qt.Horizontal, self)

        frame = QtWidgets.QFrame(self)
        self._vtk_widget = QVTKRenderWindowInteractor(frame)

        self._vtk_renderer = vtk.vtkRenderer()
        self._vtk_widget.GetRenderWindow().AddRenderer(self._vtk_renderer)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._vtk_widget)

        frame.setLayout(self._layout)
        frame.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                            QtWidgets.QSizePolicy.Expanding)

        self._splitter.addWidget(frame)
        self._splitter.setCollapsible(0, False)

        self._info_window = InfoWindow(self.plugin, self)
        self._splitter.addWidget(self._info_window)
        self._splitter.setCollapsible(1, True)

        self.setCentralWidget(self._splitter)

        # control layer
        self._view_menu = QtWidgets.QMenu()
        self._shaded_action = self._view_menu.addAction("Shaded")
        self._shaded_action.setCheckable(True)
        self._shaded_w_edges_action = self._view_menu.addAction(
            "Shaded with edges")
        self._shaded_w_edges_action.setCheckable(True)
        self._hidden_edges_removed_action = self._view_menu.addAction(
            "Hidden edges removed")
        self._hidden_edges_removed_action.setCheckable(True)
        self._transluent_action = self._view_menu.addAction(
            "Transluent")
        self._transluent_action.setCheckable(True)
        self._shaded_w_edges_action.setChecked(True)
        self._render_mode = self.SHADED_WITH_EDGES

        self._visual_repr = QtWidgets.QActionGroup(self._view_menu)
        self._visual_repr.addAction(self._shaded_action)
        self._visual_repr.addAction(self._shaded_w_edges_action)
        self._visual_repr.addAction(self._hidden_edges_removed_action)
        self._visual_repr.addAction(self._transluent_action)
        self._visual_repr.setExclusive(True)

        self._view_menu.addSeparator()
        self._perspective_action = self._view_menu.addAction("Perspective")
        self._perspective_action.setCheckable(True)
        self._perspective_action.setChecked(True)

        self._shaded_action.triggered.connect(self.onShadedTriggered)
        self._shaded_w_edges_action.triggered.connect(
            self.onShadedWithEdgesTriggered)
        self._hidden_edges_removed_action.triggered.connect(
            self.onHiddenEdgesRemovedTriggered)
        self._transluent_action.triggered.connect(self.onTransluentTriggered)
        self._perspective_action.toggled.connect(self.onPerspectiveToggled)

        self._view_mode = QtWidgets.QPushButton(frame)
        self._view_mode.setFixedSize(60, 32)
        self._view_mode.setIcon(Assets().icons['render-mode'])
        self._view_mode.setMenu(self._view_menu)
        self._view_mode.show()

    def setupMenuBar(self):
        file_menu = self._menubar.addMenu("File")
        self._new_action = file_menu.addAction(
            "New", self.onNewFile, "Ctrl+N")
        self._open_action = file_menu.addAction(
            "Open", self.onOpenFile, "Ctrl+O")
        file_menu.addSeparator()
        self._close_action = file_menu.addAction(
            "Close", self.onClose, "Ctrl+W")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # FIXME: first time through the width of widget #0 is non-sensical
        self._updateViewModeLocation()

    def _updateViewModeLocation(self):
        width = self._splitter.sizes()[0]
        self._view_mode.move(width - 5 - self._view_mode.width(), 10)

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

    def clear(self):
        self._block_actors = {}
        self._block_color = {}
        self._silhouette_actors = {}
        self._sideset_actors = {}
        self._nodeset_actors = {}
        self._block_bounds = {}
        self._vtk_renderer.RemoveAllViewProps()

    def loadFile(self, file_name):
        self.clear()

        self._progress = QtWidgets.QProgressDialog(
            "Loading {}...".format(os.path.basename(file_name)),
            None, 0, 0, self)
        self._progress.setWindowModality(QtCore.Qt.WindowModal)
        self._progress.setMinimumDuration(0)
        self._progress.show()

        self._load_thread = LoadThread(file_name)
        self._load_thread.finished.connect(self.onLoadFinished)
        self._load_thread.start(QtCore.QThread.IdlePriority)

    def onLoadFinished(self):
        reader = self._load_thread.getReader()

        self._addBlockActors()
        self._addSidesetActors()
        self._addNodesetActors()

        gmin = QtGui.QVector3D(float('inf'), float('inf'), float('inf'))
        gmax = QtGui.QVector3D(float('-inf'), float('-inf'), float('-inf'))
        for bnd in self._block_bounds.values():
            bmin, bmax = bnd
            gmin = common.point_min(bmin, gmin)
            gmax = common.point_max(bmax, gmax)
        bnds = [gmin.x(), gmax.x(), gmin.y(), gmax.y(), gmin.z(), gmax.z()]

        self._calcCenterOfMass(bnds)
        self._cube_axes_actor.SetBounds(*bnds)
        self._vtk_renderer.AddViewProp(self._cube_axes_actor)

        self._vtk_renderer.ResetCamera()
        self._vtk_renderer.GetActiveCamera().Zoom(1.5)

        params = {
            'blocks': reader.getBlocks(),
            'sidesets': reader.getSideSets(),
            'nodesets': reader.getNodeSets(),
            'total_elems': reader.getTotalNumberOfElements(),
            'total_nodes': reader.getTotalNumberOfNodes()
        }
        self.fileLoaded.emit(params)
        self.boundsChanged.emit(bnds)

        self._file_name = reader.getFileName()
        self.updateWindowTitle()

        self._progress.hide()
        self._progress = None

    def _addBlockActors(self):
        camera = self._vtk_renderer.GetActiveCamera()
        reader = self._load_thread.getReader()

        for index, binfo in enumerate(reader.getBlocks()):
            eb = vtk.vtkExtractBlock()
            eb.SetInputConnection(reader.getVtkOutputPort())
            eb.AddIndex(binfo.multiblock_index)
            eb.Update()

            bounds = self._getBlocksBounds(eb)
            self._block_bounds[binfo.number] = bounds

            geometry = vtk.vtkCompositeDataGeometryFilter()
            geometry.SetInputConnection(0, eb.GetOutputPort(0))
            geometry.Update()

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(geometry.GetOutputPort())
            mapper.SetScalarModeToUsePointFieldData()
            mapper.InterpolateScalarsBeforeMappingOn()

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.SetScale(0.99999)
            actor.VisibilityOn()
            self._vtk_renderer.AddViewProp(actor)

            self._block_color[binfo.number] = [1, 1, 1]
            self._setBlockActorProperties(binfo.number, actor)
            self._block_actors[binfo.number] = actor

            silhouette = vtk.vtkPolyDataSilhouette()
            silhouette.SetInputData(mapper.GetInput())
            silhouette.SetCamera(camera)

            silhouette_mapper = vtk.vtkPolyDataMapper()
            silhouette_mapper.SetInputConnection(silhouette.GetOutputPort())

            silhouette_actor = vtk.vtkActor()
            silhouette_actor.SetMapper(silhouette_mapper)
            if (self.renderMode() == self.HIDDEN_EDGES_REMOVED or
                    self.renderMode() == self.TRANSLUENT):
                silhouette_actor.VisibilityOn()
                self._setSilhouetteActorProperties(silhouette_actor)
            else:
                silhouette_actor.VisibilityOff()
            self._vtk_renderer.AddViewProp(silhouette_actor)

            self._silhouette_actors[binfo.number] = silhouette_actor

    def _addSidesetActors(self):
        reader = self._load_thread.getReader()

        for index, finfo in enumerate(reader.getSideSets()):
            eb = vtk.vtkExtractBlock()
            eb.SetInputConnection(reader.getVtkOutputPort())
            eb.AddIndex(finfo.multiblock_index)
            eb.Update()

            geometry = vtk.vtkCompositeDataGeometryFilter()
            geometry.SetInputConnection(0, eb.GetOutputPort(0))
            geometry.Update()

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(geometry.GetOutputPort())
            mapper.SetScalarModeToUsePointFieldData()
            mapper.InterpolateScalarsBeforeMappingOn()

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.VisibilityOff()
            self._vtk_renderer.AddViewProp(actor)

            property = actor.GetProperty()
            property.SetRepresentationToSurface()
            self._setSideSetActorProperties(actor)

            self._sideset_actors[finfo.number] = actor

    def _addNodesetActors(self):
        reader = self._load_thread.getReader()

        for index, ninfo in enumerate(reader.getNodeSets()):
            eb = vtk.vtkExtractBlock()
            eb.SetInputConnection(reader.getVtkOutputPort())
            eb.AddIndex(ninfo.multiblock_index)
            eb.Update()

            geometry = vtk.vtkCompositeDataGeometryFilter()
            geometry.SetInputConnection(0, eb.GetOutputPort(0))
            geometry.Update()

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(geometry.GetOutputPort())
            mapper.SetScalarModeToUsePointFieldData()
            mapper.InterpolateScalarsBeforeMappingOn()

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.VisibilityOff()
            self._setNodeSetActorProperties(actor)
            self._vtk_renderer.AddViewProp(actor)

            self._nodeset_actors[ninfo.number] = actor

    def _calcCenterOfMass(self, bnds):
        self._com = [
            -(bnds[0] + bnds[1]) / 2,
            -(bnds[2] + bnds[3]) / 2,
            -(bnds[4] + bnds[5]) / 2
        ]

    def _setupCubeAxesActor(self):
        self._cube_axes_actor = vtk.vtkCubeAxesActor()
        self._cube_axes_actor.VisibilityOff()
        self._cube_axes_actor.SetCamera(self._vtk_renderer.GetActiveCamera())
        self._cube_axes_actor.SetGridLineLocation(
            vtk.vtkCubeAxesActor.VTK_GRID_LINES_ALL)
        self._cube_axes_actor.SetFlyMode(
            vtk.vtkCubeAxesActor.VTK_FLY_OUTER_EDGES)

    def _getBlockActor(self, block_id):
        return self._block_actors[block_id]

    def _getSidesetActor(self, sideset_id):
        return self._sideset_actors[sideset_id]

    def _getNodesetActor(self, nodeset_id):
        return self._nodeset_actors[nodeset_id]

    def _getSilhouetteActor(self, block_id):
        return self._silhouette_actors[block_id]

    def renderMode(self):
        return self._render_mode

    def _setupOrientationMarker(self):
        axes = vtk.vtkAxesActor()
        self._ori_marker = vtk.vtkOrientationMarkerWidget()
        self._ori_marker.SetOrientationMarker(axes)
        self._ori_marker.SetViewport(0.8, 0, 1.0, 0.2)
        self._ori_marker.SetInteractor(self._vtk_interactor)
        self._ori_marker.SetEnabled(1)
        self._ori_marker.SetInteractive(False)

    def onBlockVisibilityChanged(self, block_id, visible):
        actor = self._getBlockActor(block_id)
        if visible:
            actor.VisibilityOn()
        else:
            actor.VisibilityOff()

        if self.renderMode() == self.HIDDEN_EDGES_REMOVED:
            actor = self._getSilhouetteActor(block_id)
            if visible:
                actor.VisibilityOn()
            else:
                actor.VisibilityOff()

    def onBlockColorChanged(self, block_id, qcolor):
        clr = [qcolor.redF(), qcolor.greenF(), qcolor.blueF()]
        self._block_color[block_id] = clr

        actor = self._getBlockActor(block_id)
        property = actor.GetProperty()
        if self.renderMode() == self.HIDDEN_EDGES_REMOVED:
            property.SetColor([1, 1, 1])
        else:
            property.SetColor(clr)

    def onSidesetVisibilityChanged(self, sideset_id, visible):
        actor = self._getSidesetActor(sideset_id)
        if visible:
            actor.VisibilityOn()
        else:
            actor.VisibilityOff()

    def onNodesetVisibilityChanged(self, nodeset_id, visible):
        actor = self._getNodesetActor(nodeset_id)
        if visible:
            actor.VisibilityOn()
        else:
            actor.VisibilityOff()

    def _getBlocksBounds(self, extract_block):
        glob_min = QtGui.QVector3D(float('inf'), float('inf'), float('inf'))
        glob_max = QtGui.QVector3D(float('-inf'), float('-inf'), float('-inf'))
        for i in range(extract_block.GetOutput().GetNumberOfBlocks()):
            current = extract_block.GetOutput().GetBlock(i)
            if isinstance(current, vtk.vtkUnstructuredGrid):
                bnd = current.GetBounds()
                bnd_min = QtGui.QVector3D(bnd[0], bnd[2], bnd[4])
                bnd_max = QtGui.QVector3D(bnd[1], bnd[3], bnd[5])
                glob_min = common.point_min(bnd_min, glob_min)
                glob_max = common.point_max(bnd_max, glob_max)

            elif isinstance(current, vtk.vtkMultiBlockDataSet):
                for j in range(current.GetNumberOfBlocks()):
                    bnd = current.GetBlock(j).GetBounds()
                    bnd_min = QtGui.QVector3D(bnd[0], bnd[2], bnd[4])
                    bnd_max = QtGui.QVector3D(bnd[1], bnd[3], bnd[5])
                    glob_min = common.point_min(bnd_min, glob_min)
                    glob_max = common.point_max(bnd_max, glob_max)

        return (glob_min, glob_max)

    def onCubeAxisVisibilityChanged(self, visible):
        if visible:
            self._cube_axes_actor.VisibilityOn()
        else:
            self._cube_axes_actor.VisibilityOff()

    def onOrientationmarkerVisibilityChanged(self, visible):
        if visible:
            self._ori_marker.EnabledOn()
        else:
            self._ori_marker.EnabledOff()

    def onOpenFile(self):
        file_name, f = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open File',
            "",
            "ExodusII files (*.e *.exo)")
        if file_name:
            self.loadFile(file_name)

    def onNewFile(self):
        self.clear()
        self.fileLoaded.emit(None)
        self.boundsChanged.emit([])
        self._file_name = None
        self.updateWindowTitle()

    def updateWindowTitle(self):
        if self._file_name is None:
            self.setWindowTitle("Mesh Inspector")
        else:
            self.setWindowTitle("Mesh Inspector \u2014 {}".format(
                os.path.basename(self._file_name)))

    def onShadedTriggered(self, checked):
        self._render_mode = self.SHADED
        for block_id, actor in self._block_actors.items():
            self._setBlockActorProperties(block_id, actor)
        for actor in self._sideset_actors.values():
            self._setSideSetActorProperties(actor)
        for actor in self._silhouette_actors.values():
            actor.VisibilityOff()

    def onShadedWithEdgesTriggered(self, checked):
        self._render_mode = self.SHADED_WITH_EDGES
        for block_id, actor in self._block_actors.items():
            self._setBlockActorProperties(block_id, actor)
        for actor in self._sideset_actors.values():
            self._setSideSetActorProperties(actor)
        for actor in self._silhouette_actors.values():
            actor.VisibilityOff()

    def onHiddenEdgesRemovedTriggered(self, checked):
        self._render_mode = self.HIDDEN_EDGES_REMOVED
        for block_id, actor in self._block_actors.items():
            self._setBlockActorProperties(block_id, actor)
        for actor in self._sideset_actors.values():
            self._setSideSetActorProperties(actor)
        for actor in self._silhouette_actors.values():
            actor.VisibilityOn()
            self._setSilhouetteActorProperties(actor)

    def onTransluentTriggered(self, checked):
        self._render_mode = self.TRANSLUENT
        for block_id, actor in self._block_actors.items():
            self._setBlockActorProperties(block_id, actor)
        for actor in self._sideset_actors.values():
            self._setSideSetActorProperties(actor)
        for actor in self._silhouette_actors.values():
            actor.VisibilityOn()
            self._setSilhouetteActorProperties(actor)

    def onPerspectiveToggled(self, checked):
        if checked:
            camera = self._vtk_renderer.GetActiveCamera()
            camera.ParallelProjectionOff()
        else:
            camera = self._vtk_renderer.GetActiveCamera()
            camera.ParallelProjectionOn()

    def _setBlockActorProperties(self, block_id, actor):
        property = actor.GetProperty()
        property.SetAmbient(0.4)
        property.SetDiffuse(0.6)
        if self.renderMode() == self.SHADED:
            property.SetColor(self._block_color[block_id])
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(False)
        elif self.renderMode() == self.SHADED_WITH_EDGES:
            property.SetColor(self._block_color[block_id])
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(True)
            property.SetEdgeColor(self.SIDESET_EDGE_CLR)
            property.SetLineWidth(2)
        elif self.renderMode() == self.HIDDEN_EDGES_REMOVED:
            property.SetColor([1, 1, 1])
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(False)
        elif self.renderMode() == self.TRANSLUENT:
            property.SetColor(self._block_color[block_id])
            property.SetOpacity(0.33)
            property.SetEdgeVisibility(False)

    def _setSideSetActorProperties(self, actor):
        property = actor.GetProperty()
        if self.renderMode() == self.SHADED:
            property.SetColor(self.SIDESET_CLR)
            property.SetEdgeVisibility(False)
            property.SetEdgeColor(self.SIDESET_EDGE_CLR)
            property.SetLineWidth(self.SIDESET_EDGE_WIDTH)
            property.LightingOff()
        elif self.renderMode() == self.SHADED_WITH_EDGES:
            property = actor.GetProperty()
            property.SetColor(self.SIDESET_CLR)
            property.SetEdgeVisibility(False)
            property.SetEdgeColor(self.SIDESET_EDGE_CLR)
            property.SetLineWidth(self.SIDESET_EDGE_WIDTH)
            property.LightingOff()
        elif self.renderMode() == self.HIDDEN_EDGES_REMOVED:
            property = actor.GetProperty()
            property.SetColor(self.SIDESET_CLR)
            property.SetEdgeVisibility(False)
            property.LightingOff()
        elif self.renderMode() == self.TRANSLUENT:
            property = actor.GetProperty()
            property.SetColor(self.SIDESET_CLR)
            property.SetEdgeVisibility(False)
            property.LightingOff()

    def _setNodeSetActorProperties(self, actor):
        property = actor.GetProperty()
        property.SetRepresentationToPoints()
        property.SetRenderPointsAsSpheres(True)
        property.SetVertexVisibility(True)
        property.SetEdgeVisibility(False)
        property.SetPointSize(10)
        property.SetColor(self.NODESET_CLR)
        property.SetOpacity(1)
        property.SetAmbient(1)
        property.SetDiffuse(0)

    def _setSilhouetteActorProperties(self, actor):
        property = actor.GetProperty()
        property.SetColor([0, 0, 0])
        property.SetLineWidth(3)

    def onUpdateWindow(self):
        self._vtk_render_window.Render()

    def event(self, e):
        if e.type() == LoadFileEvent.TYPE:
            self.loadFile(e.fileName())
            return True
        else:
            return super().event(e)

    def closeEvent(self, event):
        self.plugin.settings.setValue(
            "splitter/state", self._splitter.saveState())
        super().closeEvent(event)
