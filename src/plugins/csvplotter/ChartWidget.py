from PyQt5 import QtWidgets, QtCore, QtGui, QtChart

class ChartWidget(QtChart.QChartView):

    def __init__(self, parent):
        super(ChartWidget, self).__init__(parent)

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
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.chart().layout().setContentsMargins(0, 0, 0, 0)
        self.chart().setBackgroundRoundness(self.chart_corner_roundness)

        for n, alignment in self.axis_alignment.items():
            self.chart().addAxis(self.axes[n], alignment)
        self.axes['x'].setVisible(True)
        for n, axis in self.axes.items():
            axis.setGridLineVisible(False)

        self.chart().legend().setVisible(False)

    def dragEnterEvent(self, event):
        pass

    def dropEvent(self, event):
        pass

    def onChartRemoveSeries(self):
        self.chart().removeAllSeries()
        self.series = {}
        self.yaxis = {}
        self.pen = {}
        self.ymin = {}
        self.ymax = {}

    def onChartSeriesAdded(self, pri_var, name, xdata, ydata):
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
        series = self.series[name].clear()
        self.ymin[name] = None
        self.ymax[name] = None

    def onChartSeriesUpdate(self, name, xdata, ydata):
        series = self.series[name]
        for x, y in zip(xdata, ydata):
            series.append(x, y)
        if self.ymin[name] == None:
            self.ymin[name] = min(ydata)
        else:
            self.ymin[name] = min(self.ymin[name], min(ydata))
        if self.ymax[name] == None:
            self.ymax[name] = max(ydata)
        else:
            self.ymax[name] = max(self.ymax[name], max(ydata))
        self.rescaleYAxes()

    def rescaleXAxis(self):
        self.axes['x'].setRange(self.xmin, self.xmax)
        self.min['x'] = self.xmin
        self.max['x'] = self.xmax

    def rescaleYAxes(self, force = False):
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
        series = self.series[name]
        series.setVisible(visible)
        self.rescaleYAxes()
        self.setAxesVisibility()

    def onChartSeriesNameChanged(self, name, series_name):
        series = self.series[name]
        series.setName(series_name)

    def onChartSeriesColorChanged(self, name, color):
        series = self.series[name]
        self.pen[name].setColor(color)
        series.setPen(self.pen[name])

    def onChartSeriesAxisChanged(self, name, axis):
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

        if pen_style != None:
            self.pen[name].setStyle(pen_style)
            series.setPen(self.pen[name])

    def onChartSeriesLineWidthChanged(self, name, width):
        series = self.series[name]
        self.pen[name].setWidth(width)
        series.setPen(self.pen[name])

    def onChartTitleChanged(self, title):
        self.chart().setTitle(title)

    def onChartLegendVisibilityChanged(self, visible):
        self.chart().legend().setVisible(visible)

    def onChartLegendAlignmentChanged(self, alignment):
        if alignment == 'left':
            self.chart().legend().setAlignment(QtCore.Qt.AlignLeft)
        elif alignment == 'right':
            self.chart().legend().setAlignment(QtCore.Qt.AlignRight)
        elif alignment == 'top':
            self.chart().legend().setAlignment(QtCore.Qt.AlignTop)
        elif alignment == 'bottom':
            self.chart().legend().setAlignment(QtCore.Qt.AlignBottom)

    def onAxisLabelChanged(self, axis_name, label):
        if axis_name in self.axes:
            self.axes[axis_name].setTitleText(label)

    def onAxisMajorTicksChanged(self, axis_name, value):
        if axis_name in self.axes:
            self.axes[axis_name].setTickCount(value)

    def onAxisGridLineVisiblityChanged(self, axis_name, visible):
        if axis_name in self.axes:
            self.axes[axis_name].setGridLineVisible(visible)

    def onAxisLogScaleChanged(self, axis_name, on):
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

            # swap the old axis for the new one in chart and all series attached to old_axis
            self.chart().addAxis(self.axes[axis_name], self.axis_alignment[axis_name])
            for name, series in self.series.items():
                if old_axis in series.attachedAxes():
                    series.detachAxis(old_axis)
                    series.attachAxis(new_axis)
            self.chart().removeAxis(old_axis)

    def onAxisMaximumChanged(self, axis_name, value):
        if axis_name in self.axes:
            if value == None:
                self.axes[axis_name].setMax(self.max[axis_name])
            else:
                self.axes[axis_name].setMax(value)

    def onAxisMinimumChanged(self, axis_name, value):
        if axis_name in self.axes:
            if value == None:
                self.axes[axis_name].setMin(self.min[axis_name])
            else:
                self.axes[axis_name].setMin(value)

    def onHovered(self, point, state):
        series = self.sender()
        if state:
            pos = QtGui.QCursor.pos()
            text = "{}: {:f}\n {}: {:f}".format(self.pri_var, point.x(), series.name(), point.y())
            QtWidgets.QToolTip.showText(pos, text)
        else:
            QtWidgets.QToolTip.hideText()

    def exportPdf(self, file_name):
        # temporarily disable the roundness, so that plots are rectangular
        self.chart().setBackgroundRoundness(0)

        contents_rect = self.chart().layout().contentsRect()
        screen = QtWidgets.QApplication.screens()[0]
        dpi = screen.logicalDotsPerInch()
        # 25.4 milimeters in 1 inch
        scale = 25.4 / dpi

        writer = QtGui.QPdfWriter(file_name)
        writer.setResolution(600)
        writer.setPageSizeMM(QtCore.QSizeF(scale * contents_rect.width(), scale * contents_rect.height()))
        painter = QtGui.QPainter(writer)
        self.render(painter)
        painter.end()

        self.chart().setBackgroundRoundness(self.chart_corner_roundness)

    def exportPng(self, file_name):
        # temporarily disable the roundness, so that plots are rectangular
        self.chart().setBackgroundRoundness(0)

        p = self.grab(self.chart().layout().contentsRect().toRect())
        p.save(file_name, "PNG")

        self.chart().setBackgroundRoundness(self.chart_corner_roundness)
