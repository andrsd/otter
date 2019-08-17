#!/usr/bin/env python2

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from OtterObjectsTab import OtterObjectsTab

class OtterColorbarsTab(OtterObjectsTab):

    PARAMS_AXIS = [
        { 'name': 'result', 'value': None, 'hint': 'The name of the viewport with a result', 'req': True },
        { 'name': 'num-ticks', 'value': None, 'hint': 'The number of tick on the axis', 'req': False },
        { 'name': 'font-size', 'value': None, 'hint': 'The size of the font used for the numbers', 'req': False }
    ]

    PARAMS = [
        { 'name': 'location', 'value': None, 'hint': 'Location of the color bar [left, right, top, bottom]', 'req': False },
        { 'name': 'origin', 'value': [0, 0], 'hint': 'The position of the color bar', 'req': False },
        { 'name': 'viewport', 'value': [0, 0, 1, 1], 'hint': 'The viewport', 'req': False },
        { 'name': 'layer', 'value': 1, 'hint': 'The layer where the color bar is drawn', 'req': False },
        { 'name': 'width', 'value': 0, 'hint': 'The width of the color bar', 'req': True },
        { 'name': 'length', 'value': 0, 'hint': 'The length of the color bar', 'req': True },
        { 'name': 'axis1', 'group': True, 'childs': PARAMS_AXIS, 'hint': 'Primary axis' },
        { 'name': 'axis2', 'group': True, 'childs': PARAMS_AXIS, 'hint': 'Secondary axis' }
    ]

    def __init__(self, parent):
        super(OtterColorbarsTab, self).__init__(parent)

        self.model = QStandardItemModel(0, 2, self)
        self.model.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.model.sort(0, Qt.AscendingOrder)
        self.ctlObjects.setModel(self.model)
        self.ctlObjects.setRootIsDecorated(False)
        self.ctlObjects.setIndentation(14)

    def name(self):
        return "CBs"

    def buildAddButton(self):
        btn = QPushButton("Add", self)
        btn.clicked.connect(self.onAdd)
        return btn

    def onAdd(self):
        idx = self.model.rowCount()
        si = QStandardItem()
        si.setEditable(False)
        # FIXME: use color from the GUI color scheme
        si.setBackground(QBrush(QColor(192, 192, 192)))
        self.model.setItem(idx, si)
        self.ctlObjects.setFirstColumnSpanned(idx, QModelIndex(), True)

        for i, item in enumerate(self.PARAMS):
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

        self.ctlObjects.expand(si.index())
        self.model.sort(0, Qt.AscendingOrder)

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

    def toText(self):
        str = ""
        str += "colorbars = [\n"
        str += "]\n"

        return str
