#!/usr/bin/env python2

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from OtterObjectsTab import OtterObjectsTab

class OtterViewportsTab(OtterObjectsTab):

    EXODUS = 0
    RELAP7_RESULT = 1
    PLOT_OVER_TIME = 2
    VPP_PLOT = 3

    PARAMS_PLOT_VARIABLE = [
        { 'name': 'name', 'value': '', 'hint': 'The name of the variable to plot', 'req': True },
        { 'name': 'width', 'value': 2, 'hint': 'The width of the line', 'req': False },
        { 'name': 'color', 'value': [1, 1, 1], 'hint': 'The color of the line', 'req': False },
        { 'name': 'label', 'value': '', 'hint': 'The name used in the legend of this plot', 'req': False }
    ]

    PARAMS_LEGEND = [
        { 'name': 'label-font-size', 'value': None, 'hint': 'The size of the font used for the label', 'req': False },
        { 'name': 'label-color', 'value': [1, 1, 1], 'hint': 'The color of the labels', 'req': False },
        { 'name': 'visible', 'value': True, 'hint': 'Is the legend visoble', 'req': False },
        { 'name': 'background', 'value': [0, 0, 0], 'hint': 'The background colot of the legend', 'req': False },
        { 'name': 'opacity', 'value': None, 'hint': 'The posititon of the viewport with a result', 'req': False },
        { 'name': 'position', 'value': [0.5, 0.5], 'hint': 'The posititon of the legend', 'req': False },
        { 'name': 'halign', 'value': 'left', 'hint': 'The horizontal alignment [left, center, right]', 'req': False },
        { 'name': 'valign', 'value': 'top', 'hint': 'The vertical alignment [top, middle, bottom]', 'req': False },
        { 'name': 'border', 'value': False, 'hint': 'Draw border around the legend', 'req': False },
        { 'name': 'border-color', 'value': [0, 0, 0], 'hint': 'The color of the border around the legend', 'req': False },
        { 'name': 'border-opacity', 'value': 0, 'hint': 'The opacoty of the legend border', 'req': False },
        { 'name': 'border-width', 'value': 0., 'hint': 'The width of the border around the legend', 'req': False },
    ]

    PARAMS_EXODUS_RESULT = [
        { 'name': 'blocks', 'value': [], 'hint': 'The name of the viewport with a result', 'req': False },
        { 'name': 'viewport', 'value': [0, 0, 1, 1], 'hint': 'The viewport', 'req': False },
        { 'name': 'file', 'value': '', 'hint': 'The file name of the Exodus II file', 'req': True },
        { 'name': 'variable', 'value': '', 'hint': 'The name of the variable', 'req': True },
        { 'name': 'title', 'value': '', 'hint': 'The title of what is being plotted', 'req': False },
        { 'name': 'cmap', 'value': 'jet', 'hint': 'The name of the color map', 'req': False },
        { 'name': 'light', 'value': None, 'hint': 'IDK', 'req': False },
        { 'name': 'range', 'value': [0, 100], 'hint': 'The value range of the variable', 'req': False },
    ]

    PARAMS_RELAP7_RESULT = [
        { 'name': 'blocks', 'value': [], 'hint': 'The name of the viewport with a result', 'req': False },
        { 'name': 'viewport', 'value': [0, 0, 1, 1], 'hint': 'The viewport', 'req': False },
        { 'name': 'input-file', 'value': '', 'hint': 'The file name of the RELAP-7 input file', 'req': True },
        { 'name': 'exodus-file', 'value': '', 'hint': 'The file name of the Exodus II file', 'req': True },
        { 'name': 'variable', 'value': '', 'hint': 'The name of the variable', 'req': True },
        { 'name': 'title', 'value': '', 'hint': 'The title of what is being plotted', 'req': False },
        { 'name': 'cmap', 'value': 'jet', 'hint': 'The name of the color map', 'req': False },
        { 'name': 'light', 'value': None, 'hint': 'IDK', 'req': False },
        { 'name': 'range', 'value': [0, 100], 'hint': 'The value range of the variable', 'req': False },
    ]

    PARAMS_PLOT_OVER_LINE = [
        { 'name': 'file', 'value': '', 'hint': 'The file name of the CSV file', 'req': True },
        { 'name': 'variables', 'value': [], 'hint': 'The list of the variables', 'req': True },
        { 'name': 'viewport', 'value': [0, 0, 1, 1], 'hint': 'The viewport', 'req': False },
        { 'name': 'x-axis', 'group': True, 'childs': OtterObjectsTab.PARAMS_AXIS, 'hint': 'X axis' },
        { 'name': 'y-axis', 'group': True, 'childs': OtterObjectsTab.PARAMS_AXIS, 'hint': 'Y axis' },
        { 'name': 'legend', 'group': True, 'childs': PARAMS_LEGEND, 'hint': 'The legend' },
    ]

    PARAMS_VPP_PLOT = [
        { 'name': 'exodus-file', 'value': '', 'hint': 'The file name of the Exodus II file', 'req': True },
        { 'name': 'csv-file', 'value': '', 'hint': 'The file name of the CSV file', 'req': True },
        { 'name': 'variables', 'value': [], 'hint': 'The list of the variables', 'req': True },
        { 'name': 'viewport', 'value': [0, 0, 1, 1], 'hint': 'The viewport', 'req': False },
        { 'name': 'legend', 'group': True, 'childs': PARAMS_LEGEND, 'hint': 'The legend' },
        { 'name': 'x-axis', 'group': True, 'childs': OtterObjectsTab.PARAMS_AXIS, 'hint': 'X axis' },
        { 'name': 'y-axis', 'group': True, 'childs': OtterObjectsTab.PARAMS_AXIS, 'hint': 'Y axis' },
    ]

    def __init__(self, parent, chigger_window):
        super(OtterViewportsTab, self).__init__(parent, chigger_window)

    def name(self):
        return "VPs"

    def buildAddButton(self):
        btn = QPushButton("Add", self)
        mnu = QMenu("Add", self)
        mnu.addAction("Exodus result", lambda : self.onAdd(self.EXODUS))
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
        item = self.addGroup(self.PARAMS_EXODUS_RESULT, spanned = False)
        item.setText("[exodus]")

    def addRELAP7Result(self):
        item = self.addGroup(self.PARAMS_RELAP7_RESULT, spanned = False)
        item.setText("[RELAP-7 result]")

    def addPlotOverLine(self):
        item = self.addGroup(self.PARAMS_PLOT_OVER_LINE, spanned = False)
        item.setText("[plot over line]")

    def addVPPPlot(self):
        item = self.addGroup(self.PARAMS_VPP_PLOT, spanned = False)
        item.setText("[vpp plot]")

    def toText(self):
        str = ""
        str += "viewports = [\n"
        str += "]\n"

        return str
