#!/usr/bin/env python2

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from OtterObjectsTab import OtterObjectsTab

class OtterAnnotationsTab(OtterObjectsTab):

    TEXT = 0
    IMAGE = 1
    TIME = 2

    def __init__(self, parent):
        super(OtterAnnotationsTab, self).__init__(parent)

    def name(self):
        return "ANs"

    def buildAddButton(self):
        btn = QPushButton("Add", self)
        mnu = QMenu("Add", self)
        mnu.addAction("Text", lambda : self.onAddAnnotation(self.TEXT))
        mnu.addAction("Image", lambda : self.onAddAnnotation(self.IMAGE))
        mnu.addAction("Time", lambda : self.onAddAnnotation(self.TIME))
        btn.setMenu(mnu)
        return btn

    def onAddAnnotation(self, type):
        pass

    def toText(self):
        str = ""
        str += "annotations = [\n"
        str += "]\n"

        return str
