from PyQt5.QtWidgets import QWidget, QVBoxLayout, QAbstractItemView, QMenu, \
    QGraphicsOpacityEffect, QHBoxLayout, QLabel, QSizePolicy, QPushButton
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QItemSelectionModel
from otter.OTreeView import OTreeView


class ParamsWindow(QWidget):
    """
    Window for entering parameters
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._main_wnd = parent

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("options")
        self.setStyleSheet("""
            #options, #closeButton {
                border-radius: 6px;
                background-color: rgb(0, 0, 0);
                color: #fff;
            }
            QLabel, QCheckBox {
                background-color: rgb(0, 0, 0);
                color: #fff;
            }
            """)

        self.setupWidgets()

        effect = QGraphicsOpacityEffect()
        effect.setOpacity(0.66)
        self.setGraphicsEffect(effect)

        self.setMinimumWidth(220)
        self.updateWidgets()
        self.connectSignals()

        self.setAcceptDrops(True)

    def mainWnd(self):
        return self._main_wnd

    def setupWidgets(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 6, 12, 12)
        layout.setSpacing(4)

        title_layout = QHBoxLayout()
        self._title = QLabel("Objects")
        self._title.setStyleSheet("""
            font-weight: bold;
            qproperty-alignment: AlignLeft;
            """)
        self._title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        title_layout.addWidget(self._title)

        self._close_button = QPushButton("\u2716")
        self._close_button.setObjectName("closeButton")
        self._close_button.setStyleSheet("""
            font-size: 20px;
            """)
        title_layout.addWidget(self._close_button)

        layout.addLayout(title_layout)

        layout.addSpacing(4)

        self._pipeline_model = QStandardItemModel()
        self._pipeline = OTreeView()
        self._pipeline.setRootIsDecorated(False)
        self._pipeline.setHeaderHidden(True)
        self._pipeline.setModel(self._pipeline_model)
        # self._pipeline.setItemsExpandable(False)
        self._pipeline.setRootIsDecorated(True)
        self._pipeline.setExpandsOnDoubleClick(False)
        self._pipeline.setContextMenuPolicy(Qt.CustomContextMenu)
        self._pipeline.setSelectionMode(QAbstractItemView.SingleSelection)
        self._pipeline.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self._pipeline)

        self._blocks = OTreeView()
        layout.addWidget(self._blocks)

        self.setLayout(layout)

    def connectSignals(self):
        self._pipeline.doubleClicked.connect(self.onPipelineDoubleClicked)
        self._pipeline.customContextMenuRequested.connect(
            self.onPipelineCustomContextMenu)
        self._pipeline_model.itemChanged.connect(self.onPipelineItemChanged)
        self._close_button.clicked.connect(self.hide)

    def updateWidgets(self):
        pass

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
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
        rows = self._pipeline_model.rowCount()
        si = QStandardItem()
        si.setText(name)
        si.setData(props)
        si.setEditable(True)
        self._pipeline_model.insertRow(rows, si)

        index = self._pipeline_model.indexFromItem(si)
        sel_model = self._pipeline.selectionModel()
        sel_model.clearSelection()
        sel_model.setCurrentIndex(index, QItemSelectionModel.Select)

    def clear(self):
        self._pipeline_model.removeRows(0, self._pipeline_model.rowCount())

    def _onPipelineContextMenu(self, point):
        menu = QMenu()
        menu.addAction("Rename", self.onRename)
        menu.addSeparator()
        menu.addAction("Edit...", self.onEdit)
        menu.addSeparator()
        menu.addAction("Delete", self.onDelete)
        menu.exec(point)

    def onPipelineCustomContextMenu(self, point):
        index = self._pipeline.indexAt(point)
        if index.isValid():
            point = self._pipeline.viewport().mapToGlobal(point)
            self._onPipelineContextMenu(point)

    def _getSelectedPipelineItems(self):
        selection_model = self._pipeline.selectionModel()
        indexes = selection_model.selectedIndexes()
        return indexes

    def onRename(self):
        indexes = self._getSelectedPipelineItems()
        if len(indexes) > 0:
            index = indexes[0]
            self._pipeline.edit(index)

    def onEdit(self):
        indexes = self._getSelectedPipelineItems()
        if len(indexes) > 0:
            index = indexes[0]
            item = self._pipeline_model.itemFromIndex(index)
            props = item.data()
            props.show()

    def onDelete(self):
        indexes = self._getSelectedPipelineItems()
        if len(indexes) > 0:
            index = indexes[0]
            item = self._pipeline_model.itemFromIndex(index)
            props = item.data()
            self._main_wnd.remove(props)
            self._pipeline_model.removeRow(index.row())

    def onPipelineItemChanged(self, item):
        name = item.text()
        props = item.data()
        props.setWindowTitle(name)

    def hide(self):
        super().hide()
        self._main_wnd.updateMenuBar()
