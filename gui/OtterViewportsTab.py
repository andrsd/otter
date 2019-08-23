#!/usr/bin/env python2

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from OtterObjectsTab import OtterObjectsTab
import otter

class OtterViewportsTab(OtterObjectsTab):

    EXODUS = 0
    RELAP7_RESULT = 1
    PLOT_OVER_TIME = 2
    VPP_PLOT = 3

    PARAMS_PLOT_VARIABLE = [
        { 'name': 'name', 'value': '', 'hint': 'The name of the variable to plot', 'req': True },
        { 'name': 'color', 'value': [1, 1, 1], 'hint': 'The color of the line', 'req': False },
        { 'name': 'label', 'value': '', 'hint': 'The name used in the legend of this plot', 'req': False },
        { 'name': 'width', 'value': 2, 'hint': 'The width of the line', 'req': False },
    ]

    PARAMS_LEGEND = [
        { 'name': 'background', 'value': [0, 0, 0], 'hint': 'The background colot of the legend', 'req': False },
        { 'name': 'border', 'value': False, 'hint': 'Draw border around the legend', 'req': False },
        { 'name': 'border-color', 'value': [0, 0, 0], 'hint': 'The color of the border around the legend', 'req': False },
        { 'name': 'border-opacity', 'value': None, 'limits': [0., 1.], 'hint': 'The opacoty of the legend border', 'req': False },
        { 'name': 'border-width', 'value': 0., 'hint': 'The width of the border around the legend', 'req': False },
        { 'name': 'halign', 'value': 'left', 'enum': ['left', 'center', 'right'], 'hint': 'The horizontal alignment [left, center, right]', 'req': False },
        { 'name': 'label-color', 'value': [1, 1, 1], 'hint': 'The color of the labels', 'req': False },
        { 'name': 'label-font-size', 'value': None, 'valid': '\d+', 'hint': 'The size of the font used for the label', 'req': False },
        { 'name': 'opacity', 'value': None, 'limits': [0., 1.], 'hint': 'The posititon of the viewport with a result', 'req': False },
        { 'name': 'position', 'value': [0.5, 0.5], 'hint': 'The posititon of the legend', 'req': False },
        { 'name': 'valign', 'value': 'top', 'enum': ['top', 'middle', 'bottom'], 'hint': 'The vertical alignment [top, middle, bottom]', 'req': False },
        { 'name': 'visible', 'value': True, 'hint': 'Is the legend visoble', 'req': False },
    ]

    PARAMS_EXODUS_RESULT = [
        { 'name': 'file', 'value': '', 'hint': 'The file name of the Exodus II file', 'req': True },
        { 'name': 'variable', 'value': '', 'hint': 'The name of the variable', 'req': True },
        { 'name': 'blocks', 'value': [], 'hint': 'The name of the viewport with a result', 'req': False },
        { 'name': 'cmap', 'value': 'jet', 'hint': 'The name of the color map', 'req': False },
        { 'name': 'light', 'value': None, 'hint': 'IDK', 'req': False },
        { 'name': 'range', 'value': [0, 100], 'hint': 'The value range of the variable', 'req': False },
        { 'name': 'title', 'value': '', 'hint': 'The title of what is being plotted', 'req': False },
        { 'name': 'viewport', 'value': [0, 0, 1, 1], 'hint': 'The viewport', 'req': False },
    ]

    PARAMS_RELAP7_RESULT = [
        { 'name': 'exodus-file', 'value': '', 'hint': 'The file name of the Exodus II file', 'req': True },
        { 'name': 'input-file', 'value': '', 'hint': 'The file name of the RELAP-7 input file', 'req': True },
        { 'name': 'blocks', 'value': [], 'hint': 'The name of the viewport with a result', 'req': False },
        { 'name': 'cmap', 'value': 'jet', 'hint': 'The name of the color map', 'req': False },
        { 'name': 'light', 'value': None, 'hint': 'IDK', 'req': False },
        { 'name': 'range', 'value': [0, 100], 'hint': 'The value range of the variable', 'req': False },
        { 'name': 'title', 'value': '', 'hint': 'The title of what is being plotted', 'req': False },
        { 'name': 'variable', 'value': '', 'hint': 'The name of the variable', 'req': True },
        { 'name': 'viewport', 'value': [0, 0, 1, 1], 'hint': 'The viewport', 'req': False },
    ]

    PARAMS_PLOT_OVER_LINE = [
        { 'name': 'file', 'value': '', 'hint': 'The file name of the CSV file', 'req': True },
        { 'name': 'variables', 'value': [], 'hint': 'The list of the variables', 'req': True },
        { 'name': 'legend', 'group': True, 'childs': PARAMS_LEGEND, 'hint': 'The legend' },
        { 'name': 'viewport', 'value': [0, 0, 1, 1], 'hint': 'The viewport', 'req': False },
        { 'name': 'x-axis', 'group': True, 'childs': OtterObjectsTab.PARAMS_AXIS, 'hint': 'X axis' },
        { 'name': 'y-axis', 'group': True, 'childs': OtterObjectsTab.PARAMS_AXIS, 'hint': 'Y axis' },
    ]

    PARAMS_VPP_PLOT = [
        { 'name': 'csv-file', 'value': '', 'hint': 'The file name of the CSV file', 'req': True },
        { 'name': 'exodus-file', 'value': '', 'hint': 'The file name of the Exodus II file', 'req': True },
        { 'name': 'variables', 'value': [], 'hint': 'The list of the variables', 'req': True },
        { 'name': 'legend', 'group': True, 'childs': PARAMS_LEGEND, 'hint': 'The legend' },
        { 'name': 'viewport', 'value': [0, 0, 1, 1], 'hint': 'The viewport', 'req': False },
        { 'name': 'x-axis', 'group': True, 'childs': OtterObjectsTab.PARAMS_AXIS, 'hint': 'X axis' },
        { 'name': 'y-axis', 'group': True, 'childs': OtterObjectsTab.PARAMS_AXIS, 'hint': 'Y axis' },
    ]

    def __init__(self, parent, chigger_window):
        super(OtterViewportsTab, self).__init__(parent, chigger_window)

    def name(self):
        return "VPs"

    def pythonName(self):
        return "viewports"

    def needsName(self):
        return True

    def buildAddButton(self):
        btn = QPushButton("Add", self)
        mnu = QMenu("Add", self)
        mnu.addAction("Exodus result", lambda : self.onAdd(self.EXODUS))
        if otter.HAVE_RELAP7:
            mnu.addAction("RELAP-7 result", lambda : self.onAdd(self.RELAP7_RESULT))
        mnu.addAction("Plot over time", lambda : self.onAdd(self.PLOT_OVER_TIME))
        mnu.addAction("VPP Plot", lambda : self.onAdd(self.VPP_PLOT))
        btn.setMenu(mnu)
        return btn

    def onAdd(self, type):
        if type == self.EXODUS:
            self.addExodusResult()
        elif type == self.RELAP7_RESULT:
            self.addRELAP7Result()
        elif type == self.PLOT_OVER_TIME:
            self.addPlotOverLine()
        elif type == self.VPP_PLOT:
            self.addVPPPlot()

    def addExodusResult(self):
        item, params = self.addGroup(self.PARAMS_EXODUS_RESULT, spanned = False)
        item.setText("[exodus]")

    def addRELAP7Result(self):
        item, params = self.addGroup(self.PARAMS_RELAP7_RESULT, spanned = False)
        item.setText("[RELAP-7 result]")

    def addPlotOverLine(self):
        item, params = self.addGroup(self.PARAMS_PLOT_OVER_LINE, spanned = False)
        item.setText("[plot over line]")

    def addVPPPlot(self):
        item, params = self.addGroup(self.PARAMS_VPP_PLOT, spanned = False)
        item.setText("[vpp plot]")
