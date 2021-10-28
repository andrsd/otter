import os
import collections
import vtk
from PyQt5 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from otter.plugins.PluginWindowBase import PluginWindowBase
import otter.plugins.common as common
from otter.assets import Assets


BlockInformation = collections.namedtuple(
    'BlockInformation', [
        'name', 'object_type', 'object_index', 'number', 'multiblock_index'
    ])


class LoadThread(QtCore.QThread):
    """ Worker thread for loading ExodusII files """

    def __init__(self, file_name):
        super().__init__()
        self._file_name = file_name
        self._reader = None
        # BlockInformation objects
        self._block_info = dict()

    def run(self):
        self._reader = vtk.vtkExodusIIReader()

        with common.lock_file(self._file_name):
            self._reader.SetFileName(self._file_name)
            self._reader.UpdateInformation()
            self._reader.Update()

            self._readBlockInfo()
            for obj_type, data in self._block_info.items():
                for info in data.values():
                    self._reader.SetObjectStatus(
                        info.object_type, info.object_index, 1)

    def _readBlockInfo(self):
        object_types = [
            vtk.vtkExodusIIReader.ELEM_BLOCK,
            vtk.vtkExodusIIReader.FACE_BLOCK,
            vtk.vtkExodusIIReader.EDGE_BLOCK,
            vtk.vtkExodusIIReader.ELEM_SET,
            vtk.vtkExodusIIReader.SIDE_SET,
            vtk.vtkExodusIIReader.FACE_SET,
            vtk.vtkExodusIIReader.EDGE_SET,
            vtk.vtkExodusIIReader.NODE_SET
        ]

        # Index to be used with the vtkExtractBlock::AddIndex method
        index = 0
        # Loop over all blocks of the vtk.MultiBlockDataSet
        for obj_type in object_types:
            index += 1
            self._block_info[obj_type] = dict()
            for j in range(self._reader.GetNumberOfObjects(obj_type)):
                index += 1
                name = self._reader.GetObjectName(obj_type, j)
                vtkid = self._reader.GetObjectId(obj_type, j)
                if name.startswith('Unnamed'):
                    name = str(vtkid)

                binfo = BlockInformation(object_type=obj_type,
                                         name=name,
                                         number=vtkid,
                                         object_index=j,
                                         multiblock_index=index)
                self._block_info[obj_type][vtkid] = binfo

    def getReader(self):
        return self._reader

    def getBlockInfo(self):
        return self._block_info

    def getFileName(self):
        return self._file_name


class MeshWindow(PluginWindowBase):
    """
    Window for displaying the mesh
    """

    fileLoaded = QtCore.pyqtSignal(object)
    boundsChanged = QtCore.pyqtSignal(list)

    SIDESET_CLR = [247/255, 135/255, 3/255]
    SIDESET_EDGE_CLR = [0.1, 0.1, 0.4]
    SIDESET_EDGE_WIDTH = 5
    NODESET_CLR = [0.1, 0.1, 0.1]

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

        self.setAcceptDrops(True)

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

    def setupWidgets(self):
        frame = QtWidgets.QFrame(self)
        self._vtk_widget = QVTKRenderWindowInteractor(frame)

        self._vtk_renderer = vtk.vtkRenderer()
        self._vtk_widget.GetRenderWindow().AddRenderer(self._vtk_renderer)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._vtk_widget)

        frame.setLayout(self._layout)

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
        self._view_mode.setGeometry(10, 10, 80, 25)
        self._view_mode.show()

        self.setCentralWidget(frame)

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
        len = 80
        self._view_mode.setGeometry(self.width() - 5 - len, 10, len, 25)

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
        block_info = self._load_thread.getBlockInfo()

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
            'block_info': block_info,
            'total_elems': reader.GetTotalNumberOfElements(),
            'total_nodes': reader.GetTotalNumberOfNodes()
        }
        self.fileLoaded.emit(params)
        self.boundsChanged.emit(bnds)

        self._file_name = self._load_thread.getFileName()
        self.updateWindowTitle()

        self._progress.hide()
        self._progress = None

    def _addBlockActors(self):
        camera = self._vtk_renderer.GetActiveCamera()
        reader = self._load_thread.getReader()
        block_info = self._load_thread.getBlockInfo()

        blocks = block_info[vtk.vtkExodusIIReader.ELEM_BLOCK].values()
        for index, binfo in enumerate(blocks):
            eb = vtk.vtkExtractBlock()
            eb.SetInputConnection(reader.GetOutputPort(0))
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
        block_info = self._load_thread.getBlockInfo()

        faces = block_info[vtk.vtkExodusIIReader.SIDE_SET].values()
        for index, finfo in enumerate(faces):
            eb = vtk.vtkExtractBlock()
            eb.SetInputConnection(reader.GetOutputPort())
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
        block_info = self._load_thread.getBlockInfo()

        nodes = block_info[vtk.vtkExodusIIReader.NODE_SET].values()
        for index, ninfo in enumerate(nodes):
            eb = vtk.vtkExtractBlock()
            eb.SetInputConnection(reader.GetOutputPort())
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
        self._vtk_renderer.AddViewProp(self._cube_axes_actor)

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
        if self.renderMode() == self.SHADED:
            property.SetColor(self._block_color[block_id])
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(False)
        elif self.renderMode() == self.SHADED_WITH_EDGES:
            property.SetColor(self._block_color[block_id])
            property.SetOpacity(1.0)
            property.SetEdgeVisibility(True)
            property.SetEdgeColor(self.SIDESET_EDGE_CLR)
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
        property.SetPointSize(10)
        property.SetColor(self.NODESET_CLR)

    def _setSilhouetteActorProperties(self, actor):
        property = actor.GetProperty()
        property.SetColor([0, 0, 0])
        property.SetLineWidth(3)

    def onUpdateWindow(self):
        self._vtk_render_window.Render()
