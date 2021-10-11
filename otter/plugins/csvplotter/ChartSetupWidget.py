"""
ChartSetupWidget.py
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from .PostprocessorReader import PostprocessorReader


class VariablesParamDelegate(QtWidgets.QStyledItemDelegate):
    """
    Delegate for variable parameter
    """

    def createEditor(self, parent, option, index):
        col = index.column()
        if col == ChartSetupWidget.IDX_AXIS:
            editor = QtWidgets.QComboBox(parent)
            editor.addItem('right')
            editor.addItem('left')
            return editor
        elif col == ChartSetupWidget.IDX_COLOR:
            editor = QtWidgets.QColorDialog(parent)
            return editor
        elif col == ChartSetupWidget.IDX_LINE_STYLE:
            editor = QtWidgets.QComboBox(parent)
            editor.addItem('solid')
            editor.addItem('dash')
            editor.addItem('dot')
            editor.addItem('dash dot')
            editor.addItem('none')
            return editor
        elif col == ChartSetupWidget.IDX_LINE_WIDTH:
            editor = QtWidgets.QSpinBox(parent)
            editor.setRange(1, 10)
            editor.setSingleStep(1)
            return editor
        else:
            return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        model = index.model()
        if index.column() in [ChartSetupWidget.IDX_AXIS,
                              ChartSetupWidget.IDX_LINE_STYLE]:
            value = model.data(index, QtCore.Qt.EditRole)
            editor.setCurrentIndex(editor.findText(value))
        elif index.column() == ChartSetupWidget.IDX_COLOR:
            item = model.itemFromIndex(index)
            editor.setCurrentColor(item.foreground().color())
        elif index.column() == ChartSetupWidget.IDX_LINE_WIDTH:
            value = model.data(index, QtCore.Qt.EditRole)
            editor.setValue(int(value))
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index.column() in [ChartSetupWidget.IDX_AXIS,
                              ChartSetupWidget.IDX_LINE_STYLE]:
            value = editor.currentText()
            model.setData(index, value, QtCore.Qt.EditRole)
        elif index.column() == ChartSetupWidget.IDX_COLOR:
            if editor.result() == QtWidgets.QDialog.Accepted:
                color = editor.selectedColor()
                item = model.itemFromIndex(index)
                item.setForeground(QtGui.QBrush(color))
        elif index.column() == ChartSetupWidget.IDX_LINE_WIDTH:
            value = editor.value()
            model.setData(index, str(value), QtCore.Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        if index.column() in [ChartSetupWidget.IDX_AXIS,
                              ChartSetupWidget.IDX_LINE_STYLE]:
            rect = option.rect
            rect.setTop(rect.top() - 2)
            rect.setBottom(rect.bottom() + 3)
            editor.setGeometry(rect)
        else:
            super().updateEditorGeometry(editor, option, index)


class AxisTab(QtWidgets.QWidget):
    """
    Tab widget for axis
    """

    def __init__(self, parent, axis_name):
        super().__init__()
        self.parent = parent
        self.axis_name = axis_name

        self.update_maximum_timer = QtCore.QTimer()
        self.update_maximum_timer.setSingleShot(True)
        self.update_minimum_timer = QtCore.QTimer()
        self.update_minimum_timer.setSingleShot(True)

        self.layout_main = QtWidgets.QFormLayout()
        self.layout_main.setContentsMargins(10, 10, 10, 5)
        self.layout_main.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.layout_main.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.ExpandingFieldsGrow)

        self.label = QtWidgets.QLineEdit("")
        self.layout_main.addRow("Label", self.label)

        self.maximum = QtWidgets.QLineEdit("")
        self.maximum.setValidator(QtGui.QDoubleValidator())
        self.layout_main.addRow("Maximum", self.maximum)

        self.minimum = QtWidgets.QLineEdit("")
        self.minimum.setValidator(QtGui.QDoubleValidator())
        self.layout_main.addRow("Minimum", self.minimum)

        self.major_ticks = QtWidgets.QSpinBox()
        self.major_ticks.setMinimum(2)
        self.major_ticks.setValue(5)
        self.layout_main.addRow("Major ticks", self.major_ticks)

        self.bottom_layout = QtWidgets.QHBoxLayout()

        self.grid = QtWidgets.QCheckBox("Grid")
        self.bottom_layout.addWidget(self.grid)

        self.log_scale = QtWidgets.QCheckBox("Log scale")
        self.bottom_layout.addWidget(self.log_scale)

        self.layout_main.addRow(self.bottom_layout)

        self.setLayout(self.layout_main)

        self.label.textChanged.connect(self.onLabelChanged)
        self.major_ticks.valueChanged.connect(self.onMajorTicksValueChanged)
        self.grid.stateChanged.connect(self.onGridChanged)
        self.log_scale.stateChanged.connect(self.onLogScaleChanged)
        self.maximum.textChanged.connect(self.onMaximumChanged)
        self.maximum.editingFinished.connect(self.onMaximumEditingFinished)
        self.update_maximum_timer.timeout.connect(self.onUpdateMaximumTimer)
        self.minimum.textChanged.connect(self.onMinimumChanged)
        self.minimum.editingFinished.connect(self.onMinimumEditingFinished)
        self.update_minimum_timer.timeout.connect(self.onUpdateMinimumTimer)

    def onLabelChanged(self, text):
        """
        Label changed handler
        """
        self.parent.axisLabelChanged.emit(self.axis_name, text)

    def onMajorTicksValueChanged(self, value):
        """
        Major ticks value handler
        """
        self.parent.axisMajorTicksChanged.emit(self.axis_name, value)

    def onGridChanged(self, state):
        """
        Grid changed handler
        """
        self.parent.axisGridLineVisiblityChanged.emit(
            self.axis_name, state == QtCore.Qt.Checked)

    def onLogScaleChanged(self, state):
        """
        Log scale changed handler
        """
        self.parent.axisLogScaleChanged.emit(
            self.axis_name, state == QtCore.Qt.Checked)

    def onMaximumChanged(self, unused_text):
        """
        Maximum value changed handler
        """
        self.update_maximum_timer.start(1000)

    def emitMaximumChanged(self, text):
        """
        Emit 'maximum value changed' signal
        """
        if len(text) > 0:
            self.parent.axisMaximumChanged.emit(self.axis_name, float(text))
        else:
            self.parent.axisMaximumChanged.emit(self.axis_name, None)

    def onMaximumEditingFinished(self):
        """
        Editing maximum value finished
        """
        self.update_maximum_timer.stop()
        self.emitMaximumChanged(self.maximum.text())

    def onUpdateMaximumTimer(self):
        """
        'Update maximum value' timer expired
        """
        self.emitMaximumChanged(self.maximum.text())

    def onMinimumChanged(self, unused_text):
        """
        Minimum value changed handler
        """
        self.update_minimum_timer.start(1000)

    def emitMinimumChanged(self, text):
        """
        Emit 'minimum value changed' signal
        """
        if len(text) > 0:
            self.parent.axisMinimumChanged.emit(self.axis_name, float(text))
        else:
            self.parent.axisMinimumChanged.emit(self.axis_name, None)

    def onUpdateMinimumTimer(self):
        """
        'Update minimum value' timer expired
        """
        self.emitMinimumChanged(self.minimum.text())

    def onMinimumEditingFinished(self):
        """
        Editing maximum value finished
        """
        self.update_minimum_timer.stop()
        self.emitMinimumChanged(self.minimum.text())


class ChartSetupWidget(QtWidgets.QWidget):
    """
    Widget to setup chart
    """

    IDX_VARIABLE_NAME = 0
    IDX_COLOR = 1
    IDX_AXIS = 2
    IDX_LINE_STYLE = 3
    IDX_LINE_WIDTH = 4
    IDX_VARIABLE_NAME_HIDDEN = 5

    chartTitleChanged = QtCore.pyqtSignal(str)
    chartLegendVisibilityChanged = QtCore.pyqtSignal(bool)
    chartLegendAlignmentChanged = QtCore.pyqtSignal(str)
    chartRemoveSeries = QtCore.pyqtSignal()
    chartSeriesAdded = QtCore.pyqtSignal(str, str, object, object)
    chartSeriesReset = QtCore.pyqtSignal(str)
    chartSeriesUpdate = QtCore.pyqtSignal(str, object, object)
    chartSeriesVisibilityChanged = QtCore.pyqtSignal(str, bool)
    chartSeriesNameChanged = QtCore.pyqtSignal(str, str)
    chartSeriesAxisChanged = QtCore.pyqtSignal(str, str)
    chartSeriesColorChanged = QtCore.pyqtSignal(str, object)
    chartSeriesLineStyleChanged = QtCore.pyqtSignal(str, str)
    chartSeriesLineWidthChanged = QtCore.pyqtSignal(str, int)
    axisLabelChanged = QtCore.pyqtSignal(str, str)
    axisMajorTicksChanged = QtCore.pyqtSignal(str, int)
    axisGridLineVisiblityChanged = QtCore.pyqtSignal(str, bool)
    axisLogScaleChanged = QtCore.pyqtSignal(str, bool)
    axisMaximumChanged = QtCore.pyqtSignal(str, object)
    axisMinimumChanged = QtCore.pyqtSignal(str, object)

    def __init__(self, parent):
        super().__init__(parent)

        # CSV reader
        self.reader = None

        self.layout_main = QtWidgets.QVBoxLayout()
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        self.setMinimumWidth(400)
        self.setLayout(self.layout_main)

        # Variables
        self.variables = QtGui.QStandardItemModel()
        self.variables.setHorizontalHeaderLabels(
            ["Name", "", "Axis", "Line style", "Line width", ""])

        self.primary_variable_layout = QtWidgets.QHBoxLayout()

        self.primary_variable_label = QtWidgets.QLabel("Primary variable")
        self.primary_variable_layout.addWidget(self.primary_variable_label)

        self.primary_variable = QtWidgets.QComboBox()
        self.primary_variable.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Fixed)
        self.primary_variable.setModel(self.variables)
        self.primary_variable_layout.addWidget(self.primary_variable)
        self.layout_main.addLayout(self.primary_variable_layout)

        #
        self.variables_view = QtWidgets.QTreeView()
        self.variables_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                          QtWidgets.QSizePolicy.Expanding)
        self.variables_view.setModel(self.variables)
        self.variables_view.setRootIsDecorated(False)
        self.variables_view.setItemDelegate(
            VariablesParamDelegate(self.variables_view))
        self.variables_view.setEditTriggers(
            QtWidgets.QAbstractItemView.EditKeyPressed |
            QtWidgets.QAbstractItemView.CurrentChanged)

        header = self.variables_view.header()
        for i, wd in enumerate([170, 10, 60, 70, 70, 0]):
            header.resizeSection(i, wd)

        self.layout_main.addWidget(self.variables_view)

        self.layout_main.addSpacing(10)

        # chart title
        self.title_layout = QtWidgets.QHBoxLayout()
        self.title_layout.setContentsMargins(0, 0, 0, 10)

        self.title_label = QtWidgets.QLabel("Title")
        self.title_layout.addWidget(self.title_label)

        self.title = QtWidgets.QLineEdit()
        self.title_layout.addWidget(self.title)
        self.layout_main.addLayout(self.title_layout)

        # axes
        self.x_axis = AxisTab(self, 'x')
        self.y_axis = AxisTab(self, 'y')
        self.y2_axis = AxisTab(self, 'y2')

        self.axes_tab = QtWidgets.QTabWidget()
        self.axes_tab.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                    QtWidgets.QSizePolicy.Fixed)
        self.axes_tab.addTab(self.x_axis, "X axis")
        self.axes_tab.addTab(self.y_axis, "Y axis")
        self.axes_tab.addTab(self.y2_axis, "Y2 axis")
        self.layout_main.addWidget(self.axes_tab)

        # Legend
        self.legend_layout = QtWidgets.QHBoxLayout()

        self.legend = QtWidgets.QCheckBox("Legend")
        self.legend_layout.addWidget(self.legend)

        self.legend_position = QtWidgets.QComboBox()
        self.legend_position.addItem('top')
        self.legend_position.addItem('bottom')
        self.legend_position.addItem('left')
        self.legend_position.addItem('right')
        self.legend_layout.addWidget(self.legend_position)

        self.legend_layout.addStretch()

        self.layout_main.addLayout(self.legend_layout)

        self.updateControls()

        self.primary_variable.currentIndexChanged.connect(
            self.onPrimaryVariableChanged)
        self.variables.itemChanged.connect(self.onVariablesChanged)
        self.title.textChanged.connect(self.onTitleChanged)
        self.legend.stateChanged.connect(self.onLegendStateChanged)
        self.legend_position.currentIndexChanged.connect(
            self.onLegendPositionChanged)

        self.color = [
            QtGui.QColor(0, 141, 223),
            QtGui.QColor(121, 199, 44),
            QtGui.QColor(255, 146, 0),
            QtGui.QColor(94, 61, 212),
            QtGui.QColor(192, 60, 40)
        ]

    def updateControls(self):
        """
        Update controls
        """
        legend_enabled = self.legend.checkState() == QtCore.Qt.Checked
        self.legend_position.setEnabled(legend_enabled)

    def onLoadFile(self, file_name):
        """
        Load file handler
        """
        self.reader = PostprocessorReader(file_name)
        for row, var in enumerate(self.reader.variables()):
            self.variables.blockSignals(True)
            si_name = QtGui.QStandardItem(var)
            si_name.setEditable(True)
            si_name.setCheckable(True)
            si_name.setData(var)
            self.variables.setItem(row, self.IDX_VARIABLE_NAME, si_name)

            si_color = QtGui.QStandardItem('\u25a0')
            si_color.setForeground(
                QtGui.QBrush(self.color[row % len(self.color)]))
            self.variables.setItem(row, self.IDX_COLOR, si_color)

            si_axis = QtGui.QStandardItem("left")
            self.variables.setItem(row, self.IDX_AXIS, si_axis)

            si_line_style = QtGui.QStandardItem("solid")
            self.variables.setItem(row, self.IDX_LINE_STYLE, si_line_style)

            si_line_width = QtGui.QStandardItem("2")
            self.variables.setItem(row, self.IDX_LINE_WIDTH, si_line_width)

            # this is used by the primary variable combo box, but we are not
            # showing it in the tree view
            si_name2 = QtGui.QStandardItem(var)
            self.variables.setItem(
                row, self.IDX_VARIABLE_NAME_HIDDEN, si_name2)

            self.variables.blockSignals(False)

            si_name.setCheckState(QtCore.Qt.Unchecked)

        self.primary_variable.setModelColumn(self.IDX_VARIABLE_NAME_HIDDEN)
        self.primary_variable.setCurrentIndex(0)

        self.variables_view.hideColumn(self.IDX_VARIABLE_NAME_HIDDEN)

    def updateFile(self):
        """
        Update file
        """
        idx = self.primary_variable.currentIndex()
        pri_var = self.primary_variable.itemText(idx)
        start = len(self.reader[pri_var])

        self.reader.update()

        xdata = self.reader[pri_var]
        end = len(xdata)

        if start >= end:
            parent = self.variables.invisibleRootItem().index()
            for row in range(self.variables.rowCount()):
                if not self.variables_view.isRowHidden(row, parent):
                    var = self.variables.item(row,
                                              self.IDX_VARIABLE_NAME).data()
                    self.chartSeriesReset.emit(var)
                    ydata = self.reader[var]
                    self.chartSeriesUpdate.emit(var, xdata, ydata)
        else:
            parent = self.variables.invisibleRootItem().index()
            for row in range(self.variables.rowCount()):
                if not self.variables_view.isRowHidden(row, parent):
                    var = self.variables.item(row,
                                              self.IDX_VARIABLE_NAME).data()
                    ydata = self.reader[var]
                    self.chartSeriesUpdate.emit(
                        var, xdata[start:end], ydata[start:end])

    def onPrimaryVariableChanged(self, idx):
        """
        Primary variable changed handler
        """
        # enable all variables in variable view, but disable the primary
        # variable
        pri_var = self.primary_variable.itemText(idx)
        items = self.variables.findItems(pri_var)
        if len(items) > 0:
            disabled_row = items[0].row()
            # update rows in the variables view
            self.variables.blockSignals(True)
            parent = self.variables.invisibleRootItem().index()
            for row in range(self.variables.rowCount()):
                self.variables_view.setRowHidden(
                    row, parent, row == disabled_row)
            self.variables.blockSignals(False)

            # series
            self.chartRemoveSeries.emit()
            for row in range(self.variables.rowCount()):
                if row != disabled_row:
                    var = self.variables.item(
                        row, self.IDX_VARIABLE_NAME).data()
                    self.chartSeriesAdded.emit(
                        pri_var, var, self.reader[pri_var], self.reader[var])

                    color = self.variables.item(
                        row, self.IDX_COLOR).foreground().color()
                    self.chartSeriesColorChanged.emit(var, color)

    def onVariablesChanged(self, item):
        """
        Variables changed handler
        """
        if item.column() == self.IDX_VARIABLE_NAME:
            checked = item.checkState() == QtCore.Qt.Checked
            self.chartSeriesVisibilityChanged.emit(item.data(), checked)
            self.chartSeriesNameChanged.emit(item.data(), item.text())
        elif item.column() == self.IDX_COLOR:
            name = self.variables.item(
                item.row(), self.IDX_VARIABLE_NAME).data()
            color = item.foreground().color()
            self.chartSeriesColorChanged.emit(name, color)
        elif item.column() == self.IDX_AXIS:
            name = self.variables.item(
                item.row(), self.IDX_VARIABLE_NAME).data()
            self.chartSeriesAxisChanged.emit(name, item.text())
        elif item.column() == self.IDX_LINE_STYLE:
            name = self.variables.item(
                item.row(), self.IDX_VARIABLE_NAME).data()
            self.chartSeriesLineStyleChanged.emit(name, item.text())
        elif item.column() == self.IDX_LINE_WIDTH:
            name = self.variables.item(
                item.row(), self.IDX_VARIABLE_NAME).data()
            self.chartSeriesLineWidthChanged.emit(name, int(item.text()))

    def onTitleChanged(self, text):
        """
        Title changed handler
        """
        self.chartTitleChanged.emit(text)

    def onLegendStateChanged(self, state):
        """
        Legend state changed
        """
        self.updateControls()
        self.chartLegendVisibilityChanged.emit(state == QtCore.Qt.Checked)

    def onLegendPositionChanged(self, idx):
        """
        Legend position changed
        """
        alignment = self.legend_position.itemText(idx)
        self.chartLegendAlignmentChanged.emit(alignment)
