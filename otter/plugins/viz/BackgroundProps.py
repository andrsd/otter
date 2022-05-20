from PyQt5.QtWidgets import QCheckBox, QSizePolicy, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from otter.plugins.viz.PropsBase import PropsBase
from otter.plugins.common.ColorPicker import ColorPicker
from otter.plugins.common.ColorButton import ColorButton


class BackgroundProps(PropsBase):
    """
    Properties page to display when root is selected
    """

    def __init__(self, renderer, parent=None):
        super().__init__(parent)
        self._vtk_renderer = renderer
        self.setWindowTitle("Background")
        self.setupWidgets()
        self.connectSignals()

    def setupWidgets(self):
        self._gradient_bkgnd = QCheckBox("Gradient background")
        self._gradient_bkgnd.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._vtk_renderer.SetGradientBackground(False)
        self._layout.addWidget(self._gradient_bkgnd)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel("Color")
        layout.addWidget(lbl)

        self._color_picker = ColorPicker(self)

        self._color_btn = ColorButton()
        qcolor = [0.321, 0.3411, 0.4313]
        self._color_btn.setColor(
            QColor.fromRgbF(qcolor[0], qcolor[1], qcolor[2]))
        self._vtk_renderer.SetBackground(qcolor)
        layout.addWidget(self._color_btn)

        self._layout.addLayout(layout)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel("Color 2")
        layout.addWidget(lbl)

        self._color_2_picker = ColorPicker(self)

        self._color_2_btn = ColorButton()
        qcolor = [0.321, 0.3411, 0.4313]
        self._color_2_btn.setColor(
            QColor.fromRgbF(qcolor[0], qcolor[1], qcolor[2]))
        self._vtk_renderer.SetBackground2(qcolor)
        layout.addWidget(self._color_2_btn)

        self._layout.addLayout(layout)

        self.setLayout(self._layout)

    def connectSignals(self):
        self._gradient_bkgnd.stateChanged.connect(self.onGradientBkgndChanged)
        self._color_btn.clicked.connect(self.onColorClicked)
        self._color_picker.colorChanged.connect(self.onColorChanged)
        self._color_2_btn.clicked.connect(self.onColor2Clicked)
        self._color_2_picker.colorChanged.connect(self.onColor2Changed)

        self.onGradientBkgndChanged(self._gradient_bkgnd.checkState())

    def onColorClicked(self):
        qcolor = self._color_btn.color()
        self._color_picker.setColor(qcolor)
        self._color_picker.show()

    def onColorChanged(self, qcolor):
        self._color_btn.setColor(qcolor)
        clr = [
            qcolor.redF(),
            qcolor.greenF(),
            qcolor.blueF()
        ]
        self._vtk_renderer.SetBackground(clr)

    def onColor2Clicked(self):
        qcolor = self._color_2_btn.color()
        self._color_2_picker.setColor(qcolor)
        self._color_2_picker.show()

    def onColor2Changed(self, qcolor):
        self._color_2_btn.setColor(qcolor)
        clr = [
            qcolor.redF(),
            qcolor.greenF(),
            qcolor.blueF()
        ]
        self._vtk_renderer.SetBackground2(clr)

    def onGradientBkgndChanged(self, state):
        if state == Qt.Checked:
            self._vtk_renderer.SetGradientBackground(True)
            self._color_2_btn.setEnabled(True)
        else:
            self._vtk_renderer.SetGradientBackground(False)
            self._color_2_btn.setEnabled(False)
