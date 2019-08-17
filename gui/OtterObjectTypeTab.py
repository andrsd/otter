#!/usr/bin/env python2

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeView, QComboBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class OtterObjectTypeTab(QWidget):

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
        self.ctlParams.header().resizeSection(0, 200)
        self.ctlParams.setRootIsDecorated(False)
        layout.addWidget(self.ctlParams)

        self.onTypeChanged(0)

    def onTypeChanged(self, idx):
        if idx == self.IDX_IMAGE:
            self.ctlParams.setModel(self.modelImage)
        elif idx == self.IDX_MOVIE:
            self.ctlParams.setModel(self.modelMovie)

    def populateModels(self):
        self.modelImage = self.populateParams(self.PARAMS_IMAGE)
        self.modelMovie = self.populateParams(self.PARAMS_MOVIE)

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
