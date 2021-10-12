"""
CSVPlotterPlugin.py
"""

from PyQt5 import QtCore, QtWidgets
from Plugin import Plugin
from otter.assets import Assets
from .CSVPlotterWindow import CSVPlotterWindow


class CSVPlotterPlugin(Plugin):
    """
    Plug-in for CVS plotting
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.window = None
        file_menu = self.getMenu("File")
        self.addMenuSeparator(file_menu)
        self._export_menu = self.addMenu(file_menu, "Export")
        self._export_png = self.addMenuAction(
            self._export_menu, "PNG...", self.onExportPng)
        self._export_pdf = self.addMenuAction(
            self._export_menu, "PDF...", self.onExportPdf)
        self._export_gnuplot = self.addMenuAction(
            self._export_menu, "gnuplot...", self.onExportGnuplot)

    @staticmethod
    def name():
        """
        Name of the plug-in
        """
        return "CSV Plotter"

    @staticmethod
    def icon():
        """
        Icon of the plug-in
        """
        return Assets().icons['graph']

    def onCreate(self):
        """
        Create handler
        """
        self.window = CSVPlotterWindow(self)
        self.registerWindow(self.window)

        settings = QtCore.QSettings()
        settings.beginGroup(self.name())
        geom = settings.value("wnd_geometry")
        if geom is None:
            self.window.resize(700, 900)
            qapp = QtWidgets.QApplication.instance()
            self.window.setGeometry(
                QtWidgets.QStyle.alignedRect(
                    QtCore.Qt.LeftToRight,
                    QtCore.Qt.AlignCenter,
                    self.window.size(),
                    qapp.desktop().screenGeometry()
                )
            )
        else:
            self.window.restoreGeometry(geom)
        settings.endGroup()

    def onClose(self):
        settings = QtCore.QSettings()
        settings.beginGroup(self.name())
        settings.setValue("wnd_geometry", self.window.saveGeometry())
        settings.endGroup()

    def onExportPdf(self):
        """
        Export PDF handler
        """
        self.window.onExport("pdf")

    def onExportPng(self):
        """
        Export PNG handler
        """
        self.window.onExport("png")

    def onExportGnuplot(self):
        """
        Export gnuplot handler
        """
        self.window.onExport("gnuplot")
