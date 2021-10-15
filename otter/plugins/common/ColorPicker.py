from PyQt5 import QtWidgets, QtGui


class ColorPicker(QtWidgets.QWidgetAction):

    def __init__(self, parent=None):
        super().__init__(parent)

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

        w = QtWidgets.QWidget(parent)

        self._layout = QtWidgets.QGridLayout()
        self._layout.setVerticalSpacing(6)
        self._layout.setHorizontalSpacing(3)
        self._layout.setContentsMargins(8, 2, 4, 2)

        self._color_group = QtWidgets.QButtonGroup()
        self._color_group.setExclusive(True)
        self._color_group.buttonClicked.connect(self.onColorPicked)

        # do these first so they get IDs starting from 0
        self._layout.setColumnMinimumWidth(3, 5)
        self._layout.setRowMinimumHeight(1, 5)

        self._fillLayoutWithColors(0, 4, self._color_tr)
        self._fillLayoutWithColors(0, 0, self._color_tl)
        self._fillLayoutWithGreys(2, 0)
        self._fillLayoutWithColors2(2, 4)

        w.setLayout(self._layout)
        w.setStyleSheet("""
            background-color: #fefefe
            """)
        self.setDefaultWidget(w)

    def _fillLayoutWithColors(self, row, col, colors):
        for clr in colors:
            qclr = QtGui.QColor(clr[0], clr[1], clr[2])
            color_str = qclr.name()

            button = QtWidgets.QRadioButton("")
            button.setFixedSize(16, 16)
            button.setStyleSheet("""
                QRadioButton::indicator {{
                    width: 14px;
                    height: 14px;
                    background-color: {};
                }}
                QRadioButton::indicator::checked {{
                    border: 1px solid #000;
                }}
                """.format(color_str))

            self._color_group.addButton(button, self._id)
            self._color[self._id] = qclr
            self._id = self._id + 1

            self._layout.addWidget(button, row, col)
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
                button.setFixedSize(16, 16)
                button.setStyleSheet("""
                    QRadioButton::indicator {{
                        width: 14px;
                        height: 14px;
                        background-color: {};
                    }}
                    QRadioButton::indicator::checked {{
                        border: 1px solid #000;
                    }}
                    """.format(color_str))

                self._color_group.addButton(button, self._id)
                self._color[self._id] = qclr
                self._id = self._id + 1

                self._layout.addWidget(button, st_row + row, st_col + col)

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
                button.setFixedSize(17, 16)
                button.setStyleSheet("""
                    QRadioButton::indicator {{
                        width: 14px;
                        height: 14px;
                        background-color: {};
                    }}
                    QRadioButton::indicator::checked {{
                        border: 1px solid #000;
                    }}
                    """.format(color_str))

                self._color_group.addButton(button, self._id)
                self._color[self._id] = qclr
                self._id = self._id + 1

                self._layout.addWidget(button, st_row + row, st_col + col)

    def setColorIndex(self, clr_idx):
        button = self._color_group.button(clr_idx)
        button.setChecked(True)

    def color(self):
        id = self._color_group.checkedId()
        return self._color[id]

    def colorIndex(self):
        return self._color_group.checkedId()

    def onColorPicked(self, button):
        pass
