#!/usr/bin/env python2

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeView, QComboBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from OtterWindowModifiedObserver import OtterWindowModifiedObserver
import chigger
import re

class OtterObjectTypeTab(QWidget):

    modified = pyqtSignal()

    PARAMS_IMAGE = [
        { 'name': 'size', 'value': [1536, 864], 'hint': 'The size of the rendered image', 'req': True },
        { 'name': 't', 'value': 0, 'hint': 'Simulation time', 'req': False },
        { 'name': 'time-unit', 'value': 'sec', 'hint': 'The time unit [sec, min, hour, year]', 'req': False },
        { 'name': 'output', 'value': '', 'hint': 'The file name where image will be saved. If empty, image will be redered on the screen', 'req': False }
    ]

    PARAMS_MOVIE = [
        { 'name': 'file', 'value': '', 'hint': 'The file name of the rendered movie', 'req': True },
        { 'name': 'duration', 'value': 30, 'hint': 'The duration of the movie in seconds', 'req': True },
        { 'name': 'size', 'value': [1536, 864], 'hint': 'The size of rendered movie', 'req': True },
        { 'name': 'location', 'value': '', 'hint': 'The location where the images for the movie will be rendered', 'req': True },
        { 'name': 'times', 'value': [], 'hint': 'The simulation times of the rendered images', 'req': True },
        { 'name': 'time-unit', 'value': 'sec', 'hint': 'The time unit [sec, min, hour, year]', 'req': False },
        { 'name': 'frame', 'value': 'frame_*.png', 'hint': 'The file name pattern of the rendered frames', 'req': True }
    ]

    IDX_IMAGE = 0
    IDX_MOVIE = 1

    def __init__(self, parent):
        super(OtterObjectTypeTab, self).__init__(parent)
        self.populateModels()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 3)
        self.setLayout(layout)

        self.ctlType = QComboBox(self)
        self.ctlType.addItem("Image")
        self.ctlType.addItem("Movie")
        self.ctlType.currentIndexChanged.connect(self.onTypeChanged)
        layout.addWidget(self.ctlType)

        self.ctlParams = QTreeView(self)
        self.ctlParams.setRootIsDecorated(False)
        layout.addWidget(self.ctlParams)

        self.onTypeChanged(0)

        self.windowObserver = OtterWindowModifiedObserver()
        self.windowObserver.resized.connect(self.onWindowResized)

        args = self.args()
        args['chigger'] = True
        args['observers'] = [ self.windowObserver ]
        self.chiggerWindow = chigger.RenderWindow(*[], **args)
        self.chiggerWindow.update()

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
        self.modelImage = self.populateParams(self.PARAMS_IMAGE)
        self.modelImage.itemChanged.connect(self.onParamChanged)
        self.modelMovie = self.populateParams(self.PARAMS_MOVIE)
        self.modelMovie.itemChanged.connect(self.onParamChanged)

    def populateParams(self, params):
        model = QStandardItemModel(len(params), 2, self)
        model.setHorizontalHeaderLabels(["Parameter", "Value"])
        for i, item in enumerate(params):
            si = QStandardItem(item['name'])
            si.setEditable(False)
            if 'hint' in item:
                si.setToolTip(item['hint'])
            if item['req']:
                font = si.font()
                font.setBold(True)
                si.setFont(font)
            model.setItem(i, 0, si)

            val = item['value']
            if type(val) == bool:
                si = QStandardItem()
                si.setEditable(False)
                si.setCheckable(True)
                if val:
                    si.setCheckState(Qt.Checked)
                else:
                    si.setCheckState(Qt.Unchecked)
            elif type(val) == str:
                si = QStandardItem(val)
                si.setEditable(True)
            else:
                si = QStandardItem(str(val))
                si.setEditable(True)
            model.setItem(i, 1, si)
        model.sort(0, Qt.AscendingOrder)
        return model

    def onParamChanged(self, item):
        model = item.model()
        row = item.row()
        name = model.item(row, 0).text().encode("ascii")
        value = item.text().encode("ascii")
        param = self.toPython(value)
        self.chiggerWindow.setOption(name, param)
        self.chiggerWindow.update()

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

    def toPython(self, value):
        if value[0] == '[' and value[-1] == ']':
            str_array = re.findall('\d+', value)
            return [ int(val) for val in str_array]
        elif value[0] == '(' and value[-1] == ')':
            str_array = re.findall('\d+', value)
            return [ int(val) for val in str_array]
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
            name = model.item(idx, 0).text().encode("ascii")
            value = model.item(idx, 1).text().encode("ascii")
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

        str = ""
        str += "{} = {{\n".format(obj_type)
        for name, value in self.args().iteritems():
            if isinstance(value, basestring):
                str += "    '{}': '{}',\n".format(name, value)
            else:
                str += "    '{}': {},\n".format(name, value)

        str += "    'viewports': viewports,\n"
        str += "    'colorbars': colorbars,\n"
        str += "    'annotations': annotations\n"
        str += "}\n"
        str += "\n"
        str += "otter.render({})\n".format(obj_type)

        return str
