from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from gui.OtterObjectsTab import OtterObjectsTab
from otter import common
from otter import annotations
import chigger

class OtterAnnotationsTab(OtterObjectsTab):

    TEXT = 0
    IMAGE = 1
    TIME = 2

    PARAMS_TEXT = [
        { 'name': 'text', 'value': 'Text', 'hint': 'The text to render', 'req': True },
        { 'name': 'font-size', 'value': 20, 'valid': '\d+', 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'halign', 'value': 'left', 'enum': ['left', 'center', 'right'], 'hint': 'The horizontal alignment [left, center, right]', 'req': False },
        { 'name': 'opacity', 'value': None, 'limits': [0., 1.], 'hint': 'The opacity of object', 'req': False },
        { 'name': 'position', 'value': [0.5, 0.5], 'hint': 'The posititon of the viewport with a result', 'req': False },
        { 'name': 'shadow', 'value': False, 'hint': 'Render shadow for the text', 'req': False },
        { 'name': 'valign', 'value': 'top', 'enum': ['top', 'middle', 'bottom'], 'hint': 'The vertical alignment [top, middle, bottom]', 'req': False },
    ]

    PARAMS_IMAGE = [
        { 'name': 'file', 'value': '', 'hint': 'The file name of the image', 'req': True },
        { 'name': 'halign', 'value': 'left', 'enum': ['left', 'center', 'right'], 'hint': 'The horizontal alignment [left, center, right]', 'req': False },
        { 'name': 'position', 'value': [0.5, 0.5], 'hint': 'The posititon of the viewport with a result', 'req': False },
        { 'name': 'scale', 'value': 1., 'hint': 'The scale of the image', 'req': False },
        { 'name': 'valign', 'value': 'top', 'enum': ['top', 'middle', 'bottom'], 'hint': 'The vertical alignment [top, middle, bottom]', 'req': False },
        { 'name': 'width', 'value': 0, 'hint': 'The width of the image', 'req': False },
    ]

    PARAMS_TIME = [
        { 'name': 'font-size', 'value': 20, 'valid': '\d+', 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'format', 'value': annotations.AnnotationTime.FORMAT_STRING, 'hint': 'The format pattern for the time', 'req': False },
        { 'name': 'halign', 'value': 'left', 'enum': ['left', 'center', 'right'], 'hint': 'The horizontal alignment [left, center, right]', 'req': False },
        { 'name': 'opacity', 'value': None, 'limits': [0., 1.], 'hint': 'The opacity of object', 'req': False },
        { 'name': 'position', 'value': [0.5, 0.5], 'hint': 'The posititon of the viewport with a result', 'req': False },
        { 'name': 'shadow', 'value': False, 'hint': 'Render shadow for the text', 'req': False },
        { 'name': 'valign', 'value': 'top', 'enum': ['top', 'middle', 'bottom'], 'hint': 'The vertical alignment [top, middle, bottom]', 'req': False },
    ]

    def __init__(self, parent, chigger_window):
        super(OtterAnnotationsTab, self).__init__(parent, chigger_window)

    def name(self):
        return "ANs"

    def pythonName(self):
        return "annotations"

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
        params = self.itemParams(item)
        item.setText("[text]")

        map = annotations.AnnotationText.MAP
        kwargs = common.remap(params, map)
        ann = chigger.annotations.TextAnnotation(**kwargs)
        item.setData((ann[0], map))
        self.windowResult.append(ann)
        self.windowResult.update()

    def addImageAnnotation(self):
        item = self.addGroup(self.PARAMS_IMAGE, spanned = False)
        params = self.itemParams(item)
        item.setText("[image]")

        map = annotations.AnnotationImage.MAP
        kwargs = common.remap(params, map)
        ann = chigger.annotations.ImageAnnotation(**kwargs)
        item.setData((ann[0], map))
        self.windowResult.append(ann)
        self.windowResult.update()

    def addTimeAnnotation(self):
        item = self.addGroup(self.PARAMS_TIME, spanned = False)
        params = self.itemParams(item)
        item.setText("[time]")

        map = annotations.AnnotationTime.MAP
        kwargs = common.remap(params, map)
        kwargs['text'] = common.formatTimeStr(kwargs['format'], common.t)
        ann = chigger.annotations.TextAnnotation(**kwargs)
        item.setData((ann[0], map))
        self.windowResult.append(ann)
        self.windowResult.update()

    def onTimeChanged(self, time):
        self.updateTimeAnnotations()

    def onTimeUnitChanged(self, time):
        self.updateTimeAnnotations()

    def updateTimeAnnotations(self):
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item.text() == '[time]':
                ann, map = item.data()
                # TODO: get this from the parameter
                format_str = None
                text = common.formatTimeStr(format_str, common.t)
                ann.setOption('text', text)
        self.windowResult.update()
