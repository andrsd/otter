from PyQt5 import QtWidgets, QtCore, QtGui
from otter.plugins.viz.RootProps import RootProps
from otter.plugins.viz.TextProps import TextProps


class ParamsWindow(QtWidgets.QScrollArea):
    """
    Window for entering parameters
    """

    def __init__(self, plugin, renderer):
        super().__init__()
        self.plugin = plugin
        self._vtk_renderer = renderer

        layout = self.setupWidgets()

        w = QtWidgets.QWidget()
        w.setLayout(layout)
        self.setWidget(w)
        self.setWindowTitle("Parameters")
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
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 15)
        layout.setSpacing(0)

        self._pipeline_model = QtGui.QStandardItemModel()
        self._pipeline = QtWidgets.QTreeView()
        self._pipeline.setFixedHeight(300)
        self._pipeline.setRootIsDecorated(False)
        self._pipeline.setHeaderHidden(True)
        self._pipeline.setModel(self._pipeline_model)
        self._pipeline.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        self._pipeline.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self._pipeline.selectionModel().selectionChanged.connect(
            self.onPipelineSelectionChanged)
        layout.addWidget(self._pipeline)

        self._button_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(self._button_layout)

        self._add_button = QtWidgets.QPushButton("add")
        self._button_layout.addWidget(self._add_button)

        self._add_menu = QtWidgets.QMenu()
        self._add_text = self._add_menu.addAction("Text", self.onAddText)

        self._add_button.setMenu(self._add_menu)

        self._del_button = QtWidgets.QPushButton("del")
        self._button_layout.addWidget(self._del_button)

        self._button_layout.addStretch()

        layout.addSpacing(8)

        self._properties_stack = QtWidgets.QStackedLayout()
        layout.addLayout(self._properties_stack)

        self._root_props = RootProps(self._vtk_renderer)
        self._properties_stack.addWidget(self._root_props)

        self._root = QtGui.QStandardItem()
        self._root.setText("Pipeline")
        self._root.setData(self._root_props)
        self._pipeline_model.setItem(0, 0, self._root)

        return layout

    def event(self, event):
        """
        Event callback
        """
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

    def closeEvent(self, event):
        self.plugin.settings.setValue("info/geometry", self.saveGeometry())
        event.accept()

    def onPipelineSelectionChanged(self, selected, deselected):
        if len(selected) > 0:
            index = selected.indexes()[0]
            item = self._pipeline_model.itemFromIndex(index)
            props = item.data()
            self._properties_stack.setCurrentWidget(props)

    def onAddText(self):
        text_props = TextProps()

        actor = text_props.buildVtkActor()
        if actor is not None:
            self._vtk_renderer.AddViewProp(actor)

        text_props.setFocus()
        self._properties_stack.addWidget(text_props)

        rows = self._root.rowCount()
        si = QtGui.QStandardItem()
        si.setText("Text")
        si.setData(text_props)
        self._root.insertRow(rows, si)

        index = self._pipeline_model.indexFromItem(si)
        sel_model = self._pipeline.selectionModel()
        sel_model.clearSelection()
        sel_model.setCurrentIndex(index, QtCore.QItemSelectionModel.Select)
