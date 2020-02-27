from PyQt5 import QtCore, QtWidgets, QtGui
from gui.OtterParams import *
from gui.OtterOutput import *
from otter import common
import re
import os
import tempfile
import chigger

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
            'name': 'file',
            'file': 'save',
            'value': '',
            'hint': 'The file name where image will be saved. If empty, image will be rendered on the screen',
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
            'file': 'save',
            'hint': 'The file name of the rendered movie',
            'req': True
        },
        {
            'name': 'frame',
            'value': 'frame_*.png',
            'hint': 'The file name pattern of the rendered frames',
            'req': False
        },
        {
            'name': 'location',
            'value': '',
            'hint': 'The location where the images for the movie will be rendered',
            'req': False
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
        self.WindowResult = resultWindow
        self.WindowResult.resized.connect(self.onWindowResized)

        self.populateModels()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 3)
        self.setLayout(layout)

        self.Type = QtWidgets.QComboBox(self)
        self.Type.addItem("Image")
        self.Type.addItem("Movie")
        self.Type.currentIndexChanged.connect(self.onTypeChanged)
        layout.addWidget(self.Type)

        self.Params = QtWidgets.QTreeView(self)
        self.Params.setRootIsDecorated(False)
        self.Params.setItemDelegate(OtterParamDelegate(self.Params))
        self.Params.setEditTriggers(QtWidgets.QAbstractItemView.EditKeyPressed | QtWidgets.QAbstractItemView.CurrentChanged)
        layout.addWidget(self.Params)

        self.onTypeChanged(0)

    def onTypeChanged(self, idx):
        if idx == self.IDX_IMAGE:
            self.Params.setModel(self.ModelImage)
            self.Params.header().resizeSection(0, 140)
            self.modified.emit()
        elif idx == self.IDX_MOVIE:
            self.Params.setModel(self.ModelMovie)
            self.Params.header().resizeSection(0, 140)
            self.modified.emit()

    def populateModels(self):
        self.ModelImage = QtGui.QStandardItemModel(self)
        self.ModelMovie = QtGui.QStandardItemModel(self)

        self.ModelImage.itemChanged.connect(self.onParamChanged)
        self.ModelMovie.itemChanged.connect(self.onParamChanged)

        self.populateParams(self.ModelImage, self.PARAMS_IMAGE)
        self.populateParams(self.ModelMovie, self.PARAMS_MOVIE)

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
            elif 'file' in item:
                si = QtGui.QStandardItem(val)
                si.setEditable(True)
                si.setData(QtCore.QVariant(OtterParamFilePicker(item['file'])))
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
            param = toPython(value)
            self.WindowResult.resize(param[0], param[1])
        elif name in ['location', 'duration', 'file', 'times', 'frame']:
            pass
        else:
            if item.isCheckable():
                param = toPython(item.checkState() == QtCore.Qt.Checked)
            else:
                param = toPython(value)
            self.WindowResult.setParam(name, param)
        self.modified.emit()

    def setSizeParam(self, model, width, height):
        results = model.findItems('size')
        if len(results) == 1:
            item = results[0]
            model.item(item.row(), 1).setText("[{}, {}]".format(width, height))

    def onWindowResized(self, width, height):
        self.setSizeParam(self.ModelImage, width, height)
        self.setSizeParam(self.ModelMovie, width, height)

    def model(self):
        idx = self.Type.currentIndex()
        if idx == self.IDX_IMAGE:
            return self.ModelImage
        elif idx == self.IDX_MOVIE:
            return self.ModelMovie
        else:
            return None

    def selectObjectType(self, type):
        idx = self.Type.findText(type)
        if idx != -1:
            self.Type.setCurrentIndex(idx)
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

    def render(self):
        idx = self.Type.currentIndex()
        if idx == self.IDX_IMAGE:
            self.renderImage()
        elif idx == self.IDX_MOVIE:
            self.renderMovie()

    def renderImage(self):
        output_file = self.args()['file']
        self.WindowResult.write(output_file)
        mb = QtWidgets.QMessageBox.information(
            self,
            "Information",
            "Image saved to '{}'.".format(output_file))

    def renderMovie(self):
        args = self.args()

        if 'location' in args:
            location = args['location']
            cleanup_dir = False
        else:
            location = tempfile.mkdtemp()
            cleanup_dir = True

        if 'frame' in args:
            frame = args['frame']
            if frame.find('*') != -1:
                filename = frame.replace("*", "{:04d}")
            else:
                mb = QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    "The 'frame' parameter needs to contain '*'.")
                return
        else:
            filename = "{}{{:06d}}.png".format(tempfile.gettempprefix())

        chigger_objects = self.getChiggerObjects()
        # FIXME: set times properly
        times = range(100)

        total = len(times)
        progress = QtWidgets.QProgressDialog("", "Abort", 0, total + 1, self)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setLabelText("Rendering frames...")
        for i, t in enumerate(times):
            progress.setValue(i)
            if progress.wasCanceled():
                break

            for obj in chigger_objects:
                obj.update(t)
            self.WindowResult.write("{}/{}".format(location, filename).format(i))

        if not progress.wasCanceled():
            progress.setValue(total)

            progress.setLabelText("Rendering movie...")
            chigger.utils.img2mov(
                '{}/{}'.format(location, frame),
                args['file'],
                duration = float(args['duration']),
                num_threads = 2,
                overwrite = True)
            progress.setValue(total + 1)

        if cleanup_dir:
            for f in os.listdir(location):
                os.remove(os.path.join(location, f))
            os.removedirs(location)

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
                    args[name] = toPython(value)

        return args

    def toText(self):
        idx = self.Type.currentIndex()
        if idx == self.IDX_IMAGE:
            obj_type = 'image'
        elif idx == self.IDX_MOVIE:
            obj_type = 'movie'

        s = ""
        s += "{} = {{\n".format(obj_type)
        for name, value in self.args().items():
            s += argToText(name, value, 1)

        s += "    'viewports': viewports,\n"
        s += "    'colorbars': colorbars,\n"
        s += "    'annotations': annotations\n"
        s += "}\n"
        s += "\n"
        s += "if __name__ == '__main__':\n"
        s += "    otter.render({})\n".format(obj_type)

        return s
