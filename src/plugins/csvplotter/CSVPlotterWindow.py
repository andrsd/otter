import os
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from FilesWidget import FilesWidget
from ChartSetupWidget import ChartSetupWidget
from ChartWidget import ChartWidget

class CSVPlotterWindow(QtWidgets.QWidget):

    def __init__(self, plugin):
        super(CSVPlotterWindow, self).__init__()
        self.plugin = plugin

        self.setAcceptDrops(True)
        self.setWindowTitle("CVS Plotter")

        # The layouts for this widget
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(20)
        self.setLayout(self.main_layout)

        self.left = QtWidgets.QWidget()
        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_layout.setContentsMargins(15, 15, 5, 15)
        self.left.setLayout(self.left_layout)

        self.right = QtWidgets.QWidget()
        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_layout.setContentsMargins(5, 15, 15, 15)
        self.right.setLayout(self.right_layout)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, self)
        self.splitter.setHandleWidth(5)
        self.splitter.setStyleSheet("QSplitter::handle { background-image: none; }")
        self.splitter.addWidget(self.left)
        self.splitter.addWidget(self.right)

        self.splitter.setCollapsible(0, False)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(1, 1)

        self.files_widget = FilesWidget(self)
        self.left_layout.addWidget(self.files_widget)

        self.chart_setup_widget = ChartSetupWidget(self)
        self.left_layout.addWidget(self.chart_setup_widget)

        self.chart_widget = ChartWidget(self)
        self.right_layout.addWidget(self.chart_widget)

        self.main_layout.addWidget(self.splitter)

        self.files_widget.loadFile.connect(self.onLoadFile)
        self.files_widget.loadFile.connect(self.chart_setup_widget.onLoadFile)

        self.chart_setup_widget.chartTitleChanged.connect(self.chart_widget.onChartTitleChanged)
        self.chart_setup_widget.chartLegendVisibilityChanged.connect(self.chart_widget.onChartLegendVisibilityChanged)
        self.chart_setup_widget.chartLegendAlignmentChanged.connect(self.chart_widget.onChartLegendAlignmentChanged)
        self.chart_setup_widget.chartRemoveSeries.connect(self.chart_widget.onChartRemoveSeries)
        self.chart_setup_widget.chartSeriesAdded.connect(self.chart_widget.onChartSeriesAdded)
        self.chart_setup_widget.chartSeriesReset.connect(self.chart_widget.onChartSeriesReset)
        self.chart_setup_widget.chartSeriesUpdate.connect(self.chart_widget.onChartSeriesUpdate)
        self.chart_setup_widget.chartSeriesVisibilityChanged.connect(self.chart_widget.onChartSeriesVisibilityChanged)
        self.chart_setup_widget.chartSeriesNameChanged.connect(self.chart_widget.onChartSeriesNameChanged)
        self.chart_setup_widget.chartSeriesAxisChanged.connect(self.chart_widget.onChartSeriesAxisChanged)
        self.chart_setup_widget.chartSeriesColorChanged.connect(self.chart_widget.onChartSeriesColorChanged)
        self.chart_setup_widget.chartSeriesLineStyleChanged.connect(self.chart_widget.onChartSeriesLineStyleChanged)
        self.chart_setup_widget.chartSeriesLineWidthChanged.connect(self.chart_widget.onChartSeriesLineWidthChanged)
        self.chart_setup_widget.axisLabelChanged.connect(self.chart_widget.onAxisLabelChanged)
        self.chart_setup_widget.axisMajorTicksChanged.connect(self.chart_widget.onAxisMajorTicksChanged)
        self.chart_setup_widget.axisGridLineVisiblityChanged.connect(self.chart_widget.onAxisGridLineVisiblityChanged)
        self.chart_setup_widget.axisLogScaleChanged.connect(self.chart_widget.onAxisLogScaleChanged)
        self.chart_setup_widget.axisMaximumChanged.connect(self.chart_widget.onAxisMaximumChanged)
        self.chart_setup_widget.axisMinimumChanged.connect(self.chart_widget.onAxisMinimumChanged)

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.onUpdateTimer)

    def onLoadFile(self, file_name):
        self.last_updated = os.path.getmtime(file_name)
        self.update_timer.start(1000)

    def onUpdateTimer(self):
        last_updated = os.path.getmtime(self.files_widget.currentFileName())
        if last_updated != self.last_updated:
            self.last_updated = last_updated
            self.chart_setup_widget.updateFile()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()

            file_names = []
            for url in event.mimeData().urls():
                file_names.append(url.toLocalFile())
            self.files_widget.updateFileList(file_names)
        else:
            event.ignore()

    def event(self, e):
        if (e.type() == QtCore.QEvent.WindowActivate):
            self.plugin.updateMenuBar()
        return super(CSVPlotterWindow, self).event(e);
