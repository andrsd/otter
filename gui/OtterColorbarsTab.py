#!/usr/bin/env python2

from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from PyQt5.QtGui import QStandardItem, QBrush, QColor
from OtterObjectsTab import OtterObjectsTab
import otter
import common
import chigger

class OtterColorbarsTab(OtterObjectsTab):

    PARAMS_AXIS = [
        { 'name': 'result', 'value': None, 'hint': 'The name of the viewport with a result', 'req': True },
    ] + OtterObjectsTab.PARAMS_AXIS

    PARAMS = [
        { 'name': 'length', 'value': 0.25, 'hint': 'The length of the color bar', 'req': True },
        { 'name': 'width', 'value': 0.01, 'hint': 'The width of the color bar', 'req': True },
        { 'name': 'axis1', 'group': True, 'childs': PARAMS_AXIS, 'hint': 'Primary axis' },
        { 'name': 'axis2', 'group': True, 'childs': PARAMS_AXIS, 'hint': 'Secondary axis' },
        { 'name': 'layer', 'value': 1, 'hint': 'The layer where the color bar is drawn', 'req': False },
        { 'name': 'location', 'value': 'right', 'enum': ['left', 'right', 'top', 'bottom'], 'hint': 'Location of the color bar [left, right, top, bottom]', 'req': False },
        { 'name': 'origin', 'value': [0, 0], 'hint': 'The position of the color bar', 'req': False },
        { 'name': 'viewport', 'value': [0, 0, 1, 1], 'hint': 'The viewport', 'req': False },
    ]

    def __init__(self, parent, chigger_window):
        super(OtterColorbarsTab, self).__init__(parent, chigger_window)
        self.mainWindow = parent
        self.updateControls()

    def name(self):
        return "CBs"

    def pythonName(self):
        return "colorbars"

    def buildAddButton(self):
        self.btnAdd = QPushButton("Add", self)
        self.mnuAdd = QMenu("Add", self)
        self.mnuAdd.aboutToShow.connect(self.onAddMenuAboutToShow)
        self.btnAdd.setMenu(self.mnuAdd)
        return self.btnAdd

    def onAddMenuAboutToShow(self):
        self.mnuAdd.clear()
        ers = self.mainWindow.exodusResults()
        for i, er in ers.iteritems():
            self.mnuAdd.addAction(er['name'], lambda : self.onAdd(i))

    def onResultAdded(self):
        self.updateControls()

    def onAdd(self, idx):
        item, params = self.addGroup(self.PARAMS)
        item.setText("[colorbar]")

        ex_result = self.mainWindow.exodusResults()[idx]['result']

        map = otter.colorbars.ColorBar.COLORBAR_MAP
        kwargs = common.remap(params, map)
        cbar = chigger.exodus.ExodusColorBar(*[ex_result], **kwargs)

        axis_params = self.groupParams(params, 'axis1')
        axis_map = otter.colorbars.ColorBar.AXIS_MAP
        axis_kwargs = common.remap(axis_params, axis_map)
        cbar.setOptions('primary', **axis_kwargs)

        item.setData((cbar, map))
        self.windowResult.append(cbar)
        self.windowResult.update()

    def groupParams(self, params, group_name):
        return []

    def updateControls(self):
        if len(self.mainWindow.exodusResults().keys()) > 0:
            self.btnAdd.setEnabled(True)
        else:
            self.btnAdd.setEnabled(False)
