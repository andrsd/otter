from PyQt5 import QtWidgets, QtCore


class SliderWithEdit(QtWidgets.QWidget):
    """
    Slider control with spin box.

    Dragging the slider changes the value in the spin box.
    Changing value in the spin box updates the slider position. This has a
    bug: when users changes the location with slider, this no longer updates
    the slider position - Why? IDK.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._min = 0
        self._max = 10
        self._width = 45

        self._layout = QtWidgets.QHBoxLayout(parent)

        self._slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._slider.setRange(self._min, self._max)
        self._slider.setSingleStep(1)
        self._slider.setPageStep(10)
        self._layout.addWidget(self._slider)

        self._spin = QtWidgets.QSpinBox(parent)
        self._spin.setFixedWidth(self._width)
        self._spin.setRange(self._min, self._max)
        self._spin.setSingleStep(1)
        self._layout.addWidget(self._spin)

        self.setLayout(self._layout)

        self._slider.valueChanged.connect(self.onSliderChanged)
        self._spin.valueChanged.connect(self.onSpinValueChanged)

    def setRange(self, min, max):
        """
        Set the range of allowed values from 'min' to 'max'
        """
        self._slider.setRange(min, max)
        self._spin.setRange(min, max)
        self._min = min
        self._max = max

    def onSliderChanged(self, value):
        """
        Called when  slider was moved
        """
        self.blockSignals(True)
        self._spin.setValue(value)
        self.blockSignals(False)

    def onSpinValueChanged(self, value):
        """
        Called when edit value was changed
        """
        self.blockSignals(True)
        self._slider.setValue(value)
        self.blockSignals(False)


if __name__ == '__main__':
    import sys
    qapp = QtWidgets.QApplication(sys.argv)
    w = SliderWithEdit()
    w.setRange(0, 100)
    w.show()
    qapp.exec()
