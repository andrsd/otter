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

        layout = QtWidgets.QGridLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(8, 2, 4, 2)

        self._color_group = QtWidgets.QButtonGroup()
        self._color_group.setExclusive(True)
        self._color_group.buttonClicked.connect(self.onColorPicked)

        # do these first so they get IDs starting from 0
        btn_layout = self._createLayoutForColors(self._color_tr)
        layout.addItem(btn_layout, 0, 1)

        btn_layout = self._createLayoutForColors(self._color_tl)
        layout.addItem(btn_layout, 0, 0)

        btn_layout = self._createGreysLayout()
        layout.addItem(btn_layout, 1, 0)

        btn_layout = self._createColorsLayout()
        layout.addItem(btn_layout, 1, 1)

        w.setLayout(layout)
        self.setDefaultWidget(w)

    def _createLayoutForColors(self, colors):
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(4)

        for clr in colors:
            qclr = QtGui.QColor(clr[0], clr[1], clr[2])
            color_str = qclr.name()

            button = QtWidgets.QRadioButton("")
            button.setStyleSheet("""
                QRadioButton::indicator {{
                    width: 16px;
                    height: 16px;
                    background-color: {};
                }}
                """.format(color_str))

            self._color_group.addButton(button, self._id)
            self._color[self._id] = qclr
            self._id = self._id + 1

            layout.addWidget(button)

        return layout

    def _createGreysLayout(self):
        layout = QtWidgets.QGridLayout()
        layout.setHorizontalSpacing(4)
        layout.setVerticalSpacing(9)

        for row, v in enumerate([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3]):
            qcolors = [
                QtGui.QColor.fromHsv(0, 0, int(v * 255)),
                QtGui.QColor.fromHsv(44, int(0.1 * 255), int(v * 255)),
                QtGui.QColor.fromHsv(207, int(0.1 * 255), int(v * 255))
            ]

            for col, qclr in enumerate(qcolors):
                color_str = qclr.name()

                button = QtWidgets.QRadioButton("")
                button.setStyleSheet("""
                    QRadioButton::indicator {{
                        width: 16px;
                        height: 16px;
                        background-color: {};
                    }}
                    """.format(color_str))

                self._color_group.addButton(button, self._id)
                self._color[self._id] = qclr
                self._id = self._id + 1

                layout.addWidget(button, row, col)

        return layout

    def _createColorsLayout(self):
        layout = QtWidgets.QGridLayout()
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(9)

        for row, l in enumerate([0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]):
            qcolors = []
            hues = [14, 32, 44, 100, 175, 214, 261, 291]
            sats = [0.5, 0.6, 0.7, 0.73, 0.75, 0.84, 1.0]
            for h, s in zip(hues, sats):
                qclr = QtGui.QColor.fromHsl(h, int(s * 255), int(l * 255))
                qcolors.append(qclr)

            for col, qclr in enumerate(qcolors):
                color_str = qclr.name()

                button = QtWidgets.QRadioButton("")
                button.setStyleSheet("""
                    QRadioButton::indicator {{
                        width: 16px;
                        height: 16px;
                        background-color: {};
                    }}
                    QRadioButton::indicator::checked {{
                        border: 2px solid #000;
                    }}
                    """.format(color_str))

                self._color_group.addButton(button, self._id)
                self._color[self._id] = qclr
                self._id = self._id + 1

                layout.addWidget(button, row, col)

        return layout

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
