import os
from PyQt5 import QtCore, QtWidgets, QtGui

"""
Project type dialog
"""
class ProjectTypeDialog(QtWidgets.QDialog):

    IMAGE = 0
    MOVIE = 1
    CSV_PLOTTER = 2

    def __init__(self, parent):
        super(ProjectTypeDialog, self).__init__(parent)
        self.idx = None

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(10)

        self.type_label = QtWidgets.QLabel("Select project type")
        self.layout.addWidget(self.type_label)

        self.model = QtGui.QStandardItemModel()
        self.addProjectTypes()

        self.list_view = QtWidgets.QListView(self)
        self.list_view.setMinimumWidth(400)
        self.list_view.setModel(self.model)
        self.list_view.setViewMode(QtWidgets.QListView.IconMode)
        self.list_view.setMovement(QtWidgets.QListView.Static)
        self.list_view.setResizeMode(QtWidgets.QListView.Fixed)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.list_view.setUniformItemSizes(True)
        self.list_view.setIconSize(QtCore.QSize(64, 64))
        self.list_view.setGridSize(QtCore.QSize(96, 96))
        self.list_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.layout.addWidget(self.list_view)

        # --- buttons ---
        self.button_layout = QtWidgets.QHBoxLayout()

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

        self.button_layout.addStretch()

        self.create_button = QtWidgets.QPushButton("Create")
        self.create_button.setDefault(True)
        self.create_button.clicked.connect(self.onCreate)
        self.button_layout.addWidget(self.create_button)
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

        self.updateControls()

        self.list_view.selectionModel().selectionChanged.connect(self.onProjectTypeChanged)

    def addProjectTypes(self):
        icon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "icons")

        self.projects = [
            {
                "name": "Image",
                "icon": "picture.svg",
                "idx": self.IMAGE
            },
            {
                "name": "Movie",
                "icon": "movie.svg",
                "idx": self.MOVIE
            },
            {
                "name": "CSV plot",
                "icon": "graph.svg",
                "idx": self.CSV_PLOTTER
            }
        ]

        for p in self.projects:
            icon_file_name = os.path.join(icon_dir, p['icon'])
            icon = QtGui.QIcon(icon_file_name)
            ri = QtGui.QStandardItem(icon, p['name'])
            self.model.appendRow(ri)

    def updateControls(self):
        n_selected = len(self.list_view.selectedIndexes())
        self.create_button.setEnabled(n_selected > 0)

    def onProjectTypeChanged(self, si):
        self.updateControls()

    def onCreate(self):
        sel_idx = self.list_view.selectedIndexes()[0].row()
        self.idx = self.projects[sel_idx]['idx']
        self.accept()
