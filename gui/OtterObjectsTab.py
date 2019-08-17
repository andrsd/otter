#!/usr/bin/env python2

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu

class OtterObjectsTab(QWidget):

    def __init__(self, parent):
        super(OtterObjectsTab, self).__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 3)
        self.setLayout(layout)

        btn = self.buildAddButton()
        layout.addWidget(btn)

        self.ctlObjects = QTreeView(self)
        layout.addWidget(self.ctlObjects)
