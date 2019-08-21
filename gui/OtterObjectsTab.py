#!/usr/bin/env python2

from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
import common

class OtterObjectsTab(QWidget):

    modified = pyqtSignal()

    INDENT = 14

    PARAMS_AXIS = [
        { 'name': 'num-ticks', 'value': None, 'hint': 'The number of tick on the axis', 'req': False },
        { 'name': 'range', 'value': [0, 1], 'hint': 'The range of the axis', 'req': False },
        { 'name': 'font-size', 'value': None, 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'font-color', 'value': [1,1,1], 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'title', 'value': [1,1,1], 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'grid', 'value': True, 'hint': 'Show the grid', 'req': False },
        { 'name': 'grid-color', 'value': [0.25, 0.25, 0.25], 'hint': 'The color of the grid', 'req': False },
        { 'name': 'precision', 'value': 0, 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'notation', 'value': None, 'hint': 'The type of notation [standard, scientific, fixed, printf]', 'req': False },
        { 'name': 'ticks-visible', 'value': True, 'hint': 'Visibilitty of the tickmarks', 'req': False },
        { 'name': 'axis-visible', 'value': True, 'hint': 'Visibility of the axis', 'req': False },
        { 'name': 'labels-visible', 'value': True, 'hint': 'Visibility of the labels', 'req': False },
    ]

    def __init__(self, parent, chigger_window):
        super(OtterObjectsTab, self).__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 3)
        self.setLayout(layout)

        btn = self.buildAddButton()
        layout.addWidget(btn)

        self.model = QStandardItemModel(0, 2, self)
        self.model.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.model.sort(0, Qt.AscendingOrder)
        self.model.itemChanged.connect(self.onItemChanged)

        self.ctlObjects = QTreeView(self)
        self.ctlObjects.setModel(self.model)
        self.ctlObjects.header().resizeSection(0, 140)
        self.ctlObjects.setRootIsDecorated(False)
        self.ctlObjects.setIndentation(OtterObjectsTab.INDENT)
        layout.addWidget(self.ctlObjects)

        self.chiggerWindow = chigger_window

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

            chigger_object, map = parent.data()
            kwargs = common.remap(params, map)
            for key, val in kwargs.items():
                chigger_object.setOption(key, val)
            chigger_object.update()
            self.chiggerWindow.update()

        self.modified.emit()

    def addGroup(self, params, spanned = True):
        self.model.blockSignals(True)
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
        self.model.blockSignals(False)
        self.model.sort(0, Qt.AscendingOrder)
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
        if val == None:
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
        else:
            child = QStandardItem(str(val))
            child.setEditable(True)
        parent.setChild(idx, 1, child)

    def toPython(self, value):
        if isinstance(value, bool):
            return value
        elif value[0] == '[' and value[-1] == ']':
            value = value[1:-1]
            str_array = [x.strip() for x in value.split(',')]
            return [ float(val) for val in str_array]
        elif value[0] == '(' and value[-1] == ')':
            value = value[1:-1]
            str_array = [x.strip() for x in value.split(',')]
            return [ float(val) for val in str_array]
        else:
            try:
                return float(value)
            except ValueError:
                return value
