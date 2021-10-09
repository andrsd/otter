import vtk
from PyQt5 import QtWidgets, QtCore, QtGui


class InfoWindow(QtWidgets.QScrollArea):
    """
    Window for showing mesh info
    """

    IDX_NAME = 0
    IDX_COLOR = 1
    IDX_ID = 2

    blockVisibilityChanged = QtCore.pyqtSignal(int, object)
    blockColorChanged = QtCore.pyqtSignal(int, object)
    dimensionsStateChanged = QtCore.pyqtSignal(bool)

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

        self._colors = [
            [0, 141, 223],
            [121, 199, 44],
            [255, 146, 0],
            [94, 61, 212],
            [192, 60, 40]
        ]

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(20, 10, 20, 10)

        self._lbl_blocks = QtWidgets.QLabel("Blocks")
        self._layout.addWidget(self._lbl_blocks)
        self._block_model = QtGui.QStandardItemModel()
        self._block_model.setHorizontalHeaderLabels([
            "Name", "", "ID"
        ])
        self._block_model.itemChanged.connect(self.onBlockChanged)
        self._blocks = QtWidgets.QTreeView()
        self._blocks.setFixedHeight(300)
        self._blocks.setRootIsDecorated(False)
        self._blocks.setModel(self._block_model)
        self._blocks.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self._blocks.setColumnWidth(0, 200)
        self._blocks.setColumnWidth(1, 20)
        self._blocks.setColumnWidth(2, 50)
        self._layout.addWidget(self._blocks)

        self._lbl_sidesets = QtWidgets.QLabel("Side sets")
        self._layout.addWidget(self._lbl_sidesets)
        self._sideset_model = QtGui.QStandardItemModel()
        self._sideset_model.setHorizontalHeaderLabels([
            "Name", "", "ID"
        ])
        self._sideset_model.itemChanged.connect(self.onSidesetChanged)
        self._sidesets = QtWidgets.QTreeView()
        self._sidesets.setFixedHeight(200)
        self._sidesets.setRootIsDecorated(False)
        self._sidesets.setModel(self._sideset_model)
        self._sidesets.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self._sidesets.setColumnWidth(0, 220)
        self._sidesets.setColumnWidth(2, 50)
        self._sidesets.hideColumn(self.IDX_COLOR)
        self._layout.addWidget(self._sidesets)

        self._lbl_nodesets = QtWidgets.QLabel("Node sets")
        self._layout.addWidget(self._lbl_nodesets)
        self._nodesets = QtWidgets.QTreeView()
        self._nodeset_model = QtGui.QStandardItemModel()
        self._nodeset_model.setHorizontalHeaderLabels([
            "Name", "", "ID"
        ])
        self._nodeset_model.itemChanged.connect(self.onNodesetChanged)
        self._nodesets.setFixedHeight(200)
        self._nodesets.setRootIsDecorated(False)
        self._nodesets.setModel(self._nodeset_model)
        self._nodesets.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self._nodesets.setColumnWidth(0, 220)
        self._nodesets.setColumnWidth(2, 50)
        self._nodesets.hideColumn(self.IDX_COLOR)
        self._layout.addWidget(self._nodesets)

        self._lbl_dimensions = QtWidgets.QLabel("Dimensions")
        self._layout.addWidget(self._lbl_dimensions)

        self._x_range = QtWidgets.QLabel("x-range:")
        self._layout.addWidget(self._x_range)
        self._y_range = QtWidgets.QLabel("y-range:")
        self._layout.addWidget(self._y_range)
        self._z_range = QtWidgets.QLabel("z-range:")
        self._layout.addWidget(self._z_range)

        self._dimensions = QtWidgets.QCheckBox("Show dimensions")
        self._dimensions.stateChanged.connect(self.onDimensionsStateChanged)
        self._layout.addWidget(self._dimensions)

        self._layout.addStretch()

        w = QtWidgets.QWidget()
        w.setLayout(self._layout)
        self.setWidget(w)
        self.setWindowTitle("Info")
        self.setMinimumWidth(350)
        self.setWidgetResizable(True)
        self.show()

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

    def _loadBlocks(self, blocks):
        self._block_model.removeRows(0, self._block_model.rowCount())
        for index, blk in enumerate(blocks):
            row = self._block_model.rowCount()

            si_name = QtGui.QStandardItem()
            si_name.setText(blk.name)
            si_name.setCheckable(True)
            si_name.setCheckState(QtCore.Qt.Checked)
            si_name.setData(blk)
            self._block_model.setItem(row, self.IDX_NAME, si_name)

            si_clr = QtGui.QStandardItem()
            si_clr.setText('\u25a0')
            clr_idx = index % len(self._colors)
            rgb = self._colors[clr_idx]
            color = QtGui.QColor(rgb[0], rgb[1], rgb[2])
            si_clr.setForeground(QtGui.QBrush(color))
            self._block_model.setItem(row, self.IDX_COLOR, si_clr)

            si_id = QtGui.QStandardItem()
            si_id.setText(str(blk.number))
            self._block_model.setItem(row, self.IDX_ID, si_id)

    def _loadSideSets(self, sidesets):
        self._sideset_model.removeRows(0, self._sideset_model.rowCount())
        for index, ss in enumerate(sidesets):
            row = self._sideset_model.rowCount()

            si_name = QtGui.QStandardItem()
            si_name.setText(ss.name)
            si_name.setCheckable(True)
            si_name.setData(ss)
            self._sideset_model.setItem(row, self.IDX_NAME, si_name)

            si_id = QtGui.QStandardItem()
            si_id.setText(str(ss.number))
            self._sideset_model.setItem(row, self.IDX_ID, si_id)

    def _loadNodeSets(self, nodesets):
        self._nodeset_model.removeRows(0, self._nodeset_model.rowCount())
        for index, ss in enumerate(nodesets):
            row = self._nodeset_model.rowCount()

            si_name = QtGui.QStandardItem()
            si_name.setText(ss.name)
            si_name.setCheckable(True)
            si_name.setData(ss)
            self._nodeset_model.setItem(row, self.IDX_NAME, si_name)

            si_id = QtGui.QStandardItem()
            si_id.setText(str(ss.number))
            self._nodeset_model.setItem(row, self.IDX_ID, si_id)

    def onFileLoaded(self, block_info):
        block_type = vtk.vtkExodusIIReader.ELEM_BLOCK
        self._loadBlocks(block_info[block_type].values())
        block_type = vtk.vtkExodusIIReader.SIDE_SET
        self._loadSideSets(block_info[block_type].values())
        block_type = vtk.vtkExodusIIReader.NODE_SET
        self._loadNodeSets(block_info[block_type].values())

    def onBlockChanged(self, item):
        if item.column() == self.IDX_NAME:
            visible = item.checkState() == QtCore.Qt.Checked
            block_info = item.data()
            self.blockVisibilityChanged.emit(block_info.number, visible)
        elif item.column() == self.IDX_COLOR:
            color = item.foreground().color()
            index = self._block_model.indexFromItem(item)
            name_index = index.siblingAtColumn(self.IDX_NAME)
            block_info = self._block_model.itemFromIndex(name_index).data()
            self.blockColorChanged.emit(block_info.number, color)

    def onSidesetChanged(self, item):
        pass

    def onNodesetChanged(self, item):
        pass

    def onDimensionsStateChanged(self, state):
        self.dimensionsStateChanged.emit(state == QtCore.Qt.Checked)

    def onBoundsChanged(self, bnds):
        self._x_range.setText(
            "x-range: {:.5f} to {:.5f}".format(bnds[0], bnds[1]))
        self._y_range.setText(
            "y-range: {:.5f} to {:.5f}".format(bnds[2], bnds[3]))
        self._z_range.setText(
            "z-range: {:.5f} to {:.5f}".format(bnds[4], bnds[5]))
