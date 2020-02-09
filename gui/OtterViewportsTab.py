from PyQt5 import QtCore, QtWidgets
from gui.OtterObjectsTab import OtterObjectsTab
from otter import common, config
import chigger
import otter

class OtterViewportsTab(OtterObjectsTab):

    resultAdded = QtCore.pyqtSignal()

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

    PARAMS_PLOT_OVER_TIME = [
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
        self._text_to_type = {
            '[exodus]': 'ExodusResult',
            '[RELAP-7 result]': 'RELAP7Result',
            '[vpp plot]': 'VPPPlot',
            '[plot over time]': 'PlotOverTime'
        }

        self.num_results = 0
        self.exodusResults = {}

    def name(self):
        return "VPs"

    def pythonName(self):
        return "viewports"

    def needsName(self):
        return True

    def buildAddButton(self):
        btn = QtWidgets.QPushButton("   +", self)
        mnu = QtWidgets.QMenu("Add", self)
        mnu.addAction("Exodus result", lambda : self.onAdd(self.EXODUS))
        if config.HAVE_RELAP7:
            mnu.addAction("RELAP-7 result", lambda : self.onAdd(self.RELAP7_RESULT))
        mnu.addAction("Plot over time", lambda : self.onAdd(self.PLOT_OVER_TIME))
        mnu.addAction("VPP Plot", lambda : self.onAdd(self.VPP_PLOT))
        btn.setMenu(mnu)
        btn.setStyleSheet("::menu-indicator{ image: none; }")
        return btn

    def addObject(self, params):
        type = params['type']
        if type == 'ExodusResult':
            item = self.addExodusResult(params['file'])
            self.setObjectParams(item, params)
        elif type == 'RELAP7Result':
            item = self.addRELAP7Result()
            self.setObjectParams(item, params)
        elif type == 'VPPPlot':
            item = self.addVPPPlot()
            self.setObjectParams(item, params)
        elif type == 'PlotOverTime':
            item = self.addPlotOverTime(params['file'])
            self.setObjectParams(item, params)

    def onAdd(self, type):
        if type == self.EXODUS:
            file_names = QtWidgets.QFileDialog.getOpenFileName(self, 'Select ExodusII File')
            if file_names[0]:
                self.addExodusResult(file_names[0])
        elif type == self.RELAP7_RESULT:
            self.addRELAP7Result()
        elif type == self.PLOT_OVER_TIME:
            file_names = QtWidgets.QFileDialog.getOpenFileName(self, 'Select CSV File')
            if file_names[0]:
                self.addPlotOverTime(file_names[0])
        elif type == self.VPP_PLOT:
            self.addVPPPlot()

    def addExodusResult(self, exodus_file):
        kwargs = {}
        kwargs['time'] = common.t
        kwargs['timestep'] = None
        exodus_reader = chigger.exodus.ExodusReader(exodus_file, **kwargs)
        exodus_reader.update()
        vars = exodus_reader.getVariableInformation()
        var_names = []
        var_name = None
        for vn in list(vars.keys()):
            obj_type = vars[vn].object_type
            if obj_type in [chigger.exodus.ExodusReader.NODAL, chigger.exodus.ExodusReader.ELEMENTAL]:
                if var_name == None:
                    var_name = vn
                var_names.append(vn)

        input_params = self.PARAMS_EXODUS_RESULT
        self.setInputParam(input_params, 'file', exodus_file)
        self.setInputParam(input_params, 'variable', var_name, enum = var_names)

        self.num_results = self.num_results + 1
        exodus_result_name = 'result' + str(self.num_results)
        item = self.addGroup(input_params, spanned = False, name = exodus_result_name)
        params = self.itemParams(item)
        item.setText("[exodus]")

        map = otter.viewports.ViewportExodusResult.MAP
        kwargs = common.remap(params, map)
        exodus_result = chigger.exodus.ExodusResult(exodus_reader, **kwargs)
        self.exodusResults[item.row()] = { 'name' : exodus_result_name, 'result' : exodus_result }

        item.setData((exodus_result, map))
        self.windowResult.append(exodus_result)
        self.windowResult.update()

        self.resultAdded.emit()

        return item

    def addRELAP7Result(self):
        item = self.addGroup(self.PARAMS_RELAP7_RESULT, spanned = False)
        params = self.itemParams(item)
        item.setText("[RELAP-7 result]")
        return item

    def addPlotOverTime(self, cvs_file):
        item = self.addGroup(self.PARAMS_PLOT_OVER_TIME, spanned = False)
        params = self.itemParams(item)
        item.setText("[plot over time]")

        map = otter.viewports.ViewportPlotOverTime.MAP
        kwargs = common.remap(params, map)
        lines = []
        graph = chigger.graphs.Graph(*lines, **kwargs)

        item.setData((graph, map))

        item_x_axis = self.childItem(item, 'x-axis')
        item_x_axis.setData((None, common.AXIS_MAP))

        item_y_axis = self.childItem(item, 'y-axis')
        item_y_axis.setData((None, common.AXIS_MAP))

        item_legend = self.childItem(item, 'legend')
        item_legend.setData((None, common.LEGEND_MAP))

        self.windowResult.append(graph)
        self.windowResult.update()

        self.resultAdded.emit()

        return item

    def addVPPPlot(self):
        item = self.addGroup(self.PARAMS_VPP_PLOT, spanned = False)
        params = self.itemParams(item)
        item.setText("[vpp plot]")
        return item

    def onTimeChanged(self, time):
        # update time in exodus-based results
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item.text() in ['[exodus]', '[RELAP-7 result]']:
                exo, map = item.data()
                exo[0].getExodusReader().update(time = time, timestep = None)

    def onItemChanged(self, item):
        parent = item.parent()
        if parent != None:
            super(OtterViewportsTab, self).onItemChanged(item)
        else:
            if item.column() == 1:
                name = item.text()
                if item.row() in self.exodusResults:
                    self.exodusResults[item.row()]['name'] = name
