#!/usr/bin/env python2

from PyQt5.QtCore import Qt, QVariant, QModelIndex, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from OtterParams import *
import common

class OtterObjectsTab(QWidget):

    modified = pyqtSignal()

    INDENT = 14

    PARAMS_AXIS = [
        { 'name': 'axis-visible', 'value': True, 'hint': 'Visibility of the axis', 'req': False },
        { 'name': 'font-size', 'value': None, 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'font-color', 'value': [1,1,1], 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'grid', 'value': True, 'hint': 'Show the grid', 'req': False },
        { 'name': 'grid-color', 'value': [0.25, 0.25, 0.25], 'hint': 'The color of the grid', 'req': False },
        { 'name': 'labels-visible', 'value': True, 'hint': 'Visibility of the labels', 'req': False },
        { 'name': 'notation', 'value': None, 'hint': 'The type of notation [standard, scientific, fixed, printf]', 'req': False },
        { 'name': 'num-ticks', 'value': None, 'hint': 'The number of tick on the axis', 'req': False },
        { 'name': 'precision', 'value': 0, 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'range', 'value': [0, 1], 'hint': 'The range of the axis', 'req': False },
        { 'name': 'ticks-visible', 'value': True, 'hint': 'Visibilitty of the tickmarks', 'req': False },
        { 'name': 'title', 'value': '', 'hint': 'The title of the axis', 'req': False },
    ]

    def __init__(self, parent, resultWindow):
        super(OtterObjectsTab, self).__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 3)
        self.setLayout(layout)

        btn = self.buildAddButton()
        layout.addWidget(btn)

        self.model = QStandardItemModel(0, 2, self)
        self.model.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.model.itemChanged.connect(self.onItemChanged)

        self.ctlObjects = QTreeView(self)
        self.ctlObjects.setModel(self.model)
        self.ctlObjects.header().resizeSection(0, 140)
        self.ctlObjects.setRootIsDecorated(False)
        self.ctlObjects.setItemDelegate(OtterParamDelegate(self.ctlObjects))
        self.ctlObjects.setIndentation(OtterObjectsTab.INDENT)
        layout.addWidget(self.ctlObjects)

        self.windowResult = resultWindow

    def needsName(self):
        """
        Tells the caller if we need to store the name of the group, needed for example by viewports that needs to be referenced
        by color bars.
        """
        return False

    def onItemChanged(self, item):
        parent = item.parent()
        if parent != None:
            model = item.model()
            row = item.row()

            name = parent.child(row, 0).text().encode("ascii")
            value = item.text().encode("ascii")
            if item.isCheckable():
                value = self.toPython(item.checkState() == Qt.Checked)
            else:
                value = self.toPython(value)
            params = { name: value }

            if parent.data() != None:
                chigger_object, map = parent.data()
                kwargs = common.remap(params, map)
                for key, val in kwargs.items():
                    if chigger_object.getOptions().hasOption(key):
                        chigger_object.setOption(key, val)
                chigger_object.update()
                self.windowResult.update()

        self.modified.emit()

    def addGroup(self, params, spanned = True):
        args = {}
        idx = self.model.rowCount()
        si = QStandardItem()
        si.setEditable(False)
        # FIXME: use color from the GUI color scheme
        brush = QBrush(QColor(192, 192, 192))
        si.setBackground(brush)
        self.model.setItem(idx, si)
        if spanned:
            self.ctlObjects.setFirstColumnSpanned(idx, QModelIndex(), spanned)
        else:
            si.setText("name")
            si2 = QStandardItem()
            si2.setEditable(True)
            si2.setBackground(brush)
            self.model.setItem(idx, 1, si2)

        for i, item in enumerate(params):
            if 'group' in item and item['group']:
                group = QStandardItem(item['name'])
                group.setEditable(False)
                if 'hint' in item:
                    group.setToolTip(item['hint'])
                si.setChild(i, 0, group)
                self.ctlObjects.expand(group.index())

                for j, subitem in enumerate(item['childs']):
                    self.buildChildParam(j, group, subitem)

                self.ctlObjects.setFirstColumnSpanned(i, si.index(), True)
            else:
                self.buildChildParam(i, si, item)
                args[item['name']] = item['value']

        self.ctlObjects.expand(si.index())
        self.modified.emit()
        return si, args

    def buildChildParam(self, idx, parent, item):
        child = QStandardItem(item['name'])
        child.setEditable(False)
        if 'hint' in item:
            child.setToolTip(item['hint'])
        if item['req']:
            font = child.font()
            font.setBold(True)
            child.setFont(font)
        parent.setChild(idx, 0, child)

        val = item['value']
        if 'enum' in item:
            child = QStandardItem(val)
            child.setEditable(True)
            child.setData(QVariant(OtterParamOptions(item['enum'])))
        elif val == None:
            child = QStandardItem()
            child.setEditable(True)
        elif type(val) == bool:
            child = QStandardItem()
            child.setEditable(False)
            child.setCheckable(True)
            if val:
                child.setCheckState(Qt.Checked)
            else:
                child.setCheckState(Qt.Unchecked)
        elif type(val) == str:
            child = QStandardItem(val)
            child.setEditable(True)
            if 'valid' in item:
                valid = item['valid']
            else:
                valid = None
            child.setData(QVariant(OtterParamLineEdit('str', valid)))
        elif type(val) == int:
            child = QStandardItem(str(val))
            child.setEditable(True)
            if 'limits' in item:
                limits = item['limits']
            else:
                limits = None
            child.setData(QVariant(OtterParamLineEdit('int', limits)))
        elif type(val) == float:
            child = QStandardItem(str(val))
            child.setEditable(True)
            if 'limits' in item:
                limits = item['limits']
            else:
                limits = None
            child.setData(QVariant(OtterParamLineEdit('float', limits)))
        else:
            child = QStandardItem(str(val))
            child.setEditable(True)
            if 'valid' in item:
                valid = item['valid']
            else:
                valid = None
            child.setData(QVariant(OtterParamLineEdit('str', valid)))
        parent.setChild(idx, 1, child)

    def argsGroup(self, parent):
        """
        Build python dictionary for an otter object

        Inputs:
            parent [QStandardItem] - parent item from the model, childern of this key will be stored into the python dictionary
        """

        args = {}
        for idx in range(parent.rowCount()):
            name = parent.child(idx, 0).text().encode("ascii")
            value = parent.child(idx, 1).text().encode("ascii")
            if len(value) > 0:
                args[name] = value
        return args

    def args(self):
        """
        Build python array of all otter objects as python dictionaries
        """

        args = []
        for idx in range(self.model.rowCount()):
            parent = self.model.item(idx, 0)
            if parent.hasChildren():
                argsGroup  = self.argsGroup(parent)
                if self.needsName():
                    parent_name = self.model.item(idx, 1).text().encode("ascii")
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

        str = ""
        if isinstance(value, basestring):
            str += "    " * level + "'{}': '{}',\n".format(name, value)
        else:
            str += "    " * level + "'{}': {},\n".format(name, value)
        return str

    def groupToText(self, args, level):
        """
        Convert a group of parameters into a string representation of python dictionary for outputting

        Inputs:
            args [dict] - dictionary that will be converted into a string
            level [int] - indentation level
        """

        str = "    " * level + "{\n"
        for key, val in args.items():
            str += self.argToText(key, val, level + 1)
        str += "    " * level + "},\n"
        return str

    def toText(self):
        """
        Convert all otter objects into string representation of python code for outputting
        """

        str = ""
        str += "{} = [\n".format(self.pythonName())
        for value in self.args():
            str += self.groupToText(value, 1)
        str += "]\n"
        return str

    def toPython(self, value):
        if isinstance(value, bool):
            return value
        elif len(value) == 0:
            return None
        elif value[0] == '[' and value[-1] == ']':
            value = value[1:-1]
            if len(value) > 0:
                str_array = [x.strip() for x in value.split(',')]
                return [ float(val) for val in str_array]
            else:
                return []
        elif value[0] == '(' and value[-1] == ')':
            value = value[1:-1]
            if len(value) > 0:
                str_array = [x.strip() for x in value.split(',')]
                return [ float(val) for val in str_array]
            else:
                return []
        else:
            try:
                return float(value)
            except ValueError:
                return value
