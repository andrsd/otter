from PyQt5 import QtWidgets


class ExpandableWidget(QtWidgets.QWidget):
    """
    Widget with a title and a button to show/hide its content
    """

    def __init__(self, caption="", parent=None):
        super().__init__(parent)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Fixed)

        self._expand_button = QtWidgets.QPushButton()
        self._expand_button.setCheckable(True)
        self._expand_button.setChecked(False)
        self._expand_button.setFlat(True)
        self._expand_button.setFixedSize(30, 20)
        self._expand_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                          QtWidgets.QSizePolicy.Fixed)
        self._expand_button.setStyleSheet("""
            QPushButton {
                border: none;
            }
            QPushButton:checked {
                border: none;
            }
            """)

        self._label = QtWidgets.QLabel()
        self._label.setText(caption)
        self._label.setStyleSheet("""
            color: #444;
            font-weight: bold;
            """)
        self._label.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Fixed)

        self._layout = QtWidgets.QGridLayout()
        self._layout.setSpacing(6)
        self._layout.setHorizontalSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._expand_button, 0, 0)
        self._layout.addWidget(self._label, 0, 1)

        self._expand_button.toggled.connect(self.onExpandToggled)

        self.setLayout(self._layout)

    def setLabel(self, text):
        self._label.setText(text)

    def setWidget(self, widget):
        self._widget = widget
        self._layout.addWidget(self._widget, 1, 0, 1, 2)

        checked = self._expand_button.isChecked()
        self._widget.setVisible(checked)
        self._setExpandButtonText(checked)

    def onExpandToggled(self, checked):
        self._widget.setVisible(checked)
        self._setExpandButtonText(checked)

    def _setExpandButtonText(self, checked):
        if checked:
            self._expand_button.setText("\u25BC")
        else:
            self._expand_button.setText("\u25B6")
