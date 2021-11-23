from PyQt5 import QtWidgets, QtCore, QtGui
from otter.OTreeView import OTreeView
from otter.plugins.viz.RootProps import RootProps


class ParamsWindow(QtWidgets.QWidget):
    """
    Window for entering parameters
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._main_wnd = parent
        self._vtk_renderer = parent._vtk_renderer

        # TOOD: move to RenderWindow
        self._root_props = RootProps(self._vtk_renderer, parent)

        self.setAcceptDrops(True)

        self.setupWidgets()
        self.setMinimumWidth(220)

        self.show()

    def mainWnd(self):
        return self._main_wnd

    def setupWidgets(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self._splitter.setHandleWidth(4)

        self._pipeline_model = QtGui.QStandardItemModel()
        self._pipeline = QtWidgets.QTreeView()
        self._pipeline.setRootIsDecorated(False)
        self._pipeline.setHeaderHidden(True)
        self._pipeline.setModel(self._pipeline_model)
        # self._pipeline.setItemsExpandable(False)
        self._pipeline.setRootIsDecorated(True)
        self._pipeline.setExpandsOnDoubleClick(False)
        self._pipeline.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        self._pipeline.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self._pipeline.doubleClicked.connect(self.onPipelineDoubleClicked)
        self._splitter.addWidget(self._pipeline)

        self._blocks = OTreeView()
        self._splitter.addWidget(self._blocks)

        self._root = QtGui.QStandardItem()
        self._root.setText("Pipeline")
        self._root.setData(self._root_props)
        self._pipeline_model.setItem(0, 0, self._root)

        layout.addWidget(self._splitter)

        self.setLayout(layout)

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

    def onPipelineDoubleClicked(self, index):
        item = self._pipeline_model.itemFromIndex(index)
        props = item.data()
        props.show()

    def addPipelineItem(self, props):
        name = props.windowTitle()
        rows = self._root.rowCount()
        si = QtGui.QStandardItem()
        si.setText(name)
        si.setData(props)
        self._root.insertRow(rows, si)

        index = self._pipeline_model.indexFromItem(si)
        sel_model = self._pipeline.selectionModel()
        sel_model.clearSelection()
        sel_model.setCurrentIndex(index, QtCore.QItemSelectionModel.Select)

    def clear(self):
        self._root.removeRows(0, self._root.rowCount())
