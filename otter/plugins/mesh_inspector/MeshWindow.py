import os
import vtk
from PyQt5 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from otter.plugins.PluginWindowBase import PluginWindowBase
from otter.plugins.common.OtterInteractorStyle import OtterInteractorStyle
from otter.plugins.common.ExodusIIReader import ExodusIIReader
from otter.plugins.common.VTKReader import VTKReader
from otter.plugins.common.PetscHDF5Reader import PetscHDF5Reader
from otter.plugins.common.LoadFileEvent import LoadFileEvent
from otter.plugins.common.FileChangedNotificationWidget import \
    FileChangedNotificationWidget
import otter.plugins.common as common
from otter.assets import Assets
from otter.plugins.mesh_inspector.InfoWindow import InfoWindow
from otter.plugins.mesh_inspector.SelectedMeshEntityInfoWidget import \
    SelectedMeshEntityInfoWidget
from otter.plugins.mesh_inspector.Selection import Selection


class LoadThread(QtCore.QThread):
    """ Worker thread for loading ExodusII files """

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


class MeshWindow(PluginWindowBase):
    """
    Window for displaying the mesh
    """

    fileLoaded = QtCore.pyqtSignal(object)
    boundsChanged = QtCore.pyqtSignal(list)

    SIDESET_CLR = QtGui.QColor(255, 173, 79)
    SIDESET_EDGE_CLR = QtGui.QColor(26, 26, 102)
    SIDESET_EDGE_WIDTH = 5
    NODESET_CLR = QtGui.QColor(168, 91, 2)

    SELECTION_CLR = QtGui.QColor(255, 173, 79)
    SELECTION_EDGE_CLR = QtGui.QColor(179, 95, 0)

    SHADED = 0
    SHADED_WITH_EDGES = 1
    HIDDEN_EDGES_REMOVED = 2
    TRANSLUENT = 3

    MODE_SELECT_BLOCKS = 0
    MODE_SELECT_CELLS = 1
    MODE_SELECT_POINTS = 2

    def __init__(self, plugin):
        super().__init__(plugin)
        self._load_thread = None
        self._progress = None
        self._file_name = None
        self._file_watcher = QtCore.QFileSystemWatcher()
        self._selected_block = None

        self.setupWidgets()
        self.setupMenuBar()
        self.updateWindowTitle()
        self.updateMenuBar()

        self.setAcceptDrops(True)

        self.connectSignals()
        self.setupVtk()

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
        self._vtk_widget = QVTKRenderWindowInteractor(self)
        self._vtk_renderer = vtk.vtkRenderer()
        self._vtk_widget.GetRenderWindow().AddRenderer(self._vtk_renderer)

        self.setCentralWidget(self._vtk_widget)

        self._info_window = InfoWindow(self.plugin, self)
        self._info_window.show()

        self.setupViewModeWidget(self)
        self.setupFileChangedNotificationWidget()
        self._selected_mesh_ent_info = SelectedMeshEntityInfoWidget(self)
        self._selected_mesh_ent_info.setVisible(False)

        self.deselect_sc = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_Space), self)
        self.deselect_sc.activated.connect(self.onDeselect)

    def setupViewModeWidget(self, frame):
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

        self._view_menu.addSeparator()
        self._ori_marker_action = self._view_menu.addAction(
            "Orientation marker")
        self._ori_marker_action.setCheckable(True)
        self._ori_marker_action.setChecked(True)

        self._shaded_action.triggered.connect(self.onShadedTriggered)
        self._shaded_w_edges_action.triggered.connect(
            self.onShadedWithEdgesTriggered)
        self._hidden_edges_removed_action.triggered.connect(
            self.onHiddenEdgesRemovedTriggered)
        self._transluent_action.triggered.connect(self.onTransluentTriggered)
        self._perspective_action.toggled.connect(self.onPerspectiveToggled)
        self._ori_marker_action.toggled.connect(
            self.onOrientationmarkerVisibilityChanged)

        self._view_mode = QtWidgets.QPushButton(frame)
        self._view_mode.setFixedSize(60, 32)
        self._view_mode.setIcon(Assets().icons['render-mode'])
        self._view_mode.setMenu(self._view_menu)
        self._view_mode.show()

    def setupFileChangedNotificationWidget(self):
        self._file_changed_notification = FileChangedNotificationWidget(self)
        self._file_changed_notification.setVisible(False)
        self._file_changed_notification.reload.connect(self.onReloadFile)

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

        view_menu = self._menubar.addMenu("View")
        self._view_info_wnd_action = view_menu.addAction(
            "Info window", self.onViewInfoWindow)
        self._view_info_wnd_action.setCheckable(True)

        tools_menu = self._menubar.addMenu("Tools")
        self.setupSelectModeMenu(tools_menu)

    def setupSelectModeMenu(self, tools_menu):
        select_menu = tools_menu.addMenu("Select mode")
        self._mode_select_action_group = QtWidgets.QActionGroup(self)
        self._select_mode = self.plugin.settings.value(
            "tools/select_mode", self.MODE_SELECT_BLOCKS)
        mode_actions = [
            {
                'name': 'Blocks',
                'mode': self.MODE_SELECT_BLOCKS
            },
            {
                'name': 'Cells',
                'mode': self.MODE_SELECT_CELLS
            },
            {
                'name': 'Points',
                'mode': self.MODE_SELECT_POINTS
            }
        ]
        for ma in mode_actions:
            name = ma['name']
            mode = ma['mode']
            action = select_menu.addAction(name)
            action.setCheckable(True)
            action.setData(mode)
            self._mode_select_action_group.addAction(action)
            if mode == self._select_mode:
                action.setChecked(True)

        self._mode_select_action_group.triggered.connect(
            self.onSelectModeTriggered)

    def updateMenuBar(self):
        self._view_info_wnd_action.setChecked(self._info_window.isVisible())

    def connectSignals(self):
        self.fileLoaded.connect(self._info_window.onFileLoaded)
        self.boundsChanged.connect(
            self._info_window.onBoundsChanged)
        self._info_window.blockVisibilityChanged.connect(
            self.onBlockVisibilityChanged)
        self._info_window.blockColorChanged.connect(
            self.onBlockColorChanged)
        self._info_window.blockSelectionChanged.connect(
            self.onBlockSelectionChanged)
        self._info_window.sidesetVisibilityChanged.connect(
            self.onSidesetVisibilityChanged)
        self._info_window.sidesetSelectionChanged.connect(
            self.onSidesetSelectionChanged)
        self._info_window.nodesetVisibilityChanged.connect(
            self.onNodesetVisibilityChanged)
        self._info_window.nodesetSelectionChanged.connect(
            self.onNodesetSelectionChanged)
        self._info_window.dimensionsStateChanged.connect(
            self.onCubeAxisVisibilityChanged)
        self._file_watcher.fileChanged.connect(self.onFileChanged)

    def setupVtk(self):
        self._vtk_render_window = self._vtk_widget.GetRenderWindow()
        self._vtk_interactor = self._vtk_render_window.GetInteractor()

        self._vtk_interactor.SetInteractorStyle(OtterInteractorStyle(self))

        # TODO: set background from preferences/templates
        self._vtk_renderer.SetGradientBackground(True)
        bkgnd = common.qcolor2vtk(QtGui.QColor(82, 87, 110))
        self._vtk_renderer.SetBackground(bkgnd)
        self._vtk_renderer.SetBackground2(bkgnd)
        # set anti-aliasing on
        self._vtk_renderer.SetUseFXAA(True)
        self._vtk_render_window.SetMultiSamples(1)

        self._vtk_widget.AddObserver('StartInteractionEvent',
                                     self.onStartInteraction)
        self._vtk_widget.AddObserver('EndInteractionEvent',
                                     self.onEndInteraction)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._updateViewModeLocation()

    def getRenderWindowWidth(self):
        return self.geometry().width()

    def _updateViewModeLocation(self):
        width = self.getRenderWindowWidth()
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
        self._block_info = {}
        self._silhouette_actors = {}
        self._sideset_actors = {}
        self._sideset_info = {}
        self._nodeset_actors = {}
        self._nodeset_info = {}
        self._vtk_renderer.RemoveAllViewProps()

        watched_files = self._file_watcher.files()
        for file in watched_files:
            self._file_watcher.removePath(file)

        self._selection = None

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
        for nfo in self._block_info.values():
            bmin, bmax = nfo['bounds']
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
        self.addToRecentFiles(self._file_name)
        self._file_watcher.addPath(self._file_name)
        self._file_changed_notification.setFileName(self._file_name)

        self._selection = Selection(self._geometry.GetOutput())
        actor = self._selection.getActor()
        self._vtk_renderer.AddActor(actor)
        self._setSelectionActorProperties(actor)

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
            do = eb.GetOutput()
            bounds = self._getBlocksBounds(eb)

            self._block_info[binfo.number] = {
                'cells': do.GetNumberOfCells(),
                'points': do.GetNumberOfPoints(),
                'bounds': bounds
            }

            geometry = vtk.vtkCompositeDataGeometryFilter()
            geometry.SetInputConnection(0, eb.GetOutputPort(0))
            geometry.Update()
            # FIXME: make this work with multiple blocks
            self._geometry = geometry

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
            do = eb.GetOutput()
            self._sideset_info[finfo.number] = {
                'cells': do.GetNumberOfCells(),
                'points': do.GetNumberOfPoints()
            }

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
            do = eb.GetOutput()
            self._nodeset_info[ninfo.number] = {
                'points': do.GetNumberOfPoints()
            }

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

        if (self.renderMode() == self.HIDDEN_EDGES_REMOVED or
                self.renderMode() == self.TRANSLUENT):
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
            "ExodusII files (*.e *.exo);;"
            "HDF5 PETSc files (*.h5);;"
            "VTK Unstructured Grid files (*.vtk)")
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
            selected = self._selected_block == block_id
            self._setBlockActorProperties(block_id, actor, selected)
        for actor in self._sideset_actors.values():
            self._setSideSetActorProperties(actor)
        for actor in self._silhouette_actors.values():
            actor.VisibilityOff()

    def onShadedWithEdgesTriggered(self, checked):
        self._render_mode = self.SHADED_WITH_EDGES
        for block_id, actor in self._block_actors.items():
            selected = self._selected_block == block_id
            self._setBlockActorProperties(block_id, actor, selected)
        for actor in self._sideset_actors.values():
            self._setSideSetActorProperties(actor)
        for actor in self._silhouette_actors.values():
            actor.VisibilityOff()

    def onHiddenEdgesRemovedTriggered(self, checked):
        self._render_mode = self.HIDDEN_EDGES_REMOVED
        for block_id, actor in self._block_actors.items():
            selected = self._selected_block == block_id
            self._setBlockActorProperties(block_id, actor, selected)
            sil_act = self._getSilhouetteActor(block_id)
            self._setSilhouetteActorProperties(sil_act)
            sil_act.SetVisibility(actor.GetVisibility())
        for actor in self._sideset_actors.values():
            self._setSideSetActorProperties(actor)

    def onTransluentTriggered(self, checked):
        self._render_mode = self.TRANSLUENT
        for block_id, actor in self._block_actors.items():
            selected = self._selected_block == block_id
            self._setBlockActorProperties(block_id, actor, selected)
            sil_act = self._getSilhouetteActor(block_id)
            self._setSilhouetteActorProperties(sil_act)
            sil_act.SetVisibility(actor.GetVisibility())
        for actor in self._sideset_actors.values():
            self._setSideSetActorProperties(actor)

    def onPerspectiveToggled(self, checked):
        if checked:
            camera = self._vtk_renderer.GetActiveCamera()
            camera.ParallelProjectionOff()
        else:
            camera = self._vtk_renderer.GetActiveCamera()
            camera.ParallelProjectionOn()

    def _setSelectedBlockActorProperties(self, block_id, property):
        if self.renderMode() == self.SHADED:
            property.SetColor(common.qcolor2vtk(self.SIDESET_CLR))
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(False)
        elif self.renderMode() == self.SHADED_WITH_EDGES:
            property.SetColor(common.qcolor2vtk(self.SIDESET_CLR))
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(True)
            property.SetEdgeColor(common.qcolor2vtk(self.SIDESET_EDGE_CLR))
            property.SetLineWidth(2)
        elif self.renderMode() == self.HIDDEN_EDGES_REMOVED:
            property.SetColor(common.qcolor2vtk(self.SIDESET_CLR))
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(False)
        elif self.renderMode() == self.TRANSLUENT:
            property.SetColor(common.qcolor2vtk(self.SIDESET_CLR))
            property.SetOpacity(0.33)
            property.SetEdgeVisibility(False)

    def _setDeselectedBlockActorProperties(self, block_id, property):
        if self.renderMode() == self.SHADED:
            property.SetColor(self._block_color[block_id])
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(False)
        elif self.renderMode() == self.SHADED_WITH_EDGES:
            property.SetColor(self._block_color[block_id])
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(True)
            property.SetEdgeColor(common.qcolor2vtk(self.SIDESET_EDGE_CLR))
            property.SetLineWidth(2)
        elif self.renderMode() == self.HIDDEN_EDGES_REMOVED:
            property.SetColor([1, 1, 1])
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(False)
        elif self.renderMode() == self.TRANSLUENT:
            property.SetColor(self._block_color[block_id])
            property.SetOpacity(0.33)
            property.SetEdgeVisibility(False)

    def _setBlockActorProperties(self, block_id, actor, selected=False):
        property = actor.GetProperty()
        property.SetAmbient(0.4)
        property.SetDiffuse(0.6)
        if selected:
            self._setSelectedBlockActorProperties(block_id, property)
        else:
            self._setDeselectedBlockActorProperties(block_id, property)

    def _setSideSetActorProperties(self, actor):
        property = actor.GetProperty()
        if self.renderMode() == self.SHADED:
            property.SetColor(common.qcolor2vtk(self.SIDESET_CLR))
            property.SetEdgeVisibility(False)
            property.SetEdgeColor(common.qcolor2vtk(self.SIDESET_EDGE_CLR))
            property.SetLineWidth(self.SIDESET_EDGE_WIDTH)
            property.LightingOff()
        elif self.renderMode() == self.SHADED_WITH_EDGES:
            property = actor.GetProperty()
            property.SetColor(common.qcolor2vtk(self.SIDESET_CLR))
            property.SetEdgeVisibility(False)
            property.SetEdgeColor(common.qcolor2vtk(self.SIDESET_EDGE_CLR))
            property.SetLineWidth(self.SIDESET_EDGE_WIDTH)
            property.LightingOff()
        elif self.renderMode() == self.HIDDEN_EDGES_REMOVED:
            property = actor.GetProperty()
            property.SetColor(common.qcolor2vtk(self.SIDESET_CLR))
            property.SetEdgeVisibility(False)
            property.LightingOff()
        elif self.renderMode() == self.TRANSLUENT:
            property = actor.GetProperty()
            property.SetColor(common.qcolor2vtk(self.SIDESET_CLR))
            property.SetEdgeVisibility(False)
            property.LightingOff()

    def _setNodeSetActorProperties(self, actor):
        property = actor.GetProperty()
        property.SetRepresentationToPoints()
        property.SetRenderPointsAsSpheres(True)
        property.SetVertexVisibility(True)
        property.SetEdgeVisibility(False)
        property.SetPointSize(10)
        property.SetColor(common.qcolor2vtk(self.NODESET_CLR))
        property.SetOpacity(1)
        property.SetAmbient(1)
        property.SetDiffuse(0)

    def _setSilhouetteActorProperties(self, actor):
        property = actor.GetProperty()
        property.SetColor([0, 0, 0])
        property.SetLineWidth(3)

    def _setSelectionActorProperties(self, actor):
        property = actor.GetProperty()
        if self._select_mode == self.MODE_SELECT_CELLS:
            property.SetRepresentationToSurface()
            property.SetRenderPointsAsSpheres(False)
            property.SetVertexVisibility(False)
            property.SetPointSize(0)
            property.EdgeVisibilityOn()
            property.SetColor(common.qcolor2vtk(self.SELECTION_CLR))
            property.SetLineWidth(7)
            property.SetEdgeColor(common.qcolor2vtk(self.SELECTION_EDGE_CLR))
            property.SetOpacity(0.5)
            property.SetAmbient(1)
            property.SetDiffuse(0)
        elif self._select_mode == self.MODE_SELECT_POINTS:
            property.SetRepresentationToPoints()
            property.SetRenderPointsAsSpheres(True)
            property.SetVertexVisibility(True)
            property.SetEdgeVisibility(False)
            property.SetPointSize(15)
            property.SetColor(common.qcolor2vtk(self.SELECTION_CLR))
            property.SetOpacity(1)
            property.SetAmbient(1)
            property.SetDiffuse(0)

    def onUpdateWindow(self):
        self._vtk_render_window.Render()

    def event(self, e):
        if e.type() == LoadFileEvent.TYPE:
            self.loadFile(e.fileName())
            return True
        else:
            return super().event(e)

    def closeEvent(self, event):
        self.plugin.settings.setValue("tools/select_mode", self._select_mode)
        super().closeEvent(event)

    def onFileChanged(self, path):
        if path not in self._file_watcher.files():
            self._file_watcher.addPath(path)
        self.showFileChangedNotification()

    def showFileChangedNotification(self):
        self._file_changed_notification.adjustSize()
        width = self.getRenderWindowWidth()
        left = (width - self._file_changed_notification.width()) / 2
        top = 10
        self._file_changed_notification.setGeometry(
            left, top,
            self._file_changed_notification.width(),
            self._file_changed_notification.height())
        self._file_changed_notification.show()

    def onReloadFile(self):
        self.loadFile(self._file_name)

    def _showSelectedMeshEntity(self):
        self._selected_mesh_ent_info.adjustSize()

        wnd_geom = self.geometry()
        widget_geom = self._selected_mesh_ent_info.geometry()

        self._selected_mesh_ent_info.move(
            wnd_geom.width() - widget_geom.width() - 10,
            wnd_geom.height() - widget_geom.height() - 5)
        self._selected_mesh_ent_info.show()

    def onBlockSelectionChanged(self, block_id):
        self._deselectBlocks()
        if block_id in self._block_info:
            nfo = self._block_info[block_id]
            self._selected_mesh_ent_info.setBlockInfo(block_id, nfo)
            self._showSelectedMeshEntity()

            self._selected_block = block_id
            actor = self._block_actors[block_id]
            self._setBlockActorProperties(block_id, actor, selected=True)
        else:
            self._selected_mesh_ent_info.hide()

    def _deselectBlocks(self):
        blk_id = self._selected_block
        if blk_id is not None:
            actor = self._block_actors[blk_id]
            self._setBlockActorProperties(blk_id, actor, selected=False)
            self._selected_block = None

    def onSidesetSelectionChanged(self, sideset_id):
        if sideset_id in self._sideset_info:
            nfo = self._sideset_info[sideset_id]
            self._selected_mesh_ent_info.setSidesetInfo(sideset_id, nfo)
            self._showSelectedMeshEntity()
        else:
            self._selected_mesh_ent_info.hide()

    def onNodesetSelectionChanged(self, nodeset_id):
        if nodeset_id in self._nodeset_info:
            nfo = self._nodeset_info[nodeset_id]
            self._selected_mesh_ent_info.setNodesetInfo(nodeset_id, nfo)
            self._showSelectedMeshEntity()
        else:
            self._selected_mesh_ent_info.hide()

    def _blockActorToId(self, actor):
        # TODO: when we start to have 1000s of actors, this should be an
        # inverse dictionary from 'actor' to 'block_id'
        for blk_id, blk_actor in self._block_actors.items():
            if blk_actor == actor:
                return blk_id
        return None

    def _selectBlock(self, pt):
        picker = vtk.vtkPropPicker()
        if picker.PickProp(pt.x(), pt.y(), self._vtk_renderer):
            actor = picker.GetViewProp()
            blk_id = self._blockActorToId(actor)
            self.onBlockSelectionChanged(blk_id)

    def _selectCell(self, pt):
        picker = vtk.vtkCellPicker()
        if picker.Pick(pt.x(), pt.y(), 0, self._vtk_renderer):
            self._selection.selectCell(picker.GetCellId())
            self._setSelectionActorProperties(self._selection.getActor())

    def _selectPoint(self, pt):
        picker = vtk.vtkPointPicker()
        if picker.Pick(pt.x(), pt.y(), 0, self._vtk_renderer):
            self._selection.selectPoint(picker.GetPointId())
            self._setSelectionActorProperties(self._selection.getActor())

    def onClicked(self, pt):
        self.onDeselect()
        if self._select_mode == self.MODE_SELECT_BLOCKS:
            self._selectBlock(pt)
        elif self._select_mode == self.MODE_SELECT_CELLS:
            self._selectCell(pt)
        elif self._select_mode == self.MODE_SELECT_POINTS:
            self._selectPoint(pt)

    def onViewInfoWindow(self):
        if self._info_window.isVisible():
            self._info_window.hide()
        else:
            self._info_window.show()
        self.updateMenuBar()

    def onSelectModeTriggered(self, action):
        action.setChecked(True)
        self._select_mode = action.data()

    def onDeselect(self):
        self.onBlockSelectionChanged(None)
        self._selection.clear()
