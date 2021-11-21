import os
from PyQt5 import QtWidgets, QtCore, QtGui
from otter.plugins.common.ExodusIIReader import ExodusIIReader
from otter.plugins.viz.RootProps import RootProps
from otter.plugins.viz.FileProps import FileProps
from otter.plugins.viz.TextProps import TextProps


class LoadThread(QtCore.QThread):
    """ Worker thread for loading ExodusII files """

    def __init__(self, file_name):
        super().__init__()
        if file_name.endswith('.e') or file_name.endswith('.exo'):
            self._reader = ExodusIIReader(file_name)
        else:
            self._reader = None

    def run(self):
        self._reader.load()

    def getReader(self):
        return self._reader


class ParamsWindow(QtWidgets.QScrollArea):
    """
    Window for entering parameters
    """

    def __init__(self, plugin, renderer):
        super().__init__()
        self.plugin = plugin
        self._vtk_renderer = renderer
        self._load_thread = None
        self._progress = None

        self.setAcceptDrops(True)

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
        self._add_file = self._add_menu.addAction("File", self.onAddFile)
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

    def onPipelineSelectionChanged(self, selected, deselected):
        if len(selected) > 0:
            index = selected.indexes()[0]
            item = self._pipeline_model.itemFromIndex(index)
            props = item.data()
            self._properties_stack.setCurrentWidget(props)

    def _addPipelineItem(self, props, name):
        props.setFocus()
        self._properties_stack.addWidget(props)

        rows = self._root.rowCount()
        si = QtGui.QStandardItem()
        si.setText(name)
        si.setData(props)
        self._root.insertRow(rows, si)

        index = self._pipeline_model.indexFromItem(si)
        sel_model = self._pipeline.selectionModel()
        sel_model.clearSelection()
        sel_model.setCurrentIndex(index, QtCore.QItemSelectionModel.Select)

    def onAddText(self):
        text_props = TextProps()
        actor = text_props.getVtkActor()
        if actor is not None:
            self._vtk_renderer.AddViewProp(actor)

        self._addPipelineItem(text_props, "Text")

    def onAddFile(self):
        file_name, f = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open File',
            "",
            "ExodusII files (*.e *.exo)")
        if file_name:
            self.loadFile(file_name)

    def loadFile(self, file_name):
        self._load_thread = LoadThread(file_name)
        if self._load_thread.getReader() is not None:
            self._progress = QtWidgets.QProgressDialog(
                "Loading {}...".format(os.path.basename(file_name)),
                None, 0, 0, self)
            self._progress.setWindowModality(QtCore.Qt.WindowModal)
            self._progress.setMinimumDuration(0)
            self._progress.show()

            self._load_thread.finished.connect(self.onFileLoadFinished)
            self._load_thread.start(QtCore.QThread.IdlePriority)
        else:
            self._load_thread = None
            QtWidgets.QMessageBox.critical(
                None,
                "Unsupported file format",
                "Selected file in not in a supported format.\n"
                "We support the following formats:\n"
                "  ExodusII")

    def onFileLoadFinished(self):
        reader = self._load_thread.getReader()

        file_props = FileProps(reader)
        actors = file_props.getVtkActor()
        if isinstance(actors, list):
            for act in actors:
                self._vtk_renderer.AddViewProp(act)

        file_name = os.path.basename(reader.getFileName())
        self._addPipelineItem(file_props, file_name)

        self._progress.hide()
        self._progress = None

    def clear(self):
        for i in range(self._root.rowCount()):
            child = self._root.child(i)
            data = child.data()
            actor = data.getVtkActor()
            if actor is None:
                pass
            elif isinstance(actor, list):
                for act in actor:
                    self._vtk_renderer.RemoveViewProp(act)
            else:
                self._vtk_renderer.RemoveViewProp(actor)
        self._root.removeRows(0, self._root.rowCount())
