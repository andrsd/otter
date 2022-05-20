from PyQt5.QtWidgets import QWidget, QHBoxLayout, QGraphicsOpacityEffect, \
    QPushButton
from PyQt5.QtCore import Qt


class ToolBar(QWidget):
    """
    Window for entering parameters
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._main_wnd = parent

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("options")
        self.setStyleSheet("""
            #options, #closeButton {
                border-radius: 6px;
                background-color: rgb(0, 0, 0);
                color: #fff;
            }
            QToolBar {
                background-color: rgb(0, 0, 0);
                color: #fff;
            }
            """)

        self.setupWidgets()

        effect = QGraphicsOpacityEffect()
        effect.setOpacity(0.66)
        self.setGraphicsEffect(effect)

        self.setMinimumWidth(220)
        self.updateWidgets()
        self.connectSignals()

        self.setAcceptDrops(True)

    def mainWnd(self):
        return self._main_wnd

    def setupWidgets(self):
        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(6, 5, 12, 12)
        self._layout.setSpacing(0)

        self._open_file = self.addButton("O", self._main_wnd.onOpenFile)
        self._layout.addSpacing(8)
        self._add_text = self.addButton("T", self._main_wnd.onAddText)

        self._layout.addStretch()

        self.setLayout(self._layout)

    def addButton(self, text, action):
        button = QPushButton(text)
        button.clicked.connect(action)
        self._layout.addWidget(button)
        return button

    def connectSignals(self):
        pass

    def updateWidgets(self):
        pass
