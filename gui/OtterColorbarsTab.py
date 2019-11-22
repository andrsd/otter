from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from PyQt5.QtGui import QStandardItem, QBrush, QColor
from gui.OtterObjectsTab import OtterObjectsTab
from otter import common
from otter import colorbars
import chigger

class OtterColorbarsTab(OtterObjectsTab):

    PARAMS_AXIS = [
        { 'name': 'result', 'value': None, 'hint': 'The name of the viewport with a result', 'req': True },
        { 'name': 'axis-visible', 'value': False, 'hint': 'Visibility of the axis', 'req': False },
        { 'name': 'font-size', 'value': 30, 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'font-color', 'value': [1,1,1], 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'labels-visible', 'value': True, 'hint': 'Visibility of the labels', 'req': False },
        { 'name': 'notation', 'value': 'standard', 'hint': 'The type of notation [standard, scientific, fixed, printf]', 'req': False },
        { 'name': 'num-ticks', 'value': 5, 'hint': 'The number of tick on the axis', 'req': False },
        { 'name': 'precision', 'value': None, 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'range', 'value': [0, 1], 'hint': 'The range of the axis', 'req': False },
        { 'name': 'ticks-visible', 'value': False, 'hint': 'Visibilitty of the tickmarks', 'req': False },
        { 'name': 'title', 'value': '', 'hint': 'The title of the axis', 'req': False },
    ]

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
        for i, er in ers.items():
            self.mnuAdd.addAction(er['name'], lambda : self.onAdd(i))

    def onResultAdded(self):
        self.updateControls()

    def onAdd(self, idx):
        ex_result = self.mainWindow.exodusResults()[idx]

        input_params = self.PARAMS
        self.setGroupInputParam(input_params, 'axis1', 'result', ex_result['name'])

        item = self.addGroup(input_params)
        params = self.itemParams(item)
        item.setText("[colorbar]")

        axis1_item = self.childItem(item, 'axis1')
        axis1_params = self.itemParams(axis1_item)

        axis2_item = self.childItem(item, 'axis2')
        axis2_params = self.itemParams(axis2_item)

        kwargs = common.remap(params, colorbars.ColorBar.COLORBAR_MAP)
        axis1_kwargs = common.remap(axis1_params, common.AXIS_MAP)
        axis2_kwargs = common.remap(axis2_params, common.AXIS_MAP)

        cbar = chigger.exodus.ExodusColorBar(*[ex_result['result']], **kwargs)
        cbar.setOptions('primary', **axis1_kwargs)
        cbar.setOptions('secondary', **axis2_kwargs)

        item.setData((cbar, colorbars.ColorBar.COLORBAR_MAP))
        axis1_item.setData((None, common.AXIS_MAP))
        axis2_item.setData((None, common.AXIS_MAP))

        self.windowResult.append(cbar)
        self.windowResult.update()

    def updateControls(self):
        if len(list(self.mainWindow.exodusResults().keys())) > 0:
            self.btnAdd.setEnabled(True)
        else:
            self.btnAdd.setEnabled(False)
