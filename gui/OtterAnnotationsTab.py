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
        mnu.addAction("Text", lambda : self.onAdd(self.TEXT))
        mnu.addAction("Image", lambda : self.onAdd(self.IMAGE))
        mnu.addAction("Time", lambda : self.onAdd(self.TIME))
        btn.setMenu(mnu)
        return btn

    def onAdd(self, type):
        if type == self.TEXT:
            self.addTextAnnotation()
        elif type == self.IMAGE:
            self.addImageAnnotation()
        elif type == self.TIME:
            self.addTimeAnnotation()

    def addTextAnnotation(self):
        pass

    def addImageAnnotation(self):
        pass

    def addTimeAnnotation(self):
        pass

    def toText(self):
        str = ""
        str += "annotations = [\n"
        str += "]\n"

        return str
