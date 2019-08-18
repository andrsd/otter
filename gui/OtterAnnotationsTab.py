#!/usr/bin/env python2

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from OtterObjectsTab import OtterObjectsTab

class OtterAnnotationsTab(OtterObjectsTab):

    TEXT = 0
    IMAGE = 1
    TIME = 2

    PARAMS_BASE = [
        { 'name': 'position', 'value': [0.5, 0.5], 'hint': 'The posititon of the viewport with a result', 'req': False },
        { 'name': 'halign', 'value': 'left', 'hint': 'The horizontal alignment [left, center, right]', 'req': False },
        { 'name': 'valign', 'value': 'top', 'hint': 'The vertical alignment [top, middle, bottom]', 'req': False },
        { 'name': 'opacity', 'value': None, 'hint': 'The opacity of object', 'req': False },
        { 'name': 'shadow', 'value': False, 'hint': 'Render shadow for the text', 'req': False },
        { 'name': 'font-size', 'value': None, 'hint': 'The size of the font used for the numbers', 'req': False }
    ]

    PARAMS_TEXT = PARAMS_BASE + [
        { 'name': 'text', 'value': '', 'hint': 'The text to render', 'req': True },
    ]

    PARAMS_IMAGE = [
        { 'name': 'file', 'value': '', 'hint': 'The file name of the image', 'req': True },
        { 'name': 'halign', 'value': 'left', 'hint': 'The horizontal alignment [left, center, right]', 'req': False },
        { 'name': 'valign', 'value': 'top', 'hint': 'The vertical alignment [top, middle, bottom]', 'req': False },
        { 'name': 'position', 'value': [0.5, 0.5], 'hint': 'The posititon of the viewport with a result', 'req': False },
        { 'name': 'width', 'value': 0, 'hint': 'The width of the image', 'req': False },
        { 'name': 'scale', 'value': 1., 'hint': 'The scale of the image', 'req': False },
    ]

    PARAMS_TIME = PARAMS_BASE + [
        { 'name': 'format', 'value': '', 'hint': 'The format pattern for the time', 'req': False },
    ]

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
        item = self.addGroup(self.PARAMS_TEXT, spanned = False)
        item.setText("[text]")

    def addImageAnnotation(self):
        item = self.addGroup(self.PARAMS_IMAGE, spanned = False)
        item.setText("[image]")

    def addTimeAnnotation(self):
        item = self.addGroup(self.PARAMS_TIME, spanned = False)
        item.setText("[time]")

    def toText(self):
        str = ""
        str += "annotations = [\n"
        str += "]\n"

        return str
