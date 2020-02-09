from PyQt5 import QtCore, QtWidgets, QtGui
from gui.OtterParams import *
from otter import common
import re

class OtterMediaTab(QtWidgets.QWidget):

    modified = QtCore.pyqtSignal()
    # When user changed the time parameter (arg: the new time)
    timeChanged = QtCore.pyqtSignal(float)
    # When user changed time unit
    timeUnitChanged = QtCore.pyqtSignal(str)

    PARAMS_IMAGE = [
        {
            'name': 'size',
            'value': [1536, 864],
            'valid': '\[\d+\, ?\d+\]',
            'hint': 'The size of the rendered image',
            'req': True
        },
        {
            'name': 'background',
            'value': [0., 0., 0.],
            'hint': 'The background color',
            'req': False
        },
        {
            'name': 'background2',
            'value': [0., 0., 0.],
            'hint': 'The second background color, when supplied this creates a gradient background',
            'req': False
        },
        {
            'name': 'gradient_background',
            'value': False,
            'hint': 'Enable/disable the use of a gradient background.',
            'req': False
        },
        {
            'name': 't',
            'value': 0.,
            'limits': [None, None],
            'hint': 'Simulation time',
            'req': False
        },
        {
            'name': 'time-unit',
            'value': 'sec',
            'enum': ['sec', 'min', 'hour', 'year'],
            'hint': 'The time unit [sec, min, hour, year]',
            'req': False
        },
        {
            'name': 'output',
            'value': '',
            'hint': 'The file name where image will be saved. If empty, image will be redered on the screen',
            'req': False
        }
    ]

    PARAMS_MOVIE = [
        {
            'name': 'duration',
            'value': 30.,
            'limits': [0, None],
            'hint': 'The duration of the movie in seconds',
            'req': True
        },
        {
            'name': 'file',
            'value': '',
            'hint': 'The file name of the rendered movie',
            'req': True
        },
        {
            'name': 'frame',
            'value': 'frame_*.png',
            'hint': 'The file name pattern of the rendered frames',
            'req': True
        },
        {
            'name': 'location',
            'value': '',
            'hint': 'The location where the images for the movie will be rendered',
            'req': True
        },
        {
            'name': 'size',
            'value': [1536, 864],
            'valid': '\[\d+\, ?\d+\]',
            'hint': 'The size of rendered movie',
            'req': True
        },
        {
            'name': 'times',
            'value': [],
            'hint': 'The simulation times of the rendered images',
            'req': True
        },
        {
            'name': 'time-unit',
            'value': 'sec',
            'enum': ['sec', 'min', 'hour', 'year'],
            'hint': 'The time unit [sec, min, hour, year]',
            'req': False
        }
    ]

    IDX_IMAGE = 0
    IDX_MOVIE = 1

    def __init__(self, parent, resultWindow):
        super(OtterMediaTab, self).__init__(parent)
        self.windowResult = resultWindow
        self.windowResult.resized.connect(self.onWindowResized)

        self.populateModels()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 3)
        self.setLayout(layout)

        self.ctlType = QtWidgets.QComboBox(self)
        self.ctlType.addItem("Image")
        self.ctlType.addItem("Movie")
        self.ctlType.currentIndexChanged.connect(self.onTypeChanged)
        layout.addWidget(self.ctlType)

        self.ctlParams = QtWidgets.QTreeView(self)
        self.ctlParams.setRootIsDecorated(False)
        self.ctlParams.setItemDelegate(OtterParamDelegate(self.ctlParams))
        self.ctlParams.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed | QtWidgets.QAbstractItemView.CurrentChanged)
        layout.addWidget(self.ctlParams)

        self.onTypeChanged(0)

    def onTypeChanged(self, idx):
        if idx == self.IDX_IMAGE:
            self.ctlParams.setModel(self.modelImage)
            self.ctlParams.header().resizeSection(0, 140)
            self.modified.emit()
        elif idx == self.IDX_MOVIE:
            self.ctlParams.setModel(self.modelMovie)
            self.ctlParams.header().resizeSection(0, 140)
            self.modified.emit()

    def populateModels(self):
        self.modelImage = QtGui.QStandardItemModel(self)
        self.modelMovie = QtGui.QStandardItemModel(self)

        self.modelImage.itemChanged.connect(self.onParamChanged)
        self.modelMovie.itemChanged.connect(self.onParamChanged)

        self.populateParams(self.modelImage, self.PARAMS_IMAGE)
        self.populateParams(self.modelMovie, self.PARAMS_MOVIE)

    def populateParams(self, model, params):
        model.setHorizontalHeaderLabels(["Parameter", "Value"])
        for i, item in enumerate(params):
            si = QtGui.QStandardItem(item['name'])
            si.setEditable(False)
            if 'hint' in item:
                si.setToolTip(item['hint'])
            if item['req']:
                font = si.font()
                font.setBold(True)
                si.setFont(font)
            si.setData(item)
            model.setItem(i, 0, si)

            val = item['value']
            if 'enum' in item:
                si = QtGui.QStandardItem(val)
                si.setEditable(True)
                si.setData(QtCore.QVariant(OtterParamOptions(item['enum'])))
            elif val == None:
                si = QtGui.QStandardItem()
                si.setEditable(True)
            elif type(val) == bool:
                si = QtGui.QStandardItem()
                si.setEditable(False)
                si.setCheckable(True)
                if val:
                    si.setCheckState(QtCore.Qt.Checked)
                else:
                    si.setCheckState(QtCore.Qt.Unchecked)
            elif type(val) == str:
                si = QtGui.QStandardItem(val)
                si.setEditable(True)
                if 'valid' in item:
                    valid = item['valid']
                else:
                    valid = None
                si.setData(QtCore.QVariant(OtterParamLineEdit('str', valid)))
            elif type(val) == int:
                si = QtGui.QStandardItem(str(val))
                si.setEditable(True)
                if 'limits' in item:
                    limits = item['limits']
                else:
                    limits = None
                si.setData(QtCore.QVariant(OtterParamLineEdit('int', limits)))
            elif type(val) == float:
                si = QtGui.QStandardItem(str(val))
                si.setEditable(True)
                if 'limits' in item:
                    limits = item['limits']
                else:
                    limits = None
                si.setData(QtCore.QVariant(OtterParamLineEdit('float', limits)))
            else:
                si = QtGui.QStandardItem(str(val))
                si.setEditable(True)
                if 'valid' in item:
                    valid = item['valid']
                else:
                    valid = None
                si.setData(QtCore.QVariant(OtterParamLineEdit('str', valid)))
            model.setItem(i, 1, si)

    def onParamChanged(self, item):
        if item.column() == 0:
            return

        model = item.model()
        row = item.row()
        name = model.item(row, 0).text()
        value = item.text()
        if name == 't':
            common.t = float(value)
            self.timeChanged.emit(common.t)
        elif name == 'time-unit':
            time_unit = str(value)
            common.setTimeUnit(time_unit)
            self.timeUnitChanged.emit(time_unit)
        elif name == 'size':
            param = self.toPython(value)
            self.windowResult.resize(param[0], param[1])
        elif name in ['output', 'location', 'duration', 'file', 'times', 'frame']:
            pass
        else:
            if item.isCheckable():
                param = self.toPython(item.checkState() == QtCore.Qt.Checked)
            else:
                param = self.toPython(value)
            self.windowResult.setParam(name, param)

    def setSizeParam(self, model, width, height):
        results = model.findItems('size')
        if len(results) == 1:
            item = results[0]
            model.item(item.row(), 1).setText("[{}, {}]".format(width, height))

    def onWindowResized(self, width, height):
        self.setSizeParam(self.modelImage, width, height)
        self.setSizeParam(self.modelMovie, width, height)

    def model(self):
        idx = self.ctlType.currentIndex()
        if idx == self.IDX_IMAGE:
            return self.modelImage
        elif idx == self.IDX_MOVIE:
            return self.modelMovie
        else:
            return None

    def selectObjectType(self, type):
        idx = self.ctlType.findText(type)
        if idx != -1:
            self.ctlType.setCurrentIndex(idx)
        else:
            print("Trying to set unknown type '{}'".format(type))

    def setObjectParams(self, params):
        for row in range(self.model().rowCount()):
            item0 = self.model().item(row)
            default_param = item0.data()
            name = item0.text()

            item1 = self.model().item(row, 1)
            if name in params:
                value = params[name]
            else:
                value = default_param['value']

            if isinstance(value, bool):
                if value:
                    item1.setCheckState(QtCore.Qt.Checked)
                else:
                    item1.setCheckState(QtCore.Qt.Unchecked)
            else:
                item1.setText(str(value))


    def toPython(self, value):
        if isinstance(value, bool):
            return value
        elif len(value) == 0:
            return None
        elif value[0] == '[' and value[-1] == ']':
            value = value[1:-1]
            if len(value) > 0:
                str_array = [x.strip() for x in value.split(',')]
                arr = []
                for val in str_array:
                    try:
                        tmp = int(val)
                        arr.append(tmp)
                    except ValueError:
                        arr.append(float(val))
                return arr
            else:
                return []
        elif value[0] == '(' and value[-1] == ')':
            value = value[1:-1]
            if len(value) > 0:
                str_array = [x.strip() for x in value.split(',')]
                arr = []
                for val in str_array:
                    try:
                        tmp = int(val)
                        arr.append(tmp)
                    except ValueError:
                        arr.append(float(val))
                return arr
            else:
                return []
        else:
            try:
                return int(value)
            except ValueError:
                return value

    def args(self):
        """
        Return dict that will be used to build a chigger object
        """
        model = self.model()
        args = {}
        for idx in range(model.rowCount()):
            name = model.item(idx, 0).text()
            item1 = model.item(idx, 1)
            if item1.isCheckable():
                if item1.checkState() == QtCore.Qt.Checked:
                    args[name] = True
                else:
                    args[name] = False
            else:
                value = item1.text()
                if value != "":
                    args[name] = self.toPython(value)

        return args

    def toText(self):
        model = self.model()
        idx = self.ctlType.currentIndex()
        if idx == self.IDX_IMAGE:
            obj_type = 'image'
        elif idx == self.IDX_MOVIE:
            obj_type = 'movie'

        s = ""
        s += "{} = {{\n".format(obj_type)
        for name, value in self.args().items():
            if isinstance(value, str):
                s += "    '{}': '{}',\n".format(name, value)
            else:
                s += "    '{}': {},\n".format(name, value)

        s += "    'viewports': viewports,\n"
        s += "    'colorbars': colorbars,\n"
        s += "    'annotations': annotations\n"
        s += "}\n"
        s += "\n"
        s += "if __name__ == '__main__':\n"
        s += "    otter.render({})\n".format(obj_type)

        return s
