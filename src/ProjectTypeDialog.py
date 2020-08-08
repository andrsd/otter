import os, sys
import importlib.util
import inspect
from PyQt5 import QtCore, QtWidgets, QtGui
from plugins import Plugin

"""
Project type dialog
"""
class ProjectTypeDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super(ProjectTypeDialog, self).__init__(parent)
        self.idx = None
        self.plugin = None
        self.plugins_dir = None
        self.parent = parent

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(10)

        self.type_label = QtWidgets.QLabel("Select project type")
        self.layout.addWidget(self.type_label)

        self.model = QtGui.QStandardItemModel()

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

        self.list_view.selectionModel().selectionChanged.connect(self.onProjectTypeChanged)
        self.list_view.doubleClicked.connect(self.onCreate)

    def findPlugins(self):
        self.plugins = []
        sys.path.append(self.plugins_dir)
        for subdir in os.listdir(self.plugins_dir):
            dir = os.path.join(self.plugins_dir, subdir)
            if os.path.isdir(dir):
                self.loadPlugin(dir)

    def loadPlugin(self, dir):
        for file in os.listdir(dir):
            if file.endswith("Plugin.py"):
                module_name = os.path.splitext(os.path.basename(file))[0]
                sys.path.append(dir)
                temp = importlib.import_module(module_name)
                sys.path.remove(dir)

                is_class_member = lambda member: inspect.isclass(member) and member.__module__ == module_name
                for name, cls in inspect.getmembers(temp, is_class_member):
                    self.plugins.append(cls(self.parent))

    def addProjectTypes(self):
        for plugin in self.plugins:
            ri = QtGui.QStandardItem(plugin.icon(), plugin.name())
            ri.setData(plugin)
            self.model.appendRow(ri)

    def updateControls(self):
        n_selected = len(self.list_view.selectedIndexes())
        self.create_button.setEnabled(n_selected > 0)

    def onProjectTypeChanged(self, si):
        self.updateControls()

    def onCreate(self):
        sel_idx = self.list_view.selectedIndexes()[0]
        si = self.model.itemFromIndex(sel_idx)
        self.plugin = si.data()
        self.accept()
