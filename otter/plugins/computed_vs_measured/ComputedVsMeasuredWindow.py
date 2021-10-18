"""
ComputedVsMeasuredWindow.py
"""

import os
import csv
from PyQt5 import QtWidgets, QtCore, QtChart, QtGui


class ComputedVsMeasuredWindow(QtWidgets.QMainWindow):
    """
    Main window of the computed vs measured data plug-in
    """

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.last_updated = None

        self._icon_size = QtCore.QSize(32, 32)
        self.chart_corner_roundness = 4

        self.abs_err = 0.1
        self.rel_err = 10

        self.smin = 0
        self.smax = 1
        self.s = []

        self.setupWidgets()

        # connect signals
        self.relative_error.toggled.connect(self.onRelativeError)
        self.relative_error_amount.textChanged.connect(
            self.onRelativeErrorAmountChanged)
        self.absolute_error.toggled.connect(self.onAbsoluteError)
        self.absolute_error_amount.textChanged.connect(
            self.onAbsoluteErrorAmountChanged)
        self.file_list.itemChanged.connect(self.onFileListItemChanged)
        self.add_button.clicked.connect(self.onAddFiles)

        self.relative_error.setChecked(True)
        self.updateControls()

        self.setAcceptDrops(True)
        self.setWindowTitle("Computed vs. Measured")

        geom = self.plugin.settings.value("window/geometry")
        default_size = QtCore.QSize(1000, 700)
        if geom is None:
            self.resize(default_size)
        else:
            if not self.restoreGeometry(geom):
                self.resize(default_size)

    def setupWidgets(self):
        self.setContentsMargins(8, 8, 0, 8)

        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_layout.setSpacing(10)
        self.left_layout.setContentsMargins(0, 0, 0, 0)

        self.chart_view = QtChart.QChartView()
        self.chart_view.setMinimumSize(600, 500)
        self.chart_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Expanding)
        chart = self.chart_view.chart()
        chart.legend().setVisible(False)
        chart.layout().setContentsMargins(3, 3, 3, 3)
        chart.setBackgroundRoundness(self.chart_corner_roundness)

        self.ideal_series = QtChart.QLineSeries()
        self.ideal_series.append(0, 0)
        self.ideal_series.append(1, 1)
        self.ideal_series.setOpacity(0.1)
        self.ideal_series.setPen(QtGui.QPen(QtCore.Qt.black))
        self.chart_view.chart().addSeries(self.ideal_series)

        self.lower_bound_series = QtChart.QLineSeries()
        self.lower_bound_series.append(0, 0)
        self.lower_bound_series.append(1, 0.9)
        self.lower_bound_series.setOpacity(0.1)
        self.lower_bound_series.setPen(QtGui.QPen(QtCore.Qt.black))
        self.chart_view.chart().addSeries(self.lower_bound_series)

        self.upper_bound_series = QtChart.QLineSeries()
        self.upper_bound_series.append(0, 0)
        self.upper_bound_series.append(0.9, 1)
        self.upper_bound_series.setOpacity(0.1)
        self.upper_bound_series.setPen(QtGui.QPen(QtCore.Qt.black))
        self.chart_view.chart().addSeries(self.upper_bound_series)

        self.chart_view.chart().createDefaultAxes()
        self.axis_x = self.chart_view.chart().axes(QtCore.Qt.Horizontal)[0]
        self.axis_x.setTitleText("Measured")
        self.axis_y = self.chart_view.chart().axes(QtCore.Qt.Vertical)[0]
        self.axis_y.setTitleText("Computed")

        self.left_layout.addWidget(self.chart_view)

        self.left_layout_bottom = QtWidgets.QHBoxLayout()

        self.error_type = QtWidgets.QGroupBox()
        self.error_type.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                      QtWidgets.QSizePolicy.Fixed)
        self.error_type.setContentsMargins(0, 0, 0, 0)

        error_type_layout = QtWidgets.QGridLayout()
        error_type_layout.setSpacing(6)
        self.relative_error = QtWidgets.QRadioButton("Relative")
        error_type_layout.addWidget(self.relative_error, 0, 0)

        self.relative_error_amount = QtWidgets.QLineEdit(
            "{}".format(self.rel_err))
        validator = QtGui.QDoubleValidator()
        self.relative_error_amount.setValidator(validator)
        error_type_layout.addWidget(self.relative_error_amount, 0, 1)

        self.relative_error_label = QtWidgets.QLabel("%")
        error_type_layout.addWidget(self.relative_error_label, 0, 2)

        self.absolute_error = QtWidgets.QRadioButton("Absolute")
        error_type_layout.addWidget(self.absolute_error, 1, 0)

        self.absolute_error_amount = QtWidgets.QLineEdit(
            "{}".format(self.abs_err))
        validator = QtGui.QDoubleValidator()
        self.absolute_error_amount.setValidator(validator)
        error_type_layout.addWidget(self.absolute_error_amount, 1, 1)

        self.error_type.setLayout(error_type_layout)

        self.left_layout_bottom.addWidget(self.error_type)

        self.left_layout_bottom.addStretch()

        self.left_layout.addLayout(self.left_layout_bottom)

        self.left_pane = QtWidgets.QWidget()
        self.left_pane.setLayout(self.left_layout)
        self.left_pane.setContentsMargins(0, 0, 4, 0)

        # right side
        self.layout_right = QtWidgets.QVBoxLayout()
        self.layout_right.setContentsMargins(0, 0, 0, 0)

        self.file_list = QtGui.QStandardItemModel(0, 2, self)
        self.file_list.setHorizontalHeaderLabels(["File", ""])

        self.file_view = QtWidgets.QTreeView(self)
        self.file_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                     QtWidgets.QSizePolicy.Expanding)
        self.file_view.setMinimumWidth(255)
        self.file_view.setRootIsDecorated(False)
        self.file_view.setModel(self.file_list)
        self.file_view.setContentsMargins(0, 0, 0, 0)
        self.file_view.header().resizeSection(0, 230)
        self.file_view.header().resizeSection(1, 10)
        self.layout_right.addWidget(self.file_view)

        self.add_button = QtWidgets.QPushButton("+", self)
        self.add_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                      QtWidgets.QSizePolicy.Fixed)
        self.layout_right.addWidget(self.add_button)

        self.right_pane = QtWidgets.QWidget()
        self.right_pane.setLayout(self.layout_right)
        self.right_pane.setContentsMargins(0, 4, 4, 0)

        self.vsplitter = QtWidgets.QSplitter()
        self.vsplitter.setStyleSheet("""
            QSplitter::handle {
                background-image: none;
            }""")
        self.vsplitter.setHandleWidth(2)
        self.vsplitter.addWidget(self.left_pane)
        self.vsplitter.addWidget(self.right_pane)
        self.vsplitter.setCollapsible(0, False)

        self.setCentralWidget(self.vsplitter)

    def setupMenuBar(self):
        self._menubar = QtWidgets.QMenuBar()
        self.setMenuBar(self._menubar)

    @property
    def menubar(self):
        return self._menubar

    def updateControls(self):
        """
        Update the GUI controls
        """
        checked = self.relative_error.isChecked()
        self.relative_error_amount.setEnabled(checked)
        self.relative_error_label.setEnabled(checked)

        checked = self.absolute_error.isChecked()
        self.absolute_error_amount.setEnabled(checked)

    def updateBounds(self):
        """
        Update graph bounds
        """
        self.ideal_series.replace(0, self.smin, self.smin)
        self.ideal_series.replace(1, self.smax, self.smax)

        if self.relative_error.isChecked():
            self.lower_bound_series.replace(
                0, self.smin, self.smin * (1 - (self.rel_err / 100.)))
            self.lower_bound_series.replace(
                1, self.smax, self.smax * (1 - (self.rel_err / 100.)))

            self.upper_bound_series.replace(
                0, self.smin, self.smin * (1 + (self.rel_err / 100.)))
            self.upper_bound_series.replace(
                1, self.smax, self.smax * (1 + (self.rel_err / 100.)))
        elif self.absolute_error.isChecked():
            self.lower_bound_series.replace(
                0, self.smin, self.smin - self.abs_err)
            self.lower_bound_series.replace(
                1, self.smax, self.smax - self.abs_err)

            self.upper_bound_series.replace(
                0, self.smin, self.smin + self.abs_err)
            self.upper_bound_series.replace(
                1, self.smax, self.smax + self.abs_err)

    def onRelativeError(self):
        """
        Callback when relative error is selected
        """
        self.updateBounds()
        self.updateControls()

    def onRelativeErrorAmountChanged(self, text):
        """
        Callback when relative error is changed
        """
        try:
            self.rel_err = float(text)
            self.updateBounds()
        except ValueError:
            pass

    def onAbsoluteError(self):
        """
        Callback when absolute error is selected
        """
        self.updateBounds()
        self.updateControls()

    def onAbsoluteErrorAmountChanged(self, text):
        """
        Callback when absolute error is changed
        """
        try:
            self.abs_err = float(text)
            self.updateBounds()
        except ValueError:
            pass

    def buildFileList(self, file_names):
        """
        Take a list of file names and build a list of file name pairs with
        computed and measured data. We assume that 'gold' in file name refers
        to measured data. The lack of 'gold' refers to computed.

        @param file_names[list]: The list of file names
        @return list of pairs [measured, computed]
        """
        measured = []
        computed = []
        for file in file_names:
            if 'gold' in file:
                measured.append(file)
            else:
                computed.append(file)

        measured.sort()
        computed.sort()

        flist = []
        for m, c in zip(measured, computed):
            flist.append([m, c])

        return flist

    def readFile(self, file_name):
        """
        Read a CSV file and return its data as a dictionary

        @param file_name[str]: The name of the file to read
        @return [dict] with the data
        """
        d = None
        with open(file_name, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            d = next(reader)

        data = {}
        for k, v in d.items():
            data[k] = float(v)
        return data

    def dataCompatible(self, data1, data2):
        """
        Are data we want to plot compatible? That means:
        - do they have the same number of entries
        - do they contains the same dictionary keys

        @param data1[dict]: Data to plot
        @param data2[dict]: Data to plot
        @return True if 'data1' and 'data2' are compatible, False otherwise
        """
        if len(data1) == len(data2):
            pairs = zip(data1, data2)
            return not any(x != y for x, y in pairs)

        return False

    def buildItem(self, file_name):
        """
        Build a QStandardItem for the file list widget

        @param file_name[str]: The file name used in the widget
        """
        item = QtGui.QStandardItem(os.path.basename(file_name))
        item.setToolTip(file_name)
        item.setData(file_name)
        item.setEditable(False)
        return item

    def addFiles(self, files):
        """
        Add 'files' into the file list widget

        @param files[list]: The list of files to add into the plugin for
            plotting
        """
        for f in files:
            measured_data = self.readFile(f[0])
            computed_data = self.readFile(f[1])

            del measured_data['time']
            del computed_data['time']

            if self.dataCompatible(measured_data, computed_data):
                series = QtChart.QScatterSeries()
                series.setMarkerSize(10)
                for k, v in measured_data.items():
                    series.append(v, computed_data[k])

                series.hovered.connect(self.onHovered)
                self.chart_view.chart().addSeries(series)
                series.attachAxis(self.axis_x)
                series.attachAxis(self.axis_y)

                # to prevent the garbagge collector to destroy the series
                # object so we can use it later
                self.s.append(series)

                # rescale the axis
                smin = min(min(measured_data.values()),
                           min(computed_data.values()))
                if len(self.s) == 1:
                    self.smin = smin
                else:
                    self.smin = min(self.smin, smin)

                smax = max(max(measured_data.values()),
                           max(computed_data.values()))
                if len(self.s) == 1:
                    self.smax = smax
                else:
                    self.smax = max(self.smax, smax)

                self.axis_x.setRange(self.smin, self.smax)
                self.axis_y.setRange(self.smin, self.smax)

                # add into file list
                item1 = self.buildItem(f[0])
                item1.setCheckable(True)
                item1.setCheckState(QtCore.Qt.Checked)

                item2 = QtGui.QStandardItem("\u25A0")
                item2.setEditable(False)
                item2.setForeground(series.brush())
                item2.setData(series)

                self.file_list.appendRow([item1, item2])

    def onAddFiles(self):
        """
        Called when adding files
        """
        file_names, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Select one or more files to open")
        if len(file_names) > 0:
            files = self.buildFileList(file_names)
            self.addFiles(files)
            self.updateBounds()

    def onFileListItemChanged(self, item):
        """
        Called when item in the file list changes
        """
        if item.column() == 0:
            model = item.model()
            series_item = model.item(item.row(), 1)
            if series_item is not None:
                series = series_item.data()
                checked = item.checkState() == QtCore.Qt.Checked
                series.setVisible(checked)

    def onHovered(self, point, state):
        """
        Callback when cursor hover on a data point

        @param point[QPointF]: Point where the cursor hovered
        """
        if state:
            QtWidgets.QToolTip.showText(
                QtGui.QCursor.pos(),
                "{}, {}".format(point.x(), point.y()),
                self.chart_view)
        else:
            QtWidgets.QToolTip.hideText()

    def dragEnterEvent(self, event):
        """
        Enter drag event
        """
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Drop event
        """
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()

            file_names = []
            for url in event.mimeData().urls():
                file_names.append(url.toLocalFile())

            files = self.buildFileList(file_names)
            self.addFiles(files)
            self.updateBounds()
        else:
            event.ignore()

    def event(self, event):
        """
        Event handler
        """
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

    def closeEvent(self, event):
        self.plugin.settings.setValue("window/geometry", self.saveGeometry())
        event.accept()
