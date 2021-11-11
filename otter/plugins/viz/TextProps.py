import vtk
from PyQt5 import QtWidgets, QtCore
from otter.plugins.viz.PropsBase import PropsBase
from otter.plugins.viz.FontPropertiesWidget import FontPropertiesWidget
from otter.plugins.common.ColorPicker import ColorPicker
from otter.plugins.common.ColorButton import ColorButton


class TextProps(PropsBase):
    """
    Properties page to display when nothing is selected
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._title.setText("Text properties")
        self.setupWidgets()

    def setupWidgets(self):
        self._text = QtWidgets.QLineEdit("Text")
        self._layout.addWidget(self._text)

        self._font_props = FontPropertiesWidget()
        self._layout.addWidget(self._font_props)

        # whitish color in color picker
        self._color_idx = 3

        self._color_picker = ColorPicker(self)
        self._color_picker.setColorIndex(self._color_idx)

        self._color_menu = QtWidgets.QMenu()
        self._color_menu.addAction(self._color_picker)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QtWidgets.QLabel("Text color")
        layout.addWidget(lbl)

        self._color_btn = ColorButton()
        self._color_btn.setMenu(self._color_menu)
        self._color_btn.setFixedWidth(64)
        layout.addWidget(self._color_btn)

        self._layout.addLayout(layout)

        self._layout.addStretch()

        self._text.textChanged.connect(self.onTextChanged)
        self._color_picker._color_group.buttonClicked.connect(
            self.onColorClicked)

    def buildVtkActor(self):
        self._actor = vtk.vtkTextActor()
        self._actor.SetInput(self._text.text())
        self._actor.SetPickable(True)
        self._actor.SetDragable(True)
        self._text_property = self._actor.GetTextProperty()
        qcolor = self._color_picker.color()
        clr = [
            qcolor.redF(),
            qcolor.greenF(),
            qcolor.blueF()
        ]
        self._text_property.SetColor(clr)
        self._color_btn.setColor(qcolor)
        self._font_props.setVtkTextProperty(self._text_property)
        return self._actor

    def setFocus(self):
        QtCore.QTimer.singleShot(100, self._text.setFocus)

    def onTextChanged(self, txt):
        self._actor.SetInput(txt)

    def onColorClicked(self):
        self._color_idx = self._color_picker.colorIndex()
        qcolor = self._color_picker.color()
        clr = [
            qcolor.redF(),
            qcolor.greenF(),
            qcolor.blueF()
        ]
        self._text_property.SetColor(clr)
        self._color_btn.setColor(qcolor)
