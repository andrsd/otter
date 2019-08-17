#!/usr/bin/env python2

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from PyQt5.QtGui import QStandardItemModel

class OtterObjectsTab(QWidget):

    INDENT = 14

    def __init__(self, parent):
        super(OtterObjectsTab, self).__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 3)
        self.setLayout(layout)

        btn = self.buildAddButton()
        layout.addWidget(btn)

        self.model = QStandardItemModel(0, 2, self)
        self.model.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.model.sort(0, Qt.AscendingOrder)

        self.ctlObjects = QTreeView(self)
        self.ctlObjects.setModel(self.model)
        self.ctlObjects.setRootIsDecorated(False)
        self.ctlObjects.setIndentation(OtterObjectsTab.INDENT)
        layout.addWidget(self.ctlObjects)
