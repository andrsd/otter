"""
ChartWidget.py
"""

import os
from PyQt5 import QtWidgets, QtCore, QtGui, QtChart


class ChartWidget(QtChart.QChartView):
    """
    Widget for ploting charts
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.chart_corner_roundness = 4
        self.pri_var = ""
        self.series = {}
        self.pen = {}
        self.xmin = None
        self.xmax = None
        self.yaxis = {}
        self.ymin = {}
        self.ymax = {}
        self.axes = {
            'x': QtChart.QValueAxis(),
            'y': QtChart.QValueAxis(),
            'y2': QtChart.QValueAxis()
        }
        self.axis_alignment = {
            'x': QtCore.Qt.AlignBottom,
            'y': QtCore.Qt.AlignLeft,
            'y2': QtCore.Qt.AlignRight
        }
        self.min = {
            'x': None,
            'y': None,
            'y2': None
        }
        self.max = {
            'x': None,
            'y': None,
            'y2': None
        }

        self.setAcceptDrops(True)
        self.setMinimumSize(600, 500)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        self.chart().layout().setContentsMargins(0, 0, 0, 0)
        self.chart().setBackgroundRoundness(self.chart_corner_roundness)

        for n, alignment in self.axis_alignment.items():
            self.chart().addAxis(self.axes[n], alignment)
        self.axes['x'].setVisible(True)
        for n, axis in self.axes.items():
            axis.setGridLineVisible(False)

        self.chart().legend().setVisible(False)

    def dragEnterEvent(self, event):
        """
        Eneter drag event handler
        """

    def dropEvent(self, event):
        """
        Drop event handler
        """

    def onChartRemoveSeries(self):
        """
        Remove series from a chart
        """
        self.chart().removeAllSeries()
        self.series = {}
        self.yaxis = {}
        self.pen = {}
        self.ymin = {}
        self.ymax = {}

    def onChartSeriesAdded(self, pri_var, name, xdata, ydata):
        """
        Add a series to a chart
        """
        self.pri_var = pri_var
        series = QtChart.QLineSeries()
        series.setName(name)
        for x, y in zip(xdata, ydata):
            series.append(x, y)
        self.chart().addSeries(series)
        series.setVisible(False)
        series.attachAxis(self.axes['x'])
        series.attachAxis(self.axes['y'])
        series.hovered.connect(self.onHovered)

        self.series[name] = series
        self.xmin = min(xdata)
        self.xmax = max(xdata)
        self.yaxis[name] = 'left'
        self.ymin[name] = min(ydata)
        self.ymax[name] = max(ydata)
        self.pen[name] = series.pen()

        self.rescaleXAxis()
        self.rescaleYAxes(True)

    def onChartSeriesReset(self, name):
        """
        Series reset
        """
        self.series[name].clear()
        self.ymin[name] = None
        self.ymax[name] = None

    def onChartSeriesUpdate(self, name, xdata, ydata):
        """
        Update series
        """
        series = self.series[name]
        for x, y in zip(xdata, ydata):
            series.append(x, y)
        if self.ymin[name] is None:
            self.ymin[name] = min(ydata)
        else:
            self.ymin[name] = min(self.ymin[name], min(ydata))
        if self.ymax[name] is None:
            self.ymax[name] = max(ydata)
        else:
            self.ymax[name] = max(self.ymax[name], max(ydata))
        self.rescaleYAxes()

    def rescaleXAxis(self):
        """
        rescale X-axis
        """
        self.axes['x'].setRange(self.xmin, self.xmax)
        self.min['x'] = self.xmin
        self.max['x'] = self.xmax

    def rescaleYAxes(self, force=False):
        """
        Rescale Y-axes
        """
        ymin = []
        ymax = []
        y2min = []
        y2max = []

        for name, s in self.series.items():
            if force or s.isVisible():
                if self.yaxis[name] == 'left':
                    ymin.append(self.ymin[name])
                    ymax.append(self.ymax[name])
                else:
                    y2min.append(self.ymin[name])
                    y2max.append(self.ymax[name])

        if len(ymin) > 0 and len(ymax) > 0:
            self.axes['y'].setRange(min(ymin), max(ymax))
            self.min['y'] = ymin
            self.max['y'] = ymax
        if len(y2min) > 0 and len(y2max) > 0:
            self.axes['y2'].setRange(min(y2min), max(y2max))
            self.min['y2'] = y2min
            self.max['y2'] = y2max

    def setAxesVisibility(self):
        """
        Set axes visibility
        """
        yvisible = False
        y2visible = False
        for name, s in self.series.items():
            if s.isVisible():
                if self.yaxis[name] == 'left':
                    yvisible = True
                if self.yaxis[name] == 'right':
                    y2visible = True
        self.axes['y'].setVisible(yvisible)
        self.axes['y2'].setVisible(y2visible)

    def onChartSeriesVisibilityChanged(self, name, visible):
        """
        Series visibility changed
        """
        series = self.series[name]
        series.setVisible(visible)
        self.rescaleYAxes()
        self.setAxesVisibility()

    def onChartSeriesNameChanged(self, name, series_name):
        """
        Series name changed
        """
        series = self.series[name]
        series.setName(series_name)

    def onChartSeriesColorChanged(self, name, color):
        """
        Series color changed
        """
        series = self.series[name]
        self.pen[name].setColor(color)
        series.setPen(self.pen[name])

    def onChartSeriesAxisChanged(self, name, axis):
        """
        Series axis changed
        """
        series = self.series[name]
        if axis == 'left':
            series.detachAxis(self.axes['y2'])
            series.attachAxis(self.axes['y'])
        else:
            series.detachAxis(self.axes['y'])
            series.attachAxis(self.axes['y2'])
        self.yaxis[name] = axis
        self.rescaleYAxes()
        self.setAxesVisibility()

    def onChartSeriesLineStyleChanged(self, name, style):
        """
        Series line style changed
        """
        series = self.series[name]
        pen_style = None
        if style == 'solid':
            pen_style = QtCore.Qt.SolidLine
        elif style == 'dash':
            pen_style = QtCore.Qt.DashLine
        elif style == 'dot':
            pen_style = QtCore.Qt.DotLine
        elif style == 'dash dot':
            pen_style = QtCore.Qt.DashDotLine
        elif style == 'none':
            pen_style = QtCore.Qt.NoPen

        if pen_style is not None:
            self.pen[name].setStyle(pen_style)
            series.setPen(self.pen[name])

    def onChartSeriesLineWidthChanged(self, name, width):
        """
        Series line width changed
        """
        series = self.series[name]
        self.pen[name].setWidth(width)
        series.setPen(self.pen[name])

    def onChartTitleChanged(self, title):
        """
        Title changed
        """
        self.chart().setTitle(title)

    def onChartLegendVisibilityChanged(self, visible):
        """
        Legend visibility changed
        """
        self.chart().legend().setVisible(visible)

    def onChartLegendAlignmentChanged(self, alignment):
        """
        Legend alignment changed
        """
        if alignment == 'left':
            self.chart().legend().setAlignment(QtCore.Qt.AlignLeft)
        elif alignment == 'right':
            self.chart().legend().setAlignment(QtCore.Qt.AlignRight)
        elif alignment == 'top':
            self.chart().legend().setAlignment(QtCore.Qt.AlignTop)
        elif alignment == 'bottom':
            self.chart().legend().setAlignment(QtCore.Qt.AlignBottom)

    def onAxisLabelChanged(self, axis_name, label):
        """
        Axis label changed
        """
        if axis_name in self.axes:
            self.axes[axis_name].setTitleText(label)

    def onAxisMajorTicksChanged(self, axis_name, value):
        """
        Axis major ticks changed
        """
        if axis_name in self.axes:
            self.axes[axis_name].setTickCount(value)

    def onAxisGridLineVisiblityChanged(self, axis_name, visible):
        """
        Axis grid line visibility changed
        """
        if axis_name in self.axes:
            self.axes[axis_name].setGridLineVisible(visible)

    def onAxisLogScaleChanged(self, axis_name, on):
        """
        Axis log slace changed
        """
        if axis_name in self.axes:
            # take the old axis and replace it with the new one
            old_axis = self.axes[axis_name]
            if on:
                new_axis = QtChart.QLogValueAxis()
            else:
                new_axis = QtChart.QValueAxis()

            # copy the values from old_axis into new_axis
            new_axis.setRange(old_axis.min(), old_axis.max())
            new_axis.setVisible(old_axis.isVisible())
            new_axis.setGridLineVisible(old_axis.isGridLineVisible())
            new_axis.setTitleText(old_axis.titleText())
            self.axes[axis_name] = new_axis

            # swap the old axis for the new one in chart and all series
            # attached to old_axis
            self.chart().addAxis(self.axes[axis_name],
                                 self.axis_alignment[axis_name])
            for unused_name, series in self.series.items():
                if old_axis in series.attachedAxes():
                    series.detachAxis(old_axis)
                    series.attachAxis(new_axis)
            self.chart().removeAxis(old_axis)

    def onAxisMaximumChanged(self, axis_name, value):
        """
        Axis maximum value changed
        """
        if axis_name in self.axes:
            if value is None:
                self.axes[axis_name].setMax(self.max[axis_name])
            else:
                self.axes[axis_name].setMax(value)

    def onAxisMinimumChanged(self, axis_name, value):
        """
        Axis minimum value changed
        """
        if axis_name in self.axes:
            if value is None:
                self.axes[axis_name].setMin(self.min[axis_name])
            else:
                self.axes[axis_name].setMin(value)

    def onHovered(self, point, state):
        """
        Triggered when hovered on the series
        """
        series = self.sender()
        if state:
            pos = QtGui.QCursor.pos()
            text = "{}: {:f}\n {}: {:f}".format(
                self.pri_var, point.x(), series.name(), point.y())
            QtWidgets.QToolTip.showText(pos, text)
        else:
            QtWidgets.QToolTip.hideText()

    def exportPdf(self, file_name):
        """
        Export to PDF
        """
        # temporarily disable the roundness, so that plots are rectangular
        self.chart().setBackgroundRoundness(0)

        contents_rect = self.chart().layout().contentsRect()
        screen = QtWidgets.QApplication.screens()[0]
        dpi = screen.logicalDotsPerInch()
        # 25.4 milimeters in 1 inch
        scale = 25.4 / dpi

        writer = QtGui.QPdfWriter(file_name)
        writer.setResolution(600)
        writer.setPageSizeMM(
            QtCore.QSizeF(scale * contents_rect.width(),
                          scale * contents_rect.height()))
        painter = QtGui.QPainter(writer)
        self.render(painter)
        painter.end()

        self.chart().setBackgroundRoundness(self.chart_corner_roundness)

    def exportPng(self, file_name):
        """
        Export to PNG
        """
        # temporarily disable the roundness, so that plots are rectangular
        self.chart().setBackgroundRoundness(0)

        painter = self.grab(self.chart().layout().contentsRect().toRect())
        painter.save(file_name, "PNG")

        self.chart().setBackgroundRoundness(self.chart_corner_roundness)

    def exportGnuplot(self, file_name, csv_file_name):
        """
        Export to gnuplot
        """
        # build a map from variable name to its index
        hdrs = {}
        line = ""
        with open(csv_file_name, "r") as f:
            line = f.readline()
        variables = line.split(",")
        for i, v in enumerate(variables):
            n = v.strip().strip('"').strip("'")
            hdrs[n] = i + 1

        with open(file_name, "w") as f:
            f.write("set terminal svg\n")
            f.write("set output \"{}.svg\"\n".format(
                os.path.basename(file_name)))
            f.write("\n")
            if len(self.chart().title()) > 0:
                f.write("set title '{}'\n".format(self.chart().title()))

            for a in ['x', 'y', 'y2']:
                if a in self.axes and self.axes[a].isVisible():
                    axis = self.axes[a]
                    f.write("set {}label '{}'\n".format(a, axis.titleText()))
                    f.write("set {}range [{}:{}]\n".format(
                        a, axis.min(), axis.max()))
                    incr = (axis.max() - axis.min()) / (axis.tickCount() - 1)
                    f.write("set {}tics {},{},{}\n".format(
                        a, axis.min(), incr, axis.max()))
                    if axis.isGridLineVisible():
                        f.write("set grid {}tics\n".format(a))
                    else:
                        f.write("set grid no{}tics\n".format(a))
                    f.write("\n")

            f.write("set datafile separator ','\n")
            f.write("\n")

            if self.chart().legend().isVisible():
                f.write("set key on\n")
            else:
                f.write("set key off\n")
            f.write("\n")

            if len(self.series.keys()) > 0:
                f.write("plot\\\n")
                lines = []
                pri_var_idx = hdrs[self.pri_var]
                for (name, series) in self.series.items():
                    if series.isVisible():
                        var_idx = hdrs[name]

                        pen = self.pen[name]
                        rgb = pen.color().name(QtGui.QColor.HexRgb)
                        if pen.style() == QtCore.Qt.SolidLine:
                            dashtype = '1'
                        elif pen.style() == QtCore.Qt.DashLine:
                            dashtype = '2'
                        elif pen.style() == QtCore.Qt.DotLine:
                            dashtype = '3'
                        elif pen.style() == QtCore.Qt.DashDotLine:
                            dashtype = '4'
                        else:
                            dashtype = '1'

                        ln = ""
                        ln += " '{}'".format(os.path.basename(csv_file_name))
                        ln += " using {}:{}".format(pri_var_idx, var_idx)
                        ln += " title '{}'".format(name)
                        ln += " with lines"
                        ln += " dt {}".format(dashtype)
                        ln += " lc rgb \"{}\"".format(rgb)
                        ln += " lw {}".format(pen.width())

                        lines.append(ln)

                f.write(',\\\n'.join(lines))
