import os
from PyQt5 import QtWidgets, QtCore
from otter.plugins.common.ClickableLabel import ClickableLabel


class FileChangedNotificationWidget(QtWidgets.QWidget):
    """
    """

    reload = QtCore.pyqtSignal()
    dismiss = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            border-radius: 6px;
            background-color: #307BF6;
            color: #fff;
            font-size: 14px;
            """)
        self._setUpWidgets()

    def _setUpWidgets(self):
        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setContentsMargins(30, 8, 30, 8)
        self._layout.setSpacing(20)

        self._text = QtWidgets.QLabel()
        self._layout.addWidget(self._text)

        self._reload = ClickableLabel()
        self._reload.setText("Reload")
        self._reload.setStyleSheet("""
            font-weight: bold;
            """)
        self._layout.addWidget(self._reload)

        self._dismiss = ClickableLabel()
        self._dismiss.setText("Dismiss")
        self._dismiss.setStyleSheet("""
            font-weight: bold;
            """)
        self._layout.addWidget(self._dismiss)

        self.setLayout(self._layout)

        self._reload.clicked.connect(self.onReload)
        self._dismiss.clicked.connect(self.onDismiss)

    def setFileName(self, file_name):
        text = "File '{}' changed".format(os.path.basename(file_name))
        self._text.setText(text)

    def onReload(self):
        self.hide()
        self.reload.emit()

    def onDismiss(self):
        self.hide()
        self.dismiss.emit()
