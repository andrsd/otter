import os
import vtk
from PyQt5 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from otter.plugins.PluginWindowBase import PluginWindowBase
from otter.plugins.common.OtterInteractorStyle3D import OtterInteractorStyle3D
from otter.plugins.common.OtterInteractorStyle2D import OtterInteractorStyle2D
from otter.plugins.common.ExodusIIReader import ExodusIIReader
from otter.plugins.common.VTKReader import VTKReader
from otter.plugins.common.PetscHDF5Reader import PetscHDF5Reader
from otter.plugins.common.LoadFileEvent import LoadFileEvent
from otter.plugins.common.NotificationWidget import NotificationWidget
from otter.plugins.common.FileChangedNotificationWidget import \
    FileChangedNotificationWidget
from otter.plugins.common.BlockObject import BlockObject
from otter.plugins.common.SideSetObject import SideSetObject
from otter.plugins.common.NodeSetObject import NodeSetObject
import otter.plugins.common as common
from otter.assets import Assets
from otter.plugins.mesh_inspector.InfoWindow import InfoWindow
from otter.plugins.mesh_inspector.SelectedMeshEntityInfoWidget import \
    SelectedMeshEntityInfoWidget
from otter.plugins.mesh_inspector.ExplodeWidget import ExplodeWidget
from otter.plugins.mesh_inspector.Selection import Selection
from otter.plugins.mesh_inspector.color_profiles import default
from otter.plugins.mesh_inspector.color_profiles import light
from otter.plugins.mesh_inspector.color_profiles import dark


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

    COLOR_PROFILE_DEFAULT = 0
    COLOR_PROFILE_LIGHT = 1
    COLOR_PROFILE_DARK = 2

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
        self.loadColorProfiles()

        self.setAcceptDrops(True)

        self.connectSignals()
        self.setupVtk()
        self.setColorProfile()

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
        self.setupNotificationWidget()
        self._selected_mesh_ent_info = SelectedMeshEntityInfoWidget(self)
        self._selected_mesh_ent_info.setVisible(False)

        self.deselect_sc = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_Space), self)
        self.deselect_sc.activated.connect(self.onDeselect)

        self.setupExplodeWidgets()

    def setupViewModeWidget(self, frame):
        self._view_menu = QtWidgets.QMenu()
        self._shaded_action = self._view_menu.addAction("Shaded")
        self._shaded_action.setCheckable(True)
        self._shaded_action.setShortcut("Ctrl+1")
        self._shaded_w_edges_action = self._view_menu.addAction(
            "Shaded with edges")
        self._shaded_w_edges_action.setCheckable(True)
        self._shaded_w_edges_action.setShortcut("Ctrl+2")
        self._hidden_edges_removed_action = self._view_menu.addAction(
            "Hidden edges removed")
        self._hidden_edges_removed_action.setCheckable(True)
        self._hidden_edges_removed_action.setShortcut("Ctrl+3")
        self._transluent_action = self._view_menu.addAction(
            "Transluent")
        self._transluent_action.setCheckable(True)
        self._transluent_action.setShortcut("Ctrl+4")
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

    def setupNotificationWidget(self):
        self._notification = NotificationWidget(self)
        self._notification.setVisible(False)

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
        export_menu = file_menu.addMenu("Export as...")
        self.setupExportMenu(export_menu)
        file_menu.addSeparator()
        self._close_action = file_menu.addAction(
            "Close", self.onClose, "Ctrl+W")

        view_menu = self._menubar.addMenu("View")
        view_menu.addAction(self._shaded_action)
        view_menu.addAction(self._shaded_w_edges_action)
        view_menu.addAction(self._hidden_edges_removed_action)
        view_menu.addAction(self._transluent_action)
        view_menu.addSeparator()
        self._view_info_wnd_action = view_menu.addAction(
            "Info window", self.onViewInfoWindow)
        self._view_info_wnd_action.setCheckable(True)
        color_profile_menu = view_menu.addMenu("Color profile")
        self.setupColorProfileMenu(color_profile_menu)

        tools_menu = self._menubar.addMenu("Tools")
        self.setupSelectModeMenu(tools_menu)
        self._tools_explode_action = tools_menu.addAction(
            "Explode", self.onToolsExplode)

    def setupExportMenu(self, menu):
        menu.addAction("PNG...", self.onExportAsPng)
        menu.addAction("JPG...", self.onExportAsJpg)

    def setupColorProfileMenu(self, menu):
        self._color_profile_action_group = QtWidgets.QActionGroup(self)
        self._color_profile_id = self.plugin.settings.value(
            "color_profile", self.COLOR_PROFILE_DEFAULT)
        color_profiles = [
            {
                'name': 'Default',
                'id': self.COLOR_PROFILE_DEFAULT
            },
            {
                'name': 'Light',
                'id': self.COLOR_PROFILE_LIGHT
            },
            {
                'name': 'Dark',
                'id': self.COLOR_PROFILE_DARK
            }
        ]
        for cp in color_profiles:
            name = cp['name']
            id = cp['id']
            action = menu.addAction(name)
            action.setCheckable(True)
            action.setData(id)
            self._color_profile_action_group.addAction(action)
            if id == self._color_profile_id:
                action.setChecked(True)

        self._color_profile_action_group.triggered.connect(
            self.onColorProfileTriggered)

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

    def setupExplodeWidgets(self):
        self._explode = ExplodeWidget(self)
        self._explode.valueChanged.connect(self.onExplodeValueChanged)
        self._explode.setVisible(False)

    def updateMenuBar(self):
        self._view_info_wnd_action.setChecked(self._info_window.isVisible())
        self._tools_explode_action.setEnabled(self._file_name is not None)

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

        self._vtk_interactor.SetInteractorStyle(OtterInteractorStyle3D(self))

        # TODO: set background from preferences/templates
        self._vtk_renderer.SetGradientBackground(True)
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
        self._blocks = {}
        self._side_sets = {}
        self._node_sets = {}
        self._vtk_renderer.RemoveAllViewProps()

        watched_files = self._file_watcher.files()
        for file in watched_files:
            self._file_watcher.removePath(file)

        self._selection = None

    def checkFileExists(self, file_name):
        if os.path.exists(file_name):
            return True
        else:
            base_file = os.path.basename(file_name)
            self.showNotification(
                "Unable to open '{}': File does not exist.".format(base_file))
            return False

    def loadFile(self, file_name):
        self.clear()
        if not self.checkFileExists(file_name):
            return

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

        self._addBlocks()
        self._addSidesets()
        self._addNodeSets()

        gmin = QtGui.QVector3D(float('inf'), float('inf'), float('inf'))
        gmax = QtGui.QVector3D(float('-inf'), float('-inf'), float('-inf'))
        for block in self._blocks.values():
            bmin, bmax = block.bounds
            gmin = common.point_min(bmin, gmin)
            gmax = common.point_max(bmax, gmax)
        bnds = [gmin.x(), gmax.x(), gmin.y(), gmax.y(), gmin.z(), gmax.z()]

        self._com = common.centerOfBounds(bnds)
        self._cube_axes_actor.SetBounds(*bnds)
        self._vtk_renderer.AddViewProp(self._cube_axes_actor)

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
        self._setSelectionProperties(self._selection)
        self._vtk_renderer.AddActor(self._selection.getActor())

        self._progress.hide()
        self._progress = None

        self.updateMenuBar()

        if reader.getDimensionality() == 3:
            style = OtterInteractorStyle3D(self)
        else:
            style = OtterInteractorStyle2D(self)
        self._vtk_interactor.SetInteractorStyle(style)

        camera = self._vtk_renderer.GetActiveCamera()
        focal_point = camera.GetFocalPoint()
        camera.SetPosition(focal_point[0], focal_point[1], 1)
        camera.SetRoll(0)
        self._vtk_renderer.ResetCamera()

    def _addBlocks(self):
        camera = self._vtk_renderer.GetActiveCamera()
        reader = self._load_thread.getReader()

        for index, binfo in enumerate(reader.getBlocks()):
            eb = vtk.vtkExtractBlock()
            eb.SetInputConnection(reader.getVtkOutputPort())
            eb.AddIndex(binfo.multiblock_index)
            eb.Update()

            block = BlockObject(eb, camera)
            self._setBlockProperties(block)
            self._blocks[binfo.number] = block

            self._vtk_renderer.AddViewProp(block.actor)
            self._vtk_renderer.AddViewProp(block.silhouette_actor)
            # FIXME: make this work with multiple blocks
            self._geometry = block.geometry

    def _addSidesets(self):
        reader = self._load_thread.getReader()

        for index, finfo in enumerate(reader.getSideSets()):
            eb = vtk.vtkExtractBlock()
            eb.SetInputConnection(reader.getVtkOutputPort())
            eb.AddIndex(finfo.multiblock_index)
            eb.Update()

            sideset = SideSetObject(eb)
            self._side_sets[finfo.number] = sideset
            self._vtk_renderer.AddViewProp(sideset.actor)
            self._setSideSetProperties(sideset)

    def _addNodeSets(self):
        reader = self._load_thread.getReader()

        for index, ninfo in enumerate(reader.getNodeSets()):
            eb = vtk.vtkExtractBlock()
            eb.SetInputConnection(reader.getVtkOutputPort())
            eb.AddIndex(ninfo.multiblock_index)
            eb.Update()

            nodeset = NodeSetObject(eb)
            self._node_sets[ninfo.number] = nodeset
            self._vtk_renderer.AddViewProp(nodeset.actor)
            self._setNodeSetProperties(nodeset)

    def _setupCubeAxesActor(self):
        self._cube_axes_actor = vtk.vtkCubeAxesActor()
        self._cube_axes_actor.VisibilityOff()
        self._cube_axes_actor.SetCamera(self._vtk_renderer.GetActiveCamera())
        self._cube_axes_actor.SetGridLineLocation(
            vtk.vtkCubeAxesActor.VTK_GRID_LINES_ALL)
        self._cube_axes_actor.SetFlyMode(
            vtk.vtkCubeAxesActor.VTK_FLY_OUTER_EDGES)

    def _getBlock(self, block_id):
        return self._blocks[block_id]

    def _getSideSet(self, sideset_id):
        return self._side_sets[sideset_id]

    def _getNodeSet(self, nodeset_id):
        return self._node_sets[nodeset_id]

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
        block = self._getBlock(block_id)
        block.setVisible(visible)
        if (self.renderMode() == self.HIDDEN_EDGES_REMOVED or
                self.renderMode() == self.TRANSLUENT):
            block.setSilhouetteVisible(block.visible)
        else:
            block.setSilhouetteVisible(False)

    def onBlockColorChanged(self, block_id, qcolor):
        clr = [qcolor.redF(), qcolor.greenF(), qcolor.blueF()]
        block = self._getBlock(block_id)
        block.setColor(clr)

        property = block.property
        if self.renderMode() == self.HIDDEN_EDGES_REMOVED:
            property.SetColor([1, 1, 1])
        else:
            property.SetColor(clr)

    def onSidesetVisibilityChanged(self, sideset_id, visible):
        sideset = self._getSideSet(sideset_id)
        sideset.setVisible(visible)

    def onNodesetVisibilityChanged(self, nodeset_id, visible):
        nodeset = self._getNodeSet(nodeset_id)
        nodeset.setVisible(visible)

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
        for block_id, block in self._blocks.items():
            selected = self._selected_block == block_id
            self._setBlockProperties(block, selected)
            block.setSilhouetteVisible(False)
        for sideset in self._side_sets.values():
            self._setSideSetProperties(sideset)

    def onShadedWithEdgesTriggered(self, checked):
        self._render_mode = self.SHADED_WITH_EDGES
        for block_id, block in self._blocks.items():
            selected = self._selected_block == block_id
            self._setBlockProperties(block, selected)
            block.setSilhouetteVisible(False)
        for sideset in self._side_sets.values():
            self._setSideSetProperties(sideset)

    def onHiddenEdgesRemovedTriggered(self, checked):
        self._render_mode = self.HIDDEN_EDGES_REMOVED
        for block_id, block in self._blocks.items():
            selected = self._selected_block == block_id
            self._setBlockProperties(block, selected)
            block.setSilhouetteVisible(block.visible)
        for sideset in self._side_sets.values():
            self._setSideSetProperties(sideset)

    def onTransluentTriggered(self, checked):
        self._render_mode = self.TRANSLUENT
        for block_id, block in self._blocks.items():
            selected = self._selected_block == block_id
            self._setBlockProperties(block, selected)
            block.setSilhouetteVisible(block.visible)
        for sideset in self._side_sets.values():
            self._setSideSetProperties(sideset)

    def onPerspectiveToggled(self, checked):
        if checked:
            camera = self._vtk_renderer.GetActiveCamera()
            camera.ParallelProjectionOff()
        else:
            camera = self._vtk_renderer.GetActiveCamera()
            camera.ParallelProjectionOn()

    def _setSelectedBlockProperties(self, block):
        property = block.property
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

    def _setDeselectedBlockProperties(self, block):
        property = block.property
        if self.renderMode() == self.SHADED:
            property.SetColor(block.color)
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(False)
        elif self.renderMode() == self.SHADED_WITH_EDGES:
            property.SetColor(block.color)
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(True)
            property.SetEdgeColor(common.qcolor2vtk(self.SIDESET_EDGE_CLR))
            property.SetLineWidth(2)
        elif self.renderMode() == self.HIDDEN_EDGES_REMOVED:
            property.SetColor([1, 1, 1])
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(False)
        elif self.renderMode() == self.TRANSLUENT:
            property.SetColor(block.color)
            property.SetOpacity(0.33)
            property.SetEdgeVisibility(False)

    def _setBlockProperties(self, block, selected=False):
        property = block.property
        property.SetAmbient(0.4)
        property.SetDiffuse(0.6)
        if selected:
            self._setSelectedBlockProperties(block)
        else:
            self._setDeselectedBlockProperties(block)

    def _setSideSetProperties(self, sideset):
        property = sideset.property
        if self.renderMode() == self.SHADED:
            property.SetColor(common.qcolor2vtk(self.SIDESET_CLR))
            property.SetEdgeVisibility(False)
            property.SetEdgeColor(common.qcolor2vtk(self.SIDESET_EDGE_CLR))
            property.SetLineWidth(self.SIDESET_EDGE_WIDTH)
            property.LightingOff()
        elif self.renderMode() == self.SHADED_WITH_EDGES:
            property.SetColor(common.qcolor2vtk(self.SIDESET_CLR))
            property.SetEdgeVisibility(False)
            property.SetEdgeColor(common.qcolor2vtk(self.SIDESET_EDGE_CLR))
            property.SetLineWidth(self.SIDESET_EDGE_WIDTH)
            property.LightingOff()
        elif self.renderMode() == self.HIDDEN_EDGES_REMOVED:
            property.SetColor(common.qcolor2vtk(self.SIDESET_CLR))
            property.SetEdgeVisibility(False)
            property.LightingOff()
        elif self.renderMode() == self.TRANSLUENT:
            property.SetColor(common.qcolor2vtk(self.SIDESET_CLR))
            property.SetEdgeVisibility(False)
            property.LightingOff()

    def _setNodeSetProperties(self, nodeset):
        property = nodeset.property
        property.SetRepresentationToPoints()
        property.SetRenderPointsAsSpheres(True)
        property.SetVertexVisibility(True)
        property.SetEdgeVisibility(False)
        property.SetPointSize(10)
        property.SetColor(common.qcolor2vtk(self.NODESET_CLR))
        property.SetOpacity(1)
        property.SetAmbient(1)
        property.SetDiffuse(0)

    def _setSelectionProperties(self, selection):
        actor = selection.getActor()
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
        self.plugin.settings.setValue("color_profile", self._color_profile_id)
        super().closeEvent(event)

    def onFileChanged(self, path):
        if path not in self._file_watcher.files():
            self._file_watcher.addPath(path)
        self.showFileChangedNotification()

    def showNotification(self, text, ms=5000):
        """
        @param text Notification text
        @param ms Timeout for fade out in milliseconds
        """
        self._notification.setText(text)
        self._notification.adjustSize()
        width = self.geometry().width()
        left = (width - self._notification.width()) / 2
        # top = 10
        top = self.height() - self._notification.height() - 10
        self._notification.setGeometry(
            left, top,
            self._notification.width(),
            self._notification.height())
        self._notification.setGraphicsEffect(None)
        self._notification.show(ms)

    def showFileChangedNotification(self):
        self._file_changed_notification.adjustSize()
        width = self.getRenderWindowWidth()
        left = int((width - self._file_changed_notification.width()) / 2)
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
        if block_id in self._blocks:
            block = self._getBlock(block_id)
            self._selected_mesh_ent_info.setBlockInfo(block_id, block.info)
            self._showSelectedMeshEntity()
            self._selected_block = block_id
            self._setBlockProperties(block, selected=True)
        else:
            self._selected_mesh_ent_info.hide()

    def _deselectBlocks(self):
        blk_id = self._selected_block
        if blk_id is not None:
            block = self._getBlock(blk_id)
            self._setBlockProperties(block, selected=False)
            self._selected_block = None

    def onSidesetSelectionChanged(self, sideset_id):
        if sideset_id in self._side_sets:
            ss = self._side_sets[sideset_id]
            self._selected_mesh_ent_info.setSidesetInfo(sideset_id, ss.info)
            self._showSelectedMeshEntity()
        else:
            self._selected_mesh_ent_info.hide()

    def onNodesetSelectionChanged(self, nodeset_id):
        if nodeset_id in self._node_sets:
            ns = self._node_sets[nodeset_id]
            self._selected_mesh_ent_info.setNodesetInfo(nodeset_id, ns.info)
            self._showSelectedMeshEntity()
        else:
            self._selected_mesh_ent_info.hide()

    def _blockActorToId(self, actor):
        # TODO: when we start to have 1000s of actors, this should be an
        # inverse dictionary from 'actor' to 'block_id'
        for blk_id, block in self._blocks.items():
            if block.actor == actor:
                return blk_id
        return None

    def _selectBlock(self, pt):
        picker = vtk.vtkPropPicker()
        if picker.PickProp(pt.x(), pt.y(), self._vtk_renderer):
            actor = picker.GetViewProp()
            blk_id = self._blockActorToId(actor)
            self.onBlockSelectionChanged(blk_id)

    def _buildCellInfo(self, cell):
        nfo = {
            'type': cell.GetCellType()
        }
        return nfo

    def _selectCell(self, pt):
        picker = vtk.vtkCellPicker()
        if picker.Pick(pt.x(), pt.y(), 0, self._vtk_renderer):
            cell_id = picker.GetCellId()
            self._selection.selectCell(cell_id)
            self._setSelectionProperties(self._selection)

            unstr_grid = self._selection.get()
            cell = unstr_grid.GetCell(0)
            nfo = self._buildCellInfo(cell)
            self._selected_mesh_ent_info.setCellInfo(cell_id, nfo)
            self._showSelectedMeshEntity()

    def _buildPointInfo(self, points):
        coords = points.GetPoint(0)
        nfo = {
            'coords': coords
        }
        return nfo

    def _selectPoint(self, pt):
        picker = vtk.vtkPointPicker()
        if picker.Pick(pt.x(), pt.y(), 0, self._vtk_renderer):
            point_id = picker.GetPointId()
            self._selection.selectPoint(point_id)
            self._setSelectionProperties(self._selection)

            unstr_grid = self._selection.get()
            points = unstr_grid.GetPoints()
            nfo = self._buildPointInfo(points)
            self._selected_mesh_ent_info.setPointInfo(point_id, nfo)
            self._showSelectedMeshEntity()

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
        if self._selection is not None:
            self.onBlockSelectionChanged(None)
            self._selection.clear()

    def onColorProfileTriggered(self, action):
        action.setChecked(True)
        self._color_profile_id = action.data()
        self.setColorProfile()

    def setColorProfile(self):
        if self._color_profile_id in self._color_profiles:
            profile = self._color_profiles[self._color_profile_id]
        else:
            profile = self._color_profiles[self.COLOR_PROFILE_DEFAULT]

        bkgnd = common.rgb2vtk(profile['bkgnd'])
        self._vtk_renderer.SetBackground(bkgnd)
        self._vtk_renderer.SetBackground2(bkgnd)

    def loadColorProfiles(self):
        # TODO: load the profiles via import and iterating over files in
        # 'color_profile' folder

        self._color_profiles = {}
        self._color_profiles[self.COLOR_PROFILE_DEFAULT] = default.profile
        self._color_profiles[self.COLOR_PROFILE_LIGHT] = light.profile
        self._color_profiles[self.COLOR_PROFILE_DARK] = dark.profile

    def getFileName(self, window_title, name_filter, default_suffix):
        dialog = QtWidgets.QFileDialog()
        dialog.setWindowTitle(window_title)
        dialog.setNameFilter(name_filter)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setDefaultSuffix(default_suffix)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            return str(dialog.selectedFiles()[0])
        return None

    def onExportAsPng(self):
        file_name = self.getFileName('Export to PNG',
                                     'PNG files (*.png)',
                                     'png')
        if file_name:
            windowToImageFilter = vtk.vtkWindowToImageFilter()
            windowToImageFilter.SetInput(self._vtk_render_window)
            windowToImageFilter.SetInputBufferTypeToRGBA()
            windowToImageFilter.ReadFrontBufferOff()
            windowToImageFilter.Update()

            writer = vtk.vtkPNGWriter()
            writer.SetFileName(file_name)
            writer.SetInputConnection(windowToImageFilter.GetOutputPort())
            writer.Write()

    def onExportAsJpg(self):
        file_name = self.getFileName('Export to JPG',
                                     'JPG files (*.jpg)',
                                     'jpg')
        if file_name:
            windowToImageFilter = vtk.vtkWindowToImageFilter()
            windowToImageFilter.SetInput(self._vtk_render_window)
            windowToImageFilter.ReadFrontBufferOff()
            windowToImageFilter.Update()

            writer = vtk.vtkJPEGWriter()
            writer.SetFileName(file_name)
            writer.SetInputConnection(windowToImageFilter.GetOutputPort())
            writer.Write()

    def onToolsExplode(self):
        self._explode.adjustSize()
        render_win_geom = self.geometry()
        left = (render_win_geom.width() - self._explode.width()) / 2
        top = render_win_geom.height() - self._explode.height() - 10
        self._explode.setGeometry(
            left, top,
            self._explode.width(),
            self._explode.height())
        self._explode.show()

    def onExplodeValueChanged(self, value):
        dist = value / self._explode.range()
        for blk_id, block in self._blocks.items():
            blk_com = block.cob
            cntr = QtGui.QVector3D(self._com[0], self._com[1], self._com[2])
            blk_cntr = QtGui.QVector3D(blk_com[0], blk_com[1], blk_com[2])
            dir = blk_cntr - cntr
            dir.normalize()
            dir = -dist * dir
            pos = [dir.x(), dir.y(), dir.z()]
            block.actor.SetPosition(pos)
