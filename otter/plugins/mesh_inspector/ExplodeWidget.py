from PyQt5 import QtWidgets, QtCore, QtGui
from otter.plugins.common.ClickableLabel import ClickableLabel


class ExplodeWidget(QtWidgets.QWidget):
    """
    Widget with a slider to setup the amount of explosion
    """

    closed = QtCore.pyqtSignal()
    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._range = 100

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            border-radius: 3px;
            background-color: #222;
            color: #fff;
            font-size: 14px;
            """)
        self._opacity = QtWidgets.QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(0.8)
        self.setGraphicsEffect(self._opacity)

        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setContentsMargins(15, 8, 15, 8)

        self._mag_validator = QtGui.QDoubleValidator()
        self._mag_validator.setBottom(0.)

        self._magnitude = QtWidgets.QLineEdit("1.0")
        self._magnitude.setValidator(self._mag_validator)
        self._magnitude.setFixedWidth(30)
        self._layout.addWidget(self._magnitude)

        self._x_lbl = QtWidgets.QLabel("x")
        self._layout.addWidget(self._x_lbl)

        self._slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self._slider.setRange(0, self._range)
        self._slider.setSingleStep(1)
        self._slider.setPageStep(5)
        self._slider.setFixedWidth(400)
        self._layout.addWidget(self._slider)

        self._close = ClickableLabel()
        self._close.setText("Close")
        self._close.setStyleSheet("""
            font-weight: bold;
            """)
        self._layout.addWidget(self._close)

        self.setLayout(self._layout)

        self._slider.valueChanged.connect(self.onSliderValueChanged)
        self._magnitude.editingFinished.connect(self.onMagnitudeChanged)
        self._close.clicked.connect(self.onClose)

    def range(self):
        return self._range

    def onSliderValueChanged(self, value):
        scale = float(self._magnitude.text())
        self.valueChanged.emit(scale * value)

    def onMagnitudeChanged(self):
        scale = float(self._magnitude.text())
        value = self._slider.value()
        self.valueChanged.emit(scale * value)

    def onClose(self):
        self.hide()
        self.closed.emit()
