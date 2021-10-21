from PyQt5 import QtWidgets, QtCore, QtGui
from otter.plugins.model_inspector.ModelWindow import ModelWindow
from otter.plugins.common.ColorPicker import ColorPicker
from otter.plugins.model_inspector import components


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
    showLabels = QtCore.pyqtSignal(bool)

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
        self._components.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._components.customContextMenuRequested.connect(
            self.onComponentCustomContextMenu)
        sel_model = self._components.selectionModel()
        sel_model.currentChanged.connect(self.onComponentCurrentChanged)
        self._layout.addWidget(self._components)

        self._color_picker_widget = ColorPicker(self)

        self._color_picker_menu = QtWidgets.QMenu()
        self._color_picker_menu.addAction(self._color_picker_widget)

        self._color_picker_widget._color_group.buttonClicked.connect(
            self._color_picker_menu.hide)

        self._lbl_dimensions = QtWidgets.QLabel("Dimensions")
        self._layout.addWidget(self._lbl_dimensions)

        self._range = QtWidgets.QTreeWidget()
        self._range.setFixedHeight(80)
        self._range.setIndentation(0)
        self._range.setHeaderLabels(["Direction", "Range"])
        self._x_range = QtWidgets.QTreeWidgetItem(["X", "0"])
        self._range.addTopLevelItem(self._x_range)
        self._y_range = QtWidgets.QTreeWidgetItem(["Y", "0"])
        self._range.addTopLevelItem(self._y_range)
        self._z_range = QtWidgets.QTreeWidgetItem(["Z", "0"])
        self._range.addTopLevelItem(self._z_range)
        self._layout.addWidget(self._range)

        self._dimensions = QtWidgets.QCheckBox("Show dimensions")
        self._dimensions.stateChanged.connect(self.onDimensionsStateChanged)
        self._layout.addWidget(self._dimensions)

        self._show_labels = QtWidgets.QCheckBox("Show labels")
        self._show_labels.stateChanged.connect(self.onShowLabelsStateChanged)
        self._layout.addWidget(self._show_labels)

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

    def _loadComponents(self, comps):
        self._component_model.removeRows(0, self._component_model.rowCount())
        for index, comp in enumerate(comps):
            if isinstance(comp, components.InvisibleComponent):
                continue

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
            si_clr.setData(clr_idx)
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
        x_range = "{:.5f} to {:.5f}".format(bnds[0], bnds[1])
        self._x_range.setText(1, x_range)
        y_range = "{:.5f} to {:.5f}".format(bnds[2], bnds[3])
        self._y_range.setText(1, y_range)
        z_range = "{:.5f} to {:.5f}".format(bnds[4], bnds[5])
        self._z_range.setText(1, z_range)

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

    def onComponentCustomContextMenu(self, point):
        index = self._components.indexAt(point)
        if index.isValid() and index.column() == self.IDX_COLOR:
            item = self._component_model.itemFromIndex(index)
            clr_idx = item.data()

            self._color_picker_widget.setColorIndex(clr_idx)
            self._color_picker_menu.exec(
                self._components.viewport().mapToGlobal(point))

            clr_idx = self._color_picker_widget.colorIndex()
            qcolor = self._color_picker_widget.color()
            item.setForeground(QtGui.QBrush(qcolor))
            item.setData(clr_idx)

    def onColorPicked(self, id):
        pass

    def onShowLabelsStateChanged(self, state):
        self.showLabels.emit(state == QtCore.Qt.Checked)
