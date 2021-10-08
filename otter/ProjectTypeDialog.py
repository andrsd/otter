import os
import sys
import importlib.util
import inspect
from PyQt5 import QtCore, QtWidgets, QtGui

class ProjectTypeDialog(QtWidgets.QDialog):
    """
    Project type dialog
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.idx = None
        self.plugin = None
        self.plugins_dir = None
        self.plugins = []
        self.plugin_map = {}
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
        """
        Find user plug-ins
        """
        self.plugins = []
        self.plugin_map = {}
        sys.path.append(self.plugins_dir)
        for subdir in os.listdir(self.plugins_dir):
            directory = os.path.join(self.plugins_dir, subdir)
            if os.path.isdir(directory):
                self.loadPlugin(directory)

    def loadPlugin(self, directory):
        """
        Load plug-in
        @param directory Directory containing the plugin
        """
        for file in os.listdir(directory):
            if file.endswith("Plugin.py"):
                module_name = os.path.splitext(os.path.basename(file))[0]
                sys.path.append(directory)
                temp = importlib.import_module(module_name)
                sys.path.remove(directory)

                is_class_member = lambda member, module_name=module_name: \
                    inspect.isclass(member) and member.__module__ == module_name
                for name, cls in inspect.getmembers(temp, is_class_member):
                    plugin = cls(self.parent)
                    self.plugins.append(plugin)
                    self.plugin_map[name] = plugin

    def getPluginByType(self, plugin_type):
        """
        Get plugin by type
        @param plugin_type Plug-in type
        @return Plug-in class if know, None otherwise
        """
        if plugin_type in self.plugin_map:
            return self.plugin_map[plugin_type]
        return None

    def addProjectTypes(self):
        """
        Add know types of projects (i.e plug-ins)
        """
        for plugin in self.plugins:
            ri = QtGui.QStandardItem(plugin.icon(), plugin.name())
            ri.setData(plugin)
            self.model.appendRow(ri)

    def updateControls(self):
        """
        Update controls
        """
        n_selected = len(self.list_view.selectedIndexes())
        self.create_button.setEnabled(n_selected > 0)

    def onProjectTypeChanged(self, unused_si):
        """
        Called when project selection changed
        """
        self.updateControls()

    def onCreate(self):
        """
        Called when clicked on 'Create' button
        """
        sel_idx = self.list_view.selectedIndexes()[0]
        si = self.model.itemFromIndex(sel_idx)
        self.plugin = si.data()
        self.accept()
