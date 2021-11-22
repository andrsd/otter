import vtk
from PyQt5 import QtWidgets, QtCore, QtGui
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
        self.buildVtkActor()

    def getVtkActor(self):
        return self._actor

    def setupWidgets(self):
        self._text = QtWidgets.QLineEdit("Text")
        self._layout.addWidget(self._text)

        self._font_props = FontPropertiesWidget()
        self._layout.addWidget(self._font_props)

        self._color_picker = ColorPicker(self)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QtWidgets.QLabel("Text color")
        layout.addWidget(lbl)

        self._color_btn = ColorButton()
        self._color_btn.setFixedWidth(64)
        self._color_btn.setColor(QtGui.QColor("#eee"))
        layout.addWidget(self._color_btn)

        self._layout.addLayout(layout)

        self._layout.addStretch()

        self._text.textChanged.connect(self.onTextChanged)
        self._color_btn.clicked.connect(self.onColorClicked)
        self._color_picker.colorChanged.connect(self.onColorChanged)

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

    def setFocus(self):
        QtCore.QTimer.singleShot(100, self._text.setFocus)

    def onTextChanged(self, txt):
        self._actor.SetInput(txt)

    def onColorClicked(self):
        qcolor = self._color_btn.color()
        self._color_picker.setColor(qcolor)
        self._color_picker.show()

    def onColorChanged(self, qcolor):
        clr = [
            qcolor.redF(),
            qcolor.greenF(),
            qcolor.blueF()
        ]
        self._text_property.SetColor(clr)
        self._color_btn.setColor(qcolor)
