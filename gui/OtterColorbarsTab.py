#!/usr/bin/env python2

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from OtterObjectsTab import OtterObjectsTab

class OtterColorbarsTab(OtterObjectsTab):

    def __init__(self, parent):
        super(OtterColorbarsTab, self).__init__(parent)

    def name(self):
        return "CBs"

    def buildAddButton(self):
        btn = QPushButton("Add", self)
        btn.clicked.connect(self.onAdd)
        return btn

    def onAdd(self):
        pass
