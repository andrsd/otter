"""
CSVPlotterWindow.py
"""

import os
from PyQt5 import QtWidgets, QtCore
from otter.plugins.PluginWindowBase import PluginWindowBase
from otter.plugins.csvplotter.FilesWidget import FilesWidget
from otter.plugins.csvplotter.ChartSetupWidget import ChartSetupWidget
from otter.plugins.csvplotter.ChartWidget import ChartWidget


class CSVPlotterWindow(PluginWindowBase):
    """
    Main window of the CSV plotter plug-in
    """

    def __init__(self, plugin):
        super().__init__(plugin)
        self.last_updated = None

        self.setAcceptDrops(True)
        self.setWindowTitle("CVS Plotter")

        self.setupWidgets()
        self.setupMenuBar()

        self.files_widget.loadFile.connect(self.onLoadFile)
        self.files_widget.loadFile.connect(self.chart_setup_widget.onLoadFile)

        self.chart_setup_widget.chartTitleChanged.connect(
            self.chart_widget.onChartTitleChanged)
        self.chart_setup_widget.chartLegendVisibilityChanged.connect(
            self.chart_widget.onChartLegendVisibilityChanged)
        self.chart_setup_widget.chartLegendAlignmentChanged.connect(
            self.chart_widget.onChartLegendAlignmentChanged)
        self.chart_setup_widget.chartRemoveSeries.connect(
            self.chart_widget.onChartRemoveSeries)
        self.chart_setup_widget.chartSeriesAdded.connect(
            self.chart_widget.onChartSeriesAdded)
        self.chart_setup_widget.chartSeriesReset.connect(
            self.chart_widget.onChartSeriesReset)
        self.chart_setup_widget.chartSeriesUpdate.connect(
            self.chart_widget.onChartSeriesUpdate)
        self.chart_setup_widget.chartSeriesVisibilityChanged.connect(
            self.chart_widget.onChartSeriesVisibilityChanged)
        self.chart_setup_widget.chartSeriesNameChanged.connect(
            self.chart_widget.onChartSeriesNameChanged)
        self.chart_setup_widget.chartSeriesAxisChanged.connect(
            self.chart_widget.onChartSeriesAxisChanged)
        self.chart_setup_widget.chartSeriesColorChanged.connect(
            self.chart_widget.onChartSeriesColorChanged)
        self.chart_setup_widget.chartSeriesLineStyleChanged.connect(
            self.chart_widget.onChartSeriesLineStyleChanged)
        self.chart_setup_widget.chartSeriesLineWidthChanged.connect(
            self.chart_widget.onChartSeriesLineWidthChanged)
        self.chart_setup_widget.axisLabelChanged.connect(
            self.chart_widget.onAxisLabelChanged)
        self.chart_setup_widget.axisMajorTicksChanged.connect(
            self.chart_widget.onAxisMajorTicksChanged)
        self.chart_setup_widget.axisGridLineVisiblityChanged.connect(
            self.chart_widget.onAxisGridLineVisiblityChanged)
        self.chart_setup_widget.axisLogScaleChanged.connect(
            self.chart_widget.onAxisLogScaleChanged)
        self.chart_setup_widget.axisMaximumChanged.connect(
            self.chart_widget.onAxisMaximumChanged)
        self.chart_setup_widget.axisMinimumChanged.connect(
            self.chart_widget.onAxisMinimumChanged)

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.onUpdateTimer)

    def setupWidgets(self):
        self.setContentsMargins(0, 0, 0, 0)

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
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-image: none;
            }""")
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

        self.setCentralWidget(self.splitter)

    def setupMenuBar(self):
        file_menu = self._menubar.addMenu("File")
        self._export_menu = file_menu.addMenu("Export")
        self._export_png = self._export_menu.addAction(
            "PNG...", self.onExportPng)
        self._export_pdf = self._export_menu.addAction(
            "PDF...", self.onExportPdf)
        self._export_gnuplot = self._export_menu.addAction(
            "gnuplot...", self.onExportGnuplot)
        file_menu.addSeparator()
        self._close_action = file_menu.addAction(
            "Close", self.onClose, "Ctrl+W")

    def onLoadFile(self, file_name):
        """
        Load file handler
        @param file_name[str] Name of the file
        """
        self.last_updated = os.path.getmtime(file_name)
        self.update_timer.start(1000)

    def onUpdateTimer(self):
        """
        Update timer handler
        """
        last_updated = os.path.getmtime(self.files_widget.currentFileName())
        if last_updated != self.last_updated:
            self.last_updated = last_updated
            self.chart_setup_widget.updateFile()

    def onExportPdf(self):
        self.onExport("pdf")

    def onExportPng(self):
        self.onExport("png")

    def onExportGnuplot(self):
        self.onExport("gnuplot")

    def onExport(self, file_format):
        """
        Export file handler
        """
        if file_format == 'pdf':
            file_name = self.exportFileDialog('Export to PDF',
                                              'PDF files (*.pdf)',
                                              'pdf')
            if file_name:
                self.chart_widget.exportPdf(file_name)

        elif file_format == 'png':
            file_name = self.exportFileDialog('Export to PNG',
                                              'PNG files (*.png)',
                                              'png')
            if file_name:
                self.chart_widget.exportPng(file_name)

        elif file_format == 'gnuplot':
            file_name = self.exportFileDialog(
                'Export to gnuplot',
                'gnuplot files (*.plt, *.gnu, *.gpi, *.gih)',
                'plt')
            if file_name:
                csv_file_name = self.files_widget.currentFileName()
                self.chart_widget.exportGnuplot(file_name, csv_file_name)

        else:
            return

    def exportFileDialog(self, window_title, name_filter, default_suffix):
        """
        Show file export dialog
        """
        dialog = QtWidgets.QFileDialog()
        dialog.setWindowTitle(window_title)
        dialog.setNameFilter(name_filter)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setDefaultSuffix(default_suffix)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            return str(dialog.selectedFiles()[0])
        return None

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
            self.files_widget.updateFileList(file_names)
        else:
            event.ignore()
