from PyQt5 import QtWidgets, QtGui, QtCore


class ColorPicker(QtWidgets.QDialog):

    colorChanged = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        # application specific data
        self._data = None
        self._qcolor = QtGui.QColor("#eee")

        self._color_tl = [
            [0, 0, 0],
            [19, 0, 255],
            [254, 0, 0]
        ]

        self._color_tr = [
            [156, 207, 237],
            [165, 165, 165],
            [60, 97, 180],
            [234, 234, 234],
            [197, 226, 243],
            [247, 135, 3],
            [127, 127, 127],
            [250, 182, 0]
        ]

        self._id = 0
        self._color = {}

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self._layout.setContentsMargins(8, 8, 8, 10)
        self._layout.setSpacing(4)

        self._grid_layout = QtWidgets.QGridLayout()
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setVerticalSpacing(8)

        self._color_group = QtWidgets.QButtonGroup()
        self._color_group.setExclusive(True)
        self._color_group.buttonClicked.connect(self.onColorPicked)

        # do these first so they get IDs starting from 0
        self._grid_layout.setColumnMinimumWidth(3, 5)
        self._grid_layout.setRowMinimumHeight(1, 5)

        self._fillLayoutWithColors(0, 4, self._color_tr)
        self._fillLayoutWithColors(0, 0, self._color_tl)
        self._fillLayoutWithGreys(2, 0)
        self._fillLayoutWithColors2(2, 4)

        self._layout.addLayout(self._grid_layout, 1)

        self._opacity_layout = QtWidgets.QHBoxLayout()
        self._opacity_layout.setContentsMargins(0, 0, 0, 0)

        self._color_sample = QtWidgets.QLabel()
        self._color_sample.setFixedSize(50, 20)
        self._updateColorSample()
        self._opacity_layout.addWidget(self._color_sample)

        self._opacity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._opacity_slider.setRange(0, 100)
        self._opacity_layout.addWidget(self._opacity_slider)

        self._opacity = QtWidgets.QLineEdit("0.99")
        self._opacity.setFixedWidth(40)
        self._opacity.setValidator(QtGui.QDoubleValidator(0., 1., 2))
        self._opacity_layout.addWidget(self._opacity)

        self._layout.addLayout(self._opacity_layout)

        self._rgb_layout = QtWidgets.QHBoxLayout()
        self._rgb_layout.setSpacing(5)

        self._lbl_name = QtWidgets.QLabel("#")
        self._rgb_layout.addWidget(self._lbl_name)

        self._name = QtWidgets.QLineEdit("FFFFFF")
        self._name.setFixedWidth(55)
        self._rgb_layout.addWidget(self._name)

        self._lbl_red = QtWidgets.QLabel("R")
        self._rgb_layout.addWidget(self._lbl_red)

        self._red = QtWidgets.QLineEdit("255")
        self._red.setFixedWidth(30)
        self._red.setValidator(QtGui.QIntValidator(0, 255))
        self._rgb_layout.addWidget(self._red)

        self._lbl_green = QtWidgets.QLabel("G")
        self._rgb_layout.addWidget(self._lbl_green)

        self._green = QtWidgets.QLineEdit("255")
        self._green.setFixedWidth(30)
        self._green.setValidator(QtGui.QIntValidator(0, 255))
        self._rgb_layout.addWidget(self._green)

        self._lbl_blue = QtWidgets.QLabel("B")
        self._rgb_layout.addWidget(self._lbl_blue)

        self._blue = QtWidgets.QLineEdit("255")
        self._blue.setFixedWidth(30)
        self._blue.setValidator(QtGui.QIntValidator(0, 255))
        self._rgb_layout.addWidget(self._blue)

        self._layout.addLayout(self._rgb_layout)

        self.setLayout(self._layout)
        self.setWindowTitle("Colors")
        self.setWindowFlag(QtCore.Qt.Tool)
        self.setWindowFlag(QtCore.Qt.CustomizeWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowMinMaxButtonsHint, False)

        self._opacity_slider.valueChanged.connect(self.onOpacitySliderChanged)
        self._opacity.textChanged.connect(self.onOpacityChanged)
        self._red.textChanged.connect(self.onRedChanged)
        self._green.textChanged.connect(self.onGreenChanged)
        self._blue.textChanged.connect(self.onBlueChanged)

    def _fillLayoutWithColors(self, row, col, colors):
        for clr in colors:
            qclr = QtGui.QColor(clr[0], clr[1], clr[2])
            color_str = qclr.name()

            button = QtWidgets.QRadioButton("")
            button.setFixedSize(17, 17)
            button.setStyleSheet("""
                QRadioButton::indicator {{
                    width: 15px;
                    height: 15px;
                    background-color: {};
                    border: 1px solid #eee;
                }}
                QRadioButton::indicator::checked {{
                    border: 1px solid #000;
                }}
                """.format(color_str))

            self._color_group.addButton(button, self._id)
            self._color[self._id] = qclr
            self._id = self._id + 1

            self._grid_layout.addWidget(button, row, col)
            col = col + 1

    def _fillLayoutWithGreys(self, st_row, st_col):
        for row, v in enumerate([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3]):
            qcolors = [
                QtGui.QColor.fromHsv(0, 0, int(v * 255)),
                QtGui.QColor.fromHsv(44, int(0.1 * 255), int(v * 255)),
                QtGui.QColor.fromHsv(207, int(0.1 * 255), int(v * 255))
            ]

            for col, qclr in enumerate(qcolors):
                color_str = qclr.name()

                button = QtWidgets.QRadioButton("")
                button.setFixedSize(17, 17)
                button.setStyleSheet("""
                    QRadioButton::indicator {{
                        width: 15px;
                        height: 15px;
                        background-color: {};
                        border: 1px solid #eee;
                    }}
                    QRadioButton::indicator::checked {{
                        border: 1px solid #000;
                    }}
                    """.format(color_str))

                self._color_group.addButton(button, self._id)
                self._color[self._id] = qclr
                self._id = self._id + 1

                self._grid_layout.addWidget(button, st_row + row, st_col + col)

    def _fillLayoutWithColors2(self, st_row, st_col):
        hues = [14, 32, 44, 100, 175, 214, 261, 291]
        for col, hu in enumerate(hues):
            qcolors = []
            lightnesses = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
            saturations = [0.5, 0.6, 0.7, 0.73, 0.75, 0.84, 1.0]
            for li, sa in zip(lightnesses, saturations):
                qclr = QtGui.QColor.fromHsl(hu, int(sa * 255), int(li * 255))
                qcolors.append(qclr)

            for row, qclr in enumerate(qcolors):
                color_str = qclr.name()

                button = QtWidgets.QRadioButton("")
                button.setFixedSize(17, 17)
                button.setStyleSheet("""
                    QRadioButton::indicator {{
                        width: 15px;
                        height: 15px;
                        background-color: {};
                        border: 1px solid #eee;
                    }}
                    QRadioButton::indicator::checked {{
                        border: 1px solid #000;
                    }}
                    """.format(color_str))

                self._color_group.addButton(button, self._id)
                self._color[self._id] = qclr
                self._id = self._id + 1

                self._grid_layout.addWidget(button, st_row + row, st_col + col)

    def setColor(self, qcolor):
        self._qcolor = qcolor
        self._updateColorWidgets()

    def color(self):
        return self._qcolor

    def setData(self, data):
        self._data = data

    def data(self):
        return self._data

    def _updateColorSample(self):
        self._color_sample.setStyleSheet("""
            border: 1px solid #000;
            background: {};
            """.format(self._qcolor.name()))

    def _updateColorWidgets(self):
        self._name.setText(self._qcolor.name()[1:])
        self._red.setText(str(self._qcolor.red()))
        self._green.setText(str(self._qcolor.green()))
        self._blue.setText(str(self._qcolor.blue()))
        self._opacity.setText(str(self._qcolor.alphaF()))
        self._updateColorSample()

    def onColorPicked(self, button):
        id = self._color_group.id(button)
        self._qcolor = self._color[id]
        self._updateColorWidgets()
        self.colorChanged.emit(self._qcolor)

    def onOpacitySliderChanged(self, value):
        self.blockSignals(True)
        self._opacity.setText(str(value))
        self.blockSignals(False)

    def onOpacityChanged(self, text):
        self.blockSignals(True)
        if len(text) > 0:
            val = int(float(text) * 100)
            self._opacity_slider.setValue(val)
        else:
            self._opacity_slider.setValue(0.)
        self.blockSignals(False)

    def onRedChanged(self, text):
        if len(text) > 0:
            val = int(text)
            self._qcolor.setRed(val)
            self.blockSignals(True)
            self._updateColorWidgets()
            self.blockSignals(False)
        else:
            self._qcolor.setRed(0)

    def onGreenChanged(self, text):
        if len(text) > 0:
            val = int(text)
            self._qcolor.setGreen(val)
            self.blockSignals(True)
            self._updateColorWidgets()
            self.blockSignals(False)
        else:
            self._qcolor.setGreen(0)

    def onBlueChanged(self, text):
        if len(text) > 0:
            val = int(text)
            self._qcolor.setBlue(val)
            self.blockSignals(True)
            self._updateColorWidgets()
            self.blockSignals(False)
        else:
            self._qcolor.setBlue(0)
