from PyQt5 import QtCore, QtWidgets, QtGui
from gui.OtterParams import *
from otter import common

class OtterObjectsTab(QtWidgets.QWidget):

    modified = QtCore.pyqtSignal()

    INDENT = 14

    PARAMS_AXIS = [
        { 'name': 'axis-visible', 'value': False, 'hint': 'Visibility of the axis', 'req': False },
        { 'name': 'font-size', 'value': 30, 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'font-color', 'value': [1,1,1], 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'grid', 'value': True, 'hint': 'Show the grid', 'req': False },
        { 'name': 'grid-color', 'value': [0.25, 0.25, 0.25], 'hint': 'The color of the grid', 'req': False },
        { 'name': 'labels-visible', 'value': True, 'hint': 'Visibility of the labels', 'req': False },
        { 'name': 'notation', 'value': None, 'hint': 'The type of notation [standard, scientific, fixed, printf]', 'req': False },
        { 'name': 'num-ticks', 'value': 5, 'hint': 'The number of tick on the axis', 'req': False },
        { 'name': 'precision', 'value': None, 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'range', 'value': [0, 1], 'hint': 'The range of the axis', 'req': False },
        { 'name': 'ticks-visible', 'value': True, 'hint': 'Visibilitty of the tickmarks', 'req': False },
        { 'name': 'title', 'value': '', 'hint': 'The title of the axis', 'req': False },
    ]

    def __init__(self, parent, resultWindow):
        super(OtterObjectsTab, self).__init__(parent)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.ButtonLayout = QtWidgets.QHBoxLayout()
        self.ButtonLayout.setContentsMargins(0, 0, 0, 0)
        self.ButtonLayout.setSpacing(0)

        btn = self.buildAddButton()
        btn.setMaximumWidth(62)
        self.ButtonLayout.addWidget(btn)

        self.ButtonLayout.addSpacing(2)

        self.RemoveButton = QtWidgets.QPushButton("\u2212")
        self.RemoveButton.setMaximumWidth(62)
        self.RemoveButton.clicked.connect(self.onRemove)

        self.RemoveShortcut = QtWidgets.QShortcut("Ctrl+Backspace", self)
        self.RemoveShortcut.activated.connect(self.onRemove)

        self.ButtonLayout.addWidget(self.RemoveButton)
        self.ButtonLayout.addStretch()

        self.Model = QtGui.QStandardItemModel(0, 2, self)
        self.Model.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.Model.itemChanged.connect(self.onItemChanged)

        self.Objects = QtWidgets.QTreeView(self)
        self.Objects.setModel(self.Model)
        self.Objects.header().resizeSection(0, 140)
        self.Objects.setRootIsDecorated(False)
        self.Objects.setItemDelegate(OtterParamDelegate(self.Objects))
        self.Objects.setIndentation(OtterObjectsTab.INDENT)
        self.Objects.selectionModel().selectionChanged.connect(self.onObjectSelectionChanged)
        self.Objects.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed | QtWidgets.QAbstractItemView.CurrentChanged)
        layout.addWidget(self.Objects)

        layout.addLayout(self.ButtonLayout)

        self.WindowResult = resultWindow

    def needsName(self):
        """
        Tells the caller if we need to store the name of the group, needed for example by viewports that needs to be referenced
        by color bars.
        """
        return False

    def itemText2Type(self, text):
        if text in self._text_to_type:
            return self._text_to_type[text]
        else:
            return None

    def childItem(self, parent, name):
        for row in range(parent.rowCount()):
            child = parent.child(row)
            if child.text() == name:
                return child
        return None

    def setInputParam(self, map, key, value, **kwargs):
        for item in map:
            if item['name'] == key:
                item['value'] = value
                for k, v in kwargs.items():
                    item[k] = v
                return

    def setGroupInputParam(self, map, group_name, key, value, **kwargs):
        for item in map:
            if item['name'] == group_name and item['group'] == True:
                self.setInputParam(item['childs'], key, value, **kwargs)
                return

    def onRemove(self):
        index = self.Objects.currentIndex()
        row = index.row()
        item = self.Model.item(row, 0)
        (obj, map) = item.data()
        self.Model.removeRow(row)
        self.WindowResult.remove(obj)
        self.WindowResult.update()
        self.modified.emit()

    def onObjectSelectionChanged(self, selected, deselected):
        index = self.Objects.currentIndex()
        parent = self.Model.itemFromIndex(index.parent())
        if parent == None:
            self.RemoveButton.setEnabled(True)
            self.RemoveShortcut.setEnabled(True)
        else:
            self.RemoveButton.setEnabled(False)
            self.RemoveShortcut.setEnabled(False)

    def onItemChanged(self, item):
        parent = item.parent()
        if parent != None and item.column() == 1:
            model = item.model()
            row = item.row()

            name = parent.child(row, 0).text()
            value = item.text()
            if item.isCheckable():
                value = self.toPython(item.checkState() == QtCore.Qt.Checked)
            else:
                value = self.toPython(value)
            params = { name: value }

            if parent.data() != None:
                chigger_object, map = parent.data()
                if chigger_object == None:
                    root = parent.parent()
                    chigger_object, group_map = root.data()

                    group_params = { parent.text(): "" }
                    group_kwargs = common.remap(group_params, group_map)
                    group = list(group_kwargs.keys())[0]

                    kwargs = common.remap(params, map)
                    for key, val in list(kwargs.items()):
                        if chigger_object.getOptions().hasOption(group) and chigger_object.getOptions()[group].hasOption(key):
                            chigger_object.setOptions(group, **{key: val})
                    chigger_object.update()
                else:
                    kwargs = common.remap(params, map)
                    for key, val in list(kwargs.items()):
                        if chigger_object.getOptions().hasOption(key):
                            chigger_object.update(**{key: val})
                self.WindowResult.update()

            self.modified.emit()

    def itemParams(self, item):
        params = {}
        for row in range(item.rowCount()):
            name = item.child(row, 0).text()
            if item.child(row, 1) != None:
                value = item.child(row, 1).text()
                if len(value) > 0:
                    params[name] = value
        return params

    def addGroup(self, params, spanned = True, name = ''):
        idx = self.Model.rowCount()
        si = QtGui.QStandardItem()
        si.setEditable(False)
        # FIXME: use color from the GUI color scheme
        brush = QtGui.QBrush(QtGui.QColor(192, 192, 192))
        si.setBackground(brush)
        self.Model.setItem(idx, si)
        if spanned:
            self.Objects.setFirstColumnSpanned(idx, QtCore.QModelIndex(), spanned)
        else:
            si.setText("name")
            si2 = QtGui.QStandardItem(name)
            si2.setEditable(True)
            si2.setBackground(brush)
            self.Model.setItem(idx, 1, si2)

        for i, item in enumerate(params):
            if 'group' in item and item['group']:
                group = QtGui.QStandardItem(item['name'])
                group.setEditable(False)
                if 'hint' in item:
                    group.setToolTip(item['hint'])
                si.setChild(i, 0, group)

                for j, subitem in enumerate(item['childs']):
                    self.buildChildParam(j, group, subitem)

                self.Objects.setFirstColumnSpanned(i, si.index(), True)
            else:
                self.buildChildParam(i, si, item)

        self.Objects.expand(si.index())
        self.modified.emit()
        return si

    def buildChildParam(self, idx, parent, item):
        child = QtGui.QStandardItem(item['name'])
        child.setEditable(False)
        if 'hint' in item:
            child.setToolTip(item['hint'])
        if item['req']:
            font = child.font()
            font.setBold(True)
            child.setFont(font)
        child.setData(item)
        parent.setChild(idx, 0, child)

        val = item['value']
        if 'enum' in item:
            child = QtGui.QStandardItem(val)
            child.setEditable(True)
            child.setData(QtCore.QVariant(OtterParamOptions(item['enum'])))
        elif 'file' in item:
            child = QtGui.QStandardItem(val)
            child.setEditable(True)
            child.setData(QtCore.QVariant(OtterParamFilePicker(item['file'])))
        elif val == None:
            child = QtGui.QStandardItem()
            child.setEditable(True)
        elif type(val) == bool:
            child = QtGui.QStandardItem()
            child.setEditable(False)
            child.setCheckable(True)
            if val:
                child.setCheckState(QtCore.Qt.Checked)
            else:
                child.setCheckState(QtCore.Qt.Unchecked)
        elif type(val) == str:
            child = QtGui.QStandardItem(val)
            child.setEditable(True)
            if 'valid' in item:
                valid = item['valid']
            else:
                valid = None
            child.setData(QtCore.QVariant(OtterParamLineEdit('str', valid)))
        elif type(val) == int:
            child = QtGui.QStandardItem(str(val))
            child.setEditable(True)
            if 'limits' in item:
                limits = item['limits']
            else:
                limits = None
            child.setData(QtCore.QVariant(OtterParamLineEdit('int', limits)))
        elif type(val) == float:
            child = QtGui.QStandardItem(str(val))
            child.setEditable(True)
            if 'limits' in item:
                limits = item['limits']
            else:
                limits = None
            child.setData(QtCore.QVariant(OtterParamLineEdit('float', limits)))
        else:
            child = QtGui.QStandardItem(str(val))
            child.setEditable(True)
            if 'valid' in item:
                valid = item['valid']
            else:
                valid = None
            child.setData(QtCore.QVariant(OtterParamLineEdit('str', valid)))
        parent.setChild(idx, 1, child)

    def populate(self, items):
        for params in items:
            self.addObject(params)

    def setObjectParams(self, obj_item, params):
        for row in range(obj_item.rowCount()):
            item0 = obj_item.child(row)
            default_param = item0.data()
            name = item0.text()

            item1 = obj_item.child(row, 1)
            if item1 != None:
                if name in params:
                    value = params[name]
                else:
                    value = default_param['value']

                if isinstance(value, bool):
                    if value:
                        item1.setCheckState(QtCore.Qt.Checked)
                    else:
                        item1.setCheckState(QtCore.Qt.Unchecked)
                elif value != None:
                    item1.setText(str(value))

    def getChiggerObjects(self):
        objects = []

        for row in range(self.Model.rowCount()):
            item = self.Model.item(row, 0)
            (obj, map) = item.data()
            objects.append(obj)

        return objects

    def argsGroup(self, parent):
        """
        Build python dictionary for an otter object

        Inputs:
            parent [QtGui.QStandardItem] - parent item from the model, childern of this key will be stored into the python dictionary
        """

        args = {}
        for idx in range(parent.rowCount()):
            child0 = parent.child(idx, 0)
            name = child0.text()

            child1 = parent.child(idx, 1)
            if child1 != None:
                value = child1.text()
                if len(value) > 0:
                    args[name] = value
            else:
                argsGroup = self.argsGroup(child0)
                args[name] = argsGroup

        type = self.itemText2Type(parent.text())
        if type != None:
            args['type'] = type

        return args

    def args(self):
        """
        Build python array of all otter objects as python dictionaries
        """

        args = []
        for idx in range(self.Model.rowCount()):
            parent = self.Model.item(idx, 0)
            if parent.hasChildren():
                argsGroup = self.argsGroup(parent)
                if self.needsName():
                    parent_name = self.Model.item(idx, 1).text()
                    argsGroup['name'] = parent_name
                args.append(argsGroup)

        return args

    def argToText(self, name, value, level):
        """
        Convert a parameter into a string representation of python dictionary key for outputting

        Inputs:
            name [string]
            value [string]
            level [int]
        """

        s = ""
        if isinstance(value, str):
            s += "    " * level + "'{}': '{}',\n".format(name, value)
        elif isinstance(value, dict):
            s += "    " * level + "'{}':\n".format(name)
            s += self.groupToText(value, level + 1)
        else:
            s += "    " * level + "'{}': {},\n".format(name, value)
        return s

    def groupToText(self, args, level):
        """
        Convert a group of parameters into a string representation of python dictionary for outputting

        Inputs:
            args [dict] - dictionary that will be converted into a string
            level [int] - indentation level
        """

        s = "    " * level + "{\n"
        for key, val in list(args.items()):
            s += self.argToText(key, val, level + 1)
        s += "    " * level + "},\n"
        return s

    def toText(self):
        """
        Convert all otter objects into string representation of python code for outputting
        """

        s = ""
        s += "{} = [\n".format(self.pythonName())
        for value in self.args():
            s += self.groupToText(value, 1)
        s += "]\n"
        return s

    def toPython(self, value):
        if isinstance(value, bool):
            return value
        elif len(value) == 0:
            return None
        elif value[0] == '[' and value[-1] == ']':
            value = value[1:-1]
            if len(value) > 0:
                str_array = [x.strip() for x in value.split(',')]
                res = []
                for val in str_array:
                    if val[0] == "'" and val[-1] == "'":
                        res.append(val[1:-1])
                    else:
                        res.append(float(val))
                return res
            else:
                return []
        elif value[0] == '(' and value[-1] == ')':
            value = value[1:-1]
            if len(value) > 0:
                str_array = [x.strip() for x in value.split(',')]
                res = []
                for val in str_array:
                    if val[0] == "'" and val[-1] == "'":
                        res.append(val[1:-1])
                    else:
                        res.append(float(val))
            else:
                return []
        else:
            try:
                return float(value)
            except ValueError:
                return value
