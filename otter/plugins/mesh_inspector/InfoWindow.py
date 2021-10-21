import vtk
from PyQt5 import QtWidgets, QtCore, QtGui
from otter.plugins.common.ColorPicker import ColorPicker


class InfoWindow(QtWidgets.QScrollArea):
    """
    Window for showing mesh info
    """

    IDX_NAME = 0
    IDX_COLOR = 1
    IDX_ID = 2

    blockVisibilityChanged = QtCore.pyqtSignal(int, object)
    sidesetVisibilityChanged = QtCore.pyqtSignal(int, object)
    nodesetVisibilityChanged = QtCore.pyqtSignal(int, object)
    blockColorChanged = QtCore.pyqtSignal(int, object)
    dimensionsStateChanged = QtCore.pyqtSignal(bool)
    orientationMarkerStateChanged = QtCore.pyqtSignal(bool)

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

        self._colors = [
            [156, 207, 237],
            [165, 165, 165],
            [60, 97, 180],
            [234, 234, 234],
            [197, 226, 243],
            [127, 127, 127],
            [250, 182, 0]
        ]

        self.setupWidgets()

        w = QtWidgets.QWidget()
        w.setLayout(self._layout)
        self.setWidget(w)
        self.setWindowTitle("Info")
        self.setMinimumWidth(350)
        self.setWidgetResizable(True)
        self.setWindowFlags(QtCore.Qt.Tool)

        geom = self.plugin.settings.value("info/geometry")
        default_size = QtCore.QSize(350, 700)
        if geom is None:
            self.resize(default_size)
        else:
            if not self.restoreGeometry(geom):
                self.resize(default_size)

        self.show()

    def setupWidgets(self):
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(20, 10, 20, 10)

        self._color_picker_widget = ColorPicker(self)

        self._color_picker_menu = QtWidgets.QMenu()
        self._color_picker_menu.addAction(self._color_picker_widget)

        self._color_picker_widget._color_group.buttonClicked.connect(
            self._color_picker_menu.hide)

        self._lbl_blocks = QtWidgets.QLabel("Blocks")
        self._layout.addWidget(self._lbl_blocks)
        self._block_model = QtGui.QStandardItemModel()
        self._block_model.setHorizontalHeaderLabels([
            "Name", "", "ID"
        ])
        self._block_model.itemChanged.connect(self.onBlockChanged)
        self._blocks = QtWidgets.QTreeView()
        self._blocks.setFixedHeight(250)
        self._blocks.setRootIsDecorated(False)
        self._blocks.setModel(self._block_model)
        self._blocks.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self._blocks.setColumnWidth(0, 200)
        self._blocks.setColumnWidth(1, 20)
        self._blocks.setColumnWidth(2, 50)
        self._blocks.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._blocks.customContextMenuRequested.connect(
            self.onBlockCustomContextMenu)
        self._layout.addWidget(self._blocks)

        self._lbl_sidesets = QtWidgets.QLabel("Side sets")
        self._layout.addWidget(self._lbl_sidesets)
        self._sideset_model = QtGui.QStandardItemModel()
        self._sideset_model.setHorizontalHeaderLabels([
            "Name", "", "ID"
        ])
        self._sideset_model.itemChanged.connect(self.onSidesetChanged)
        self._sidesets = QtWidgets.QTreeView()
        self._sidesets.setFixedHeight(150)
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
        self._nodesets.setFixedHeight(150)
        self._nodesets.setRootIsDecorated(False)
        self._nodesets.setModel(self._nodeset_model)
        self._nodesets.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self._nodesets.setColumnWidth(0, 220)
        self._nodesets.setColumnWidth(2, 50)
        self._nodesets.hideColumn(self.IDX_COLOR)
        self._layout.addWidget(self._nodesets)

        self._totals = QtWidgets.QTreeWidget()
        self._totals.setFixedHeight(60)
        self._totals.setIndentation(0)
        self._totals.setHeaderLabels(["Total", "Count"])
        self._total_elements = QtWidgets.QTreeWidgetItem(["Elements", ""])
        self._totals.addTopLevelItem(self._total_elements)
        self._total_nodes = QtWidgets.QTreeWidgetItem(["Nodes", ""])
        self._totals.addTopLevelItem(self._total_nodes)
        self._layout.addWidget(self._totals)

        self._lbl_dimensions = QtWidgets.QLabel("Dimensions")
        self._layout.addWidget(self._lbl_dimensions)

        self._range = QtWidgets.QTreeWidget()
        self._range.setFixedHeight(80)
        self._range.setIndentation(0)
        self._range.setHeaderLabels(["Direction", "Range"])
        self._x_range = QtWidgets.QTreeWidgetItem(["X", ""])
        self._range.addTopLevelItem(self._x_range)
        self._y_range = QtWidgets.QTreeWidgetItem(["Y", ""])
        self._range.addTopLevelItem(self._y_range)
        self._z_range = QtWidgets.QTreeWidgetItem(["Z", ""])
        self._range.addTopLevelItem(self._z_range)
        self._layout.addWidget(self._range)

        self._dimensions = QtWidgets.QCheckBox("Show dimensions")
        self._dimensions.stateChanged.connect(self.onDimensionsStateChanged)
        self._layout.addWidget(self._dimensions)

        self._ori_marker = QtWidgets.QCheckBox("Orientation marker")
        self._ori_marker.stateChanged.connect(self.onOriMarkerStateChanged)
        self._ori_marker.setCheckState(QtCore.Qt.Checked)
        self._layout.addWidget(self._ori_marker)

        self._layout.addStretch()

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

    def closeEvent(self, event):
        self.plugin.settings.setValue("info/geometry", self.saveGeometry())
        event.accept()

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
            si_clr.setData(clr_idx)
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
        for index, ns in enumerate(nodesets):
            row = self._nodeset_model.rowCount()

            si_name = QtGui.QStandardItem()
            si_name.setText(ns.name)
            si_name.setCheckable(True)
            si_name.setData(ns)
            self._nodeset_model.setItem(row, self.IDX_NAME, si_name)

            si_id = QtGui.QStandardItem()
            si_id.setText(str(ns.number))
            self._nodeset_model.setItem(row, self.IDX_ID, si_id)

    def onFileLoaded(self, params):
        if params is None:
            self.clear()
        else:
            block_info = params['block_info']
            block_type = vtk.vtkExodusIIReader.ELEM_BLOCK
            self._loadBlocks(block_info[block_type].values())
            block_type = vtk.vtkExodusIIReader.SIDE_SET
            self._loadSideSets(block_info[block_type].values())
            block_type = vtk.vtkExodusIIReader.NODE_SET
            self._loadNodeSets(block_info[block_type].values())

            total_elems = params['total_elems']
            self._total_elements.setText(1, "{:,}".format(total_elems))
            total_nodes = params['total_nodes']
            self._total_nodes.setText(1, "{:,}".format(total_nodes))

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

    def onBlockCustomContextMenu(self, point):
        index = self._blocks.indexAt(point)
        if index.isValid() and index.column() == self.IDX_COLOR:
            item = self._block_model.itemFromIndex(index)
            clr_idx = item.data()

            self._color_picker_widget.setColorIndex(clr_idx)
            self._color_picker_menu.exec(
                self._blocks.viewport().mapToGlobal(point))

            clr_idx = self._color_picker_widget.colorIndex()
            qcolor = self._color_picker_widget.color()
            item.setForeground(QtGui.QBrush(qcolor))
            item.setData(clr_idx)

    def onSidesetChanged(self, item):
        if item.column() == self.IDX_NAME:
            visible = item.checkState() == QtCore.Qt.Checked
            sideset_info = item.data()
            self.sidesetVisibilityChanged.emit(sideset_info.number, visible)

    def onNodesetChanged(self, item):
        if item.column() == self.IDX_NAME:
            visible = item.checkState() == QtCore.Qt.Checked
            nodeset_info = item.data()
            self.nodesetVisibilityChanged.emit(nodeset_info.number, visible)

    def onDimensionsStateChanged(self, state):
        self.dimensionsStateChanged.emit(state == QtCore.Qt.Checked)

    def onBoundsChanged(self, bnds):
        if len(bnds) == 6:
            x_range = "{:.5f} to {:.5f}".format(bnds[0], bnds[1])
            self._x_range.setText(1, x_range)
            y_range = "{:.5f} to {:.5f}".format(bnds[2], bnds[3])
            self._y_range.setText(1, y_range)
            z_range = "{:.5f} to {:.5f}".format(bnds[4], bnds[5])
            self._z_range.setText(1, z_range)
        else:
            self._x_range.setText(1, "")
            self._y_range.setText(1, "")
            self._z_range.setText(1, "")

    def onOriMarkerStateChanged(self, state):
        self.orientationMarkerStateChanged.emit(state == QtCore.Qt.Checked)

    def clear(self):
        self._block_model.removeRows(0, self._block_model.rowCount())
        self._sideset_model.removeRows(0, self._sideset_model.rowCount())
        self._nodeset_model.removeRows(0, self._nodeset_model.rowCount())

        self._total_elements.setText(1, "")
        self._total_nodes.setText(1, "")
