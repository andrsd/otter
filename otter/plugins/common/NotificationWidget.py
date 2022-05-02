from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from otter.plugins.common.ClickableLabel import ClickableLabel


class NotificationWidget(QWidget):

    """
    Widget for simple notifications

    Show up as a rectangle with round corners with a text and a dismiss
    button
    """

    dismiss = pyqtSignal()

    def __init__(self, parent=None):
        """Inits NotificationWidget

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            border-radius: 6px;
            background-color: #307BF6;
            color: #fff;
            font-size: 14px;
            """)
        self.setUpWidgets()

    def setUpWidgets(self):
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(30, 8, 30, 8)
        self.layout.setSpacing(20)

        self.text = QLabel()
        self.layout.addWidget(self.text)

        self.dismiss_label = ClickableLabel()
        self.dismiss_label.setText("\u2716")
        self.dismiss_label.setStyleSheet("""
            font-weight: bold;
            """)
        self.layout.addWidget(self.dismiss_label)

        self.setLayout(self.layout)

        self.dismiss_label.clicked.connect(self.onDismiss)

    def setText(self, text):
        self.text.setText(text)

    def onDismiss(self):
        self.hide()
        self.dismiss.emit()

    def show(self, ms=2000):
        super().show()
        QTimer.singleShot(2000, self.onNotificationFadeOut)

    def onNotificationFadeOut(self):
        effect = QtWidgets.QGraphicsOpacityEffect()
        self.setGraphicsEffect(effect)

        self.anim = QtCore.QPropertyAnimation(effect, b"opacity")
        self.anim.setDuration(250)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.finished.connect(self.hide)
        self.anim.start()
