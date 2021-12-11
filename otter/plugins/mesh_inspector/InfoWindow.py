from PyQt5 import QtWidgets, QtCore, QtGui
from otter.plugins.common.ColorPicker import ColorPicker
from otter.plugins.common.ExpandableWidget import ExpandableWidget
from otter.plugins.common.HLine import HLine
from otter.OTreeView import OTreeView


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

    def __init__(self, plugin, parent=None):
        super().__init__(parent)
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
        self.setMinimumWidth(300)
        self.setWidgetResizable(True)

        self.show()

    def setupWidgets(self):
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(20, 10, 20, 10)
        self._layout.setSpacing(8)

        self._color_picker = ColorPicker(self)
        self._color_picker.colorChanged.connect(self.onBlockColorPicked)

        self._lbl_info = QtWidgets.QLabel("Blocks")
        self._lbl_info.setStyleSheet("""
            color: #444;
            font-weight: bold;
            """)
        self._layout.addWidget(self._lbl_info)

        self._block_model = QtGui.QStandardItemModel()
        self._block_model.setHorizontalHeaderLabels([
            "Name", "", "ID"
        ])
        self._block_model.itemChanged.connect(self.onBlockChanged)
        self._blocks = OTreeView()
        self._blocks.setFixedHeight(250)
        self._blocks.setRootIsDecorated(False)
        self._blocks.setModel(self._block_model)
        self._blocks.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self._blocks.setColumnWidth(0, 170)
        self._blocks.setColumnWidth(1, 20)
        self._blocks.setColumnWidth(2, 40)
        self._blocks.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._blocks.customContextMenuRequested.connect(
            self.onBlockCustomContextMenu)
        self._layout.addWidget(self._blocks)

        self._layout.addWidget(HLine())

        self._sideset_model = QtGui.QStandardItemModel()
        self._sideset_model.setHorizontalHeaderLabels([
            "Name", "", "ID"
        ])
        self._sideset_model.itemChanged.connect(self.onSidesetChanged)
        self._sidesets = OTreeView()
        self._sidesets.setFixedHeight(150)
        self._sidesets.setRootIsDecorated(False)
        self._sidesets.setModel(self._sideset_model)
        self._sidesets.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self._sidesets.setColumnWidth(0, 190)
        self._sidesets.setColumnWidth(2, 40)
        self._sidesets.hideColumn(self.IDX_COLOR)

        self._sidesets_expd = ExpandableWidget("Side sets")
        self._sidesets_expd.setWidget(self._sidesets)
        self._layout.addWidget(self._sidesets_expd)

        self._layout.addWidget(HLine())

        self._nodesets = OTreeView()
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
        self._nodesets.setColumnWidth(0, 190)
        self._nodesets.setColumnWidth(2, 40)
        self._nodesets.hideColumn(self.IDX_COLOR)

        self._nodesets_expd = ExpandableWidget("Node sets")
        self._nodesets_expd.setWidget(self._nodesets)
        self._layout.addWidget(self._nodesets_expd)

        self._layout.addWidget(HLine())

        self._totals = QtWidgets.QTreeWidget()
        self._totals.setFixedHeight(60)
        self._totals.setIndentation(0)
        self._totals.setHeaderLabels(["Total", "Count"])
        self._total_elements = QtWidgets.QTreeWidgetItem(["Elements", ""])
        self._totals.addTopLevelItem(self._total_elements)
        self._total_nodes = QtWidgets.QTreeWidgetItem(["Nodes", ""])
        self._totals.addTopLevelItem(self._total_nodes)

        self._totals_expd = ExpandableWidget("Summary")
        self._totals_expd.setWidget(self._totals)
        self._layout.addWidget(self._totals_expd)

        self._layout.addWidget(HLine())

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        self._range = QtWidgets.QTreeWidget()
        self._range.setFixedHeight(80)
        self._range.setIndentation(0)
        self._range.setHeaderLabels(["Dimension", "Range"])
        self._x_range = QtWidgets.QTreeWidgetItem(["X", ""])
        self._range.addTopLevelItem(self._x_range)
        self._y_range = QtWidgets.QTreeWidgetItem(["Y", ""])
        self._range.addTopLevelItem(self._y_range)
        self._z_range = QtWidgets.QTreeWidgetItem(["Z", ""])
        self._range.addTopLevelItem(self._z_range)
        layout.addWidget(self._range)

        self._dimensions = QtWidgets.QCheckBox("Show dimensions")
        self._dimensions.stateChanged.connect(self.onDimensionsStateChanged)
        layout.addWidget(self._dimensions)

        w = QtWidgets.QWidget()
        w.setLayout(layout)

        self._range_expd = ExpandableWidget("Dimensions")
        self._range_expd.setWidget(w)
        self._layout.addWidget(self._range_expd)

        self._layout.addWidget(HLine())

        self._layout.addStretch()

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

    def closeEvent(self, event):
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
            si_clr.setData(color)
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
            self._loadBlocks(params['blocks'])
            self._loadSideSets(params['sidesets'])
            self._loadNodeSets(params['nodesets'])
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

    def _onNameContextMenu(self, item, point):
        menu = QtWidgets.QMenu()
        if item.checkState() == QtCore.Qt.Checked:
            menu.addAction("Hide", self.onHideBlock)
            menu.addAction("Hide others", self.onHideOtherBlocks)
            menu.addAction("Hide all", self.onHideAllBlocks)
        else:
            menu.addAction("Show", self.onShowBlock)
            menu.addAction("Show all", self.onShowAllBlocks)
        menu.addSeparator()
        menu.addAction("Appearance...", self.onAppearance)
        menu.exec(point)

    def onBlockCustomContextMenu(self, point):
        index = self._blocks.indexAt(point)
        if index.isValid():
            item = self._block_model.itemFromIndex(index)
            self._onNameContextMenu(
                item, self._blocks.viewport().mapToGlobal(point))

    def onAppearance(self):
        selection_model = self._blocks.selectionModel()
        indexes = selection_model.selectedIndexes()
        if len(indexes) == 0:
            return
        index = indexes[0]
        clr_index = index.siblingAtColumn(self.IDX_COLOR)
        qcolor = self._block_model.itemFromIndex(clr_index).data()
        self._color_picker.setData(clr_index)
        self._color_picker.setColor(qcolor)
        self._color_picker.show()

        geom = self.parent().geometry()
        low_left = QtCore.QPoint(geom.left(), geom.bottom())
        ll = self.mapToGlobal(low_left)
        ll.setY(ll.y() - self._color_picker.geometry().height() - 20)
        ll.setX(ll.x() - self._color_picker.geometry().width() - 5)
        self._color_picker.move(ll)

    def onBlockColorPicked(self, qcolor):
        index = self._color_picker.data()
        item = self._block_model.itemFromIndex(index)
        item.setForeground(QtGui.QBrush(qcolor))
        item.setData(qcolor)

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

    def clear(self):
        self._block_model.removeRows(0, self._block_model.rowCount())
        self._sideset_model.removeRows(0, self._sideset_model.rowCount())
        self._nodeset_model.removeRows(0, self._nodeset_model.rowCount())

        self._total_elements.setText(1, "")
        self._total_nodes.setText(1, "")

    def onHideBlock(self):
        selection_model = self._blocks.selectionModel()
        indexes = selection_model.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            item = self._block_model.itemFromIndex(index)
            item.setCheckState(QtCore.Qt.Unchecked)

    def onHideOtherBlocks(self):
        selection_model = self._blocks.selectionModel()
        indexes = selection_model.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            for row in range(self._block_model.rowCount()):
                if row != index.row():
                    item = self._block_model.item(row, 0)
                    item.setCheckState(QtCore.Qt.Unchecked)

    def onHideAllBlocks(self):
        for row in range(self._block_model.rowCount()):
            item = self._block_model.item(row, 0)
            item.setCheckState(QtCore.Qt.Unchecked)

    def onShowBlock(self):
        selection_model = self._blocks.selectionModel()
        indexes = selection_model.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            item = self._block_model.itemFromIndex(index)
            item.setCheckState(QtCore.Qt.Checked)

    def onShowAllBlocks(self):
        for row in range(self._block_model.rowCount()):
            item = self._block_model.item(row, 0)
            item.setCheckState(QtCore.Qt.Checked)
