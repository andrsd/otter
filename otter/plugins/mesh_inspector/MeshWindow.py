import collections
import contextlib
import fcntl
import vtk
from PyQt5 import QtCore, QtWidgets, QtGui
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


BlockInformation = collections.namedtuple(
    'BlockInformation', [
        'name', 'object_type', 'object_index', 'number', 'multiblock_index'
    ])


def point_min(pt1, pt2):
    x = min(pt1.x(), pt2.x())
    y = min(pt1.y(), pt2.y())
    z = min(pt1.z(), pt2.z())
    return QtGui.QVector3D(x, y, z)


def point_max(pt1, pt2):
    x = max(pt1.x(), pt2.x())
    y = max(pt1.y(), pt2.y())
    z = max(pt1.z(), pt2.z())
    return QtGui.QVector3D(x, y, z)


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

        with lock_file(self._file_name):
            self._reader.SetFileName(self._file_name)
            self._reader.UpdateInformation()
            self._reader.Update()

            self._readBlockInfo()

    def _readBlockInfo(self):
        object_types = [
            vtk.vtkExodusIIReader.ELEM_BLOCK,
            vtk.vtkExodusIIReader.SIDE_SET,
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


class MeshWindow(QtWidgets.QMainWindow):
    """
    Window for displaying the mesh
    """

    fileLoaded = QtCore.pyqtSignal(object)

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self._load_thread = None
        self._block_actors = {}
        self._block_bounds = {}

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

            property = actor.GetProperty()
            property.SetRepresentationToSurface()
            property.SetColor([0.8, 0.8, 0.8])
            property.SetEdgeVisibility(True)
            # FIXME: set color from preferences/templates
            property.SetEdgeColor([0.1, 0.1, 0.4])

            self._block_actors[binfo.number] = actor

        self._vtk_renderer.ResetCamera()
        self._vtk_renderer.GetActiveCamera().Zoom(1.5)

        self.fileLoaded.emit(block_info)

        self._vtk_render_window.Render()

    def _getBlockActor(self, block_id):
        return self._block_actors[block_id]

    def onBlockVisibilityChanged(self, block_id, visible):
        actor = self._getBlockActor(block_id)
        if visible:
            self._vtk_renderer.AddViewProp(actor)
        else:
            self._vtk_renderer.RemoveViewProp(actor)
        self._vtk_render_window.Render()

    def onBlockColorChanged(self, block_id, qcolor):
        actor = self._getBlockActor(block_id)
        property = actor.GetProperty()
        clr = [qcolor.redF(), qcolor.greenF(), qcolor.blueF()]
        property.SetColor(clr)

    def _getBlocksBounds(self, extract_block):
        glob_min = QtGui.QVector3D(float('inf'), float('inf'), float('inf'))
        glob_max = QtGui.QVector3D(float('-inf'), float('-inf'), float('-inf'))
        for i in range(extract_block.GetOutput().GetNumberOfBlocks()):
            current = extract_block.GetOutput().GetBlock(i)
            if isinstance(current, vtk.vtkUnstructuredGrid):
                bnd = current.GetBounds()
                bnd_min = QtGui.QVector3D(bnd[0], bnd[2], bnd[4])
                bnd_max = QtGui.QVector3D(bnd[1], bnd[3], bnd[5])
                glob_min = point_min(bnd_min, glob_min)
                glob_max = point_max(bnd_max, glob_max)

            elif isinstance(current, vtk.vtkMultiBlockDataSet):
                for j in range(current.GetNumberOfBlocks()):
                    bnd = current.GetBlock(j).GetBounds()
                    bnd_min = QtGui.QVector3D(bnd[0], bnd[2], bnd[4])
                    bnd_max = QtGui.QVector3D(bnd[1], bnd[3], bnd[5])
                    glob_min = point_min(bnd_min, glob_min)
                    glob_max = point_max(bnd_max, glob_max)

        return (glob_min, glob_max)
