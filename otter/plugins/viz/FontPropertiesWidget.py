from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox, QPushButton
from PyQt5.QtGui import QIntValidator


class FontPropertiesWidget(QWidget):
    """
    Widget for setting font properties
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._vtk_property = None

        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(1)

        self._font_family = QComboBox()
        self._font_family.addItem("Arial")
        self._font_family.addItem("Courier")
        self._font_family.addItem("Times")
        self._layout.addWidget(self._font_family)

        self._font_size = QComboBox()
        self._font_size.addItem("9")
        self._font_size.addItem("10")
        self._font_size.addItem("11")
        self._font_size.addItem("12")
        self._font_size.addItem("14")
        self._font_size.addItem("16")
        self._font_size.addItem("18")
        self._font_size.addItem("22")
        self._font_size.addItem("28")
        self._font_size.setEditable(True)
        self._font_size.setFixedWidth(60)
        self._layout.addWidget(self._font_size)

        validator = QIntValidator()
        validator.setBottom(1)
        self._font_size.setValidator(validator)

        self._bold_button = QPushButton("B")
        self._bold_button.setFixedSize(48, 32)
        self._bold_button.setCheckable(True)
        self._layout.addWidget(self._bold_button)

        self._italics_button = QPushButton("I")
        self._italics_button.setCheckable(True)
        self._italics_button.setFixedSize(48, 32)
        self._layout.addWidget(self._italics_button)

        self._font_family.currentIndexChanged.connect(
            self.onSetFontFamilyChanged)
        self._font_size.currentTextChanged.connect(self.onFontSizeChanged)
        self._bold_button.toggled.connect(self.onBoldToggled)
        self._italics_button.toggled.connect(self.onItalicsToggled)

        self.setLayout(self._layout)

    def setVtkTextProperty(self, property):
        self._vtk_property = property

        self._font_size.setCurrentText("24")
        font_family = property.GetFontFamilyAsString()
        self._font_family.setCurrentText(font_family)
        self._font_size.setCurrentText(str(property.GetFontSize()))
        self._bold_button.setChecked(property.GetBold())
        self._italics_button.setChecked(property.GetItalic())

    def onBoldToggled(self, checked):
        self._vtk_property.SetBold(checked)

    def onItalicsToggled(self, checked):
        self._vtk_property.SetItalic(checked)

    def onFontSizeChanged(self, txt):
        if len(txt) > 0:
            size = int(txt)
            self._vtk_property.SetFontSize(size)

    def onSetFontFamilyChanged(self, index):
        font_family = self._font_family.itemText(index)
        self._vtk_property.SetFontFamilyAsString(font_family)
