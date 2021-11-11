from PyQt5 import QtWidgets, QtCore, QtGui
from otter.plugins.viz.PropsBase import PropsBase
from otter.plugins.common.ColorPicker import ColorPicker
from otter.plugins.common.ColorButton import ColorButton


class RootProps(PropsBase):
    """
    Properties page to display when root is selected
    """

    def __init__(self, renderer, parent=None):
        super().__init__(parent)
        self._vtk_renderer = renderer
        self.setupWidgets()

    def setupWidgets(self):
        self._gradient_bkgnd = QtWidgets.QCheckBox("Gradient background")
        self._gradient_bkgnd.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed
        )
        self._vtk_renderer.SetGradientBackground(False)
        self._layout.addWidget(self._gradient_bkgnd)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QtWidgets.QLabel("Color")
        layout.addWidget(lbl)

        self._color_idx = 3

        self._color_picker = ColorPicker(self)
        self._color_picker.setColorIndex(self._color_idx)

        self._color_menu = QtWidgets.QMenu()
        self._color_menu.addAction(self._color_picker)

        qcolor = [0.321, 0.3411, 0.4313]
        self._color_btn = ColorButton()
        self._color_btn.setMenu(self._color_menu)
        self._color_btn.setFixedWidth(64)
        self._color_btn.setColor(
            QtGui.QColor.fromRgbF(qcolor[0], qcolor[1], qcolor[2]))
        self._vtk_renderer.SetBackground(qcolor)
        layout.addWidget(self._color_btn)

        self._layout.addLayout(layout)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QtWidgets.QLabel("Color 2")
        layout.addWidget(lbl)

        self._color_2_idx = 3

        qcolor = [0.321, 0.3411, 0.4313]
        self._color_2_picker = ColorPicker(self)
        self._color_2_picker.setColorIndex(self._color_2_idx)

        self._color_2_menu = QtWidgets.QMenu()
        self._color_2_menu.addAction(self._color_2_picker)

        self._color_2_btn = ColorButton()
        self._color_2_btn.setMenu(self._color_2_menu)
        self._color_2_btn.setFixedWidth(64)
        self._color_2_btn.setColor(
            QtGui.QColor.fromRgbF(qcolor[0], qcolor[1], qcolor[2]))
        self._vtk_renderer.SetBackground2(qcolor)
        layout.addWidget(self._color_2_btn)

        self._layout.addLayout(layout)

        self._gradient_bkgnd.stateChanged.connect(self.onGradientBkgndChanged)
        self._color_picker._color_group.buttonClicked.connect(
            self.onColorClicked)
        self._color_2_picker._color_group.buttonClicked.connect(
            self.onColor2Clicked)

        self._layout.addStretch()

    def onColorClicked(self):
        qcolor = self._color_picker.color()
        clr = [
            qcolor.redF(),
            qcolor.greenF(),
            qcolor.blueF()
        ]
        self._color_btn.setColor(qcolor)
        self._vtk_renderer.SetBackground(clr)

    def onColor2Clicked(self):
        qcolor = self._color_2_picker.color()
        self._color_2_btn.setColor(qcolor)
        clr = [
            qcolor.redF(),
            qcolor.greenF(),
            qcolor.blueF()
        ]
        self._vtk_renderer.SetBackground2(clr)

    def onGradientBkgndChanged(self, state):
        if state == QtCore.Qt.Checked:
            self._vtk_renderer.SetGradientBackground(True)
            self._color_2_btn.setEnabled(True)
        else:
            self._vtk_renderer.SetGradientBackground(False)
            self._color_2_btn.setEnabled(False)
