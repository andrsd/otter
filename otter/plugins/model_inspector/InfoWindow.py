from PyQt5 import QtWidgets, QtCore, QtGui


class InfoWindow(QtWidgets.QScrollArea):
    """
    Window for showing model info
    """

    IDX_NAME = 0
    IDX_COLOR = 1
    IDX_TYPE = 2

    componentVisibilityChanged = QtCore.pyqtSignal(str, object)
    componentColorChanged = QtCore.pyqtSignal(str, object)
    componentSelected = QtCore.pyqtSignal(object)
    dimensionsStateChanged = QtCore.pyqtSignal(bool)
    orientationMarkerStateChanged = QtCore.pyqtSignal(bool)

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

        self._lbl_blocks = QtWidgets.QLabel("Components")
        self._layout.addWidget(self._lbl_blocks)
        self._component_model = QtGui.QStandardItemModel()
        self._component_model.setHorizontalHeaderLabels([
            "Name", "", "Type"
        ])
        self._component_model.itemChanged.connect(self.onComponentChanged)
        self._components = QtWidgets.QTreeView()
        self._components.setFixedHeight(300)
        self._components.setRootIsDecorated(False)
        self._components.setModel(self._component_model)
        self._components.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self._components.setColumnWidth(0, 180)
        self._components.setColumnWidth(1, 20)
        self._components.setColumnWidth(2, 70)
        sel_model = self._components.selectionModel()
        sel_model.currentChanged.connect(self.onComponentCurrentChanged)
        self._layout.addWidget(self._components)

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

        self._ori_marker = QtWidgets.QCheckBox("Orientation marker")
        self._ori_marker.stateChanged.connect(self.onOriMarkerStateChanged)
        self._ori_marker.setCheckState(QtCore.Qt.Checked)
        self._layout.addWidget(self._ori_marker)

        self._layout.addStretch()

        w = QtWidgets.QWidget()
        w.setLayout(self._layout)
        self.setWidget(w)
        self.setWindowTitle("Info")
        self.setMinimumWidth(350)
        self.setWidgetResizable(True)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.show()

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

    def _loadComponents(self, components):
        self._component_model.removeRows(0, self._component_model.rowCount())
        for index, comp in enumerate(components):
            row = self._component_model.rowCount()

            si_name = QtGui.QStandardItem()
            si_name.setText(comp.name)
            si_name.setCheckable(True)
            si_name.setCheckState(QtCore.Qt.Checked)
            si_name.setData(comp)
            self._component_model.setItem(row, self.IDX_NAME, si_name)

            si_clr = QtGui.QStandardItem()
            si_clr.setText('\u25a0')
            clr_idx = index % len(self._colors)
            rgb = self._colors[clr_idx]
            color = QtGui.QColor(rgb[0], rgb[1], rgb[2])
            si_clr.setForeground(QtGui.QBrush(color))
            self._component_model.setItem(row, self.IDX_COLOR, si_clr)

            si_type = QtGui.QStandardItem()
            si_type.setText(comp.type)
            self._component_model.setItem(row, self.IDX_TYPE, si_type)

    def onFileLoaded(self, components):
        self._loadComponents(components)

    def onComponentChanged(self, item):
        if item.column() == self.IDX_NAME:
            visible = item.checkState() == QtCore.Qt.Checked
            comp = item.data()
            self.componentVisibilityChanged.emit(comp.name, visible)
        elif item.column() == self.IDX_COLOR:
            color = item.foreground().color()
            index = self._component_model.indexFromItem(item)
            name_index = index.siblingAtColumn(self.IDX_NAME)
            comp = self._component_model.itemFromIndex(name_index).data()
            self.componentColorChanged.emit(comp.name, color)

    def onDimensionsStateChanged(self, state):
        self.dimensionsStateChanged.emit(state == QtCore.Qt.Checked)

    def onBoundsChanged(self, bnds):
        self._x_range.setText(
            "x-range: {:.5f} to {:.5f}".format(bnds[0], bnds[1]))
        self._y_range.setText(
            "y-range: {:.5f} to {:.5f}".format(bnds[2], bnds[3]))
        self._z_range.setText(
            "z-range: {:.5f} to {:.5f}".format(bnds[4], bnds[5]))

    def onOriMarkerStateChanged(self, state):
        self.orientationMarkerStateChanged.emit(state == QtCore.Qt.Checked)

    def onComponentSelected(self, comp_name):
        self._components.blockSignals(True)
        if comp_name is None:
            self._components.clearSelection()
        else:
            items = self._component_model.findItems(comp_name)
            if len(items) == 1:
                index = self._component_model.indexFromItem(items[0])
                self._components.setCurrentIndex(index)
        self._components.blockSignals(False)

    def onComponentCurrentChanged(self, current, previous):
        item = self._component_model.itemFromIndex(current)
        comp_name = item.text()
        self.componentSelected.emit(comp_name)
