from PyQt5 import QtWidgets
from gui.OtterObjectsTab import OtterObjectsTab
from otter import common, annotations
import chigger

class OtterAnnotationsTab(OtterObjectsTab):

    TEXT = 0
    IMAGE = 1
    TIME = 2

    PARAMS_TEXT = [
        { 'name': 'text', 'value': 'Text', 'hint': 'The text to render', 'req': True },
        { 'name': 'color', 'value': [1, 1, 1], 'hint': 'The color of the text', 'req': False },
        { 'name': 'font-size', 'value': 20, 'valid': '\d+', 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'font-family', 'value': None, 'hint': 'The font family of the font', 'req': False },
        { 'name': 'bold', 'value': False, 'hint': 'The font bolding', 'req': False },
        { 'name': 'italic', 'value': False, 'hint': 'The font italic', 'req': False },
        { 'name': 'halign', 'value': 'left', 'enum': ['left', 'center', 'right'], 'hint': 'The horizontal alignment [left, center, right]', 'req': False },
        { 'name': 'opacity', 'value': None, 'limits': [0., 1.], 'hint': 'The opacity of object', 'req': False },
        { 'name': 'position', 'value': [0.5, 0.5], 'hint': 'The posititon of the viewport with a result', 'req': False },
        { 'name': 'shadow', 'value': False, 'hint': 'Render shadow for the text', 'req': False },
        { 'name': 'valign', 'value': 'top', 'enum': ['top', 'middle', 'bottom'], 'hint': 'The vertical alignment [top, middle, bottom]', 'req': False },
    ]

    PARAMS_IMAGE = [
        { 'name': 'file', 'file': 'open', 'value': '', 'hint': 'The file name of the image', 'req': True },
        { 'name': 'halign', 'value': 'left', 'enum': ['left', 'center', 'right'], 'hint': 'The horizontal alignment [left, center, right]', 'req': False },
        { 'name': 'opacity', 'value': None, 'limits': [0., 1.], 'hint': 'The opacity of object', 'req': False },
        { 'name': 'position', 'value': [0.5, 0.5], 'hint': 'The posititon of the viewport with a result', 'req': False },
        { 'name': 'scale', 'value': 1., 'hint': 'The scale of the image', 'req': False },
        { 'name': 'valign', 'value': 'top', 'enum': ['top', 'middle', 'bottom'], 'hint': 'The vertical alignment [top, middle, bottom]', 'req': False },
        { 'name': 'width', 'value': 0, 'hint': 'The width of the image', 'req': False },
    ]

    PARAMS_TIME = [
        { 'name': 'font-size', 'value': 20, 'valid': '\d+', 'hint': 'The size of the font used for the numbers', 'req': False },
        { 'name': 'color', 'value': [1, 1, 1], 'hint': 'The color of the text', 'req': False },
        { 'name': 'format', 'value': annotations.AnnotationTime.FORMAT_STRING, 'hint': 'The format pattern for the time', 'req': False },
        { 'name': 'font-family', 'value': None, 'hint': 'The font family of the font', 'req': False },
        { 'name': 'bold', 'value': False, 'hint': 'The font bolding', 'req': False },
        { 'name': 'italic', 'value': False, 'hint': 'The font italic', 'req': False },
        { 'name': 'halign', 'value': 'left', 'enum': ['left', 'center', 'right'], 'hint': 'The horizontal alignment [left, center, right]', 'req': False },
        { 'name': 'opacity', 'value': None, 'limits': [0., 1.], 'hint': 'The opacity of object', 'req': False },
        { 'name': 'position', 'value': [0.5, 0.5], 'hint': 'The posititon of the viewport with a result', 'req': False },
        { 'name': 'shadow', 'value': False, 'hint': 'Render shadow for the text', 'req': False },
        { 'name': 'valign', 'value': 'top', 'enum': ['top', 'middle', 'bottom'], 'hint': 'The vertical alignment [top, middle, bottom]', 'req': False },
    ]

    def __init__(self, parent, chigger_window):
        super(OtterAnnotationsTab, self).__init__(parent, chigger_window)
        self._text_to_type = {
            '[text]': 'Text',
            '[image]': 'Image',
            '[time]': 'Time',
        }

    def name(self):
        return "ANs"

    def pythonName(self):
        return "annotations"

    def buildAddButton(self):
        btn = QtWidgets.QPushButton("   +", self)
        mnu = QtWidgets.QMenu("Add", self)
        mnu.addAction("Text", lambda : self.onAdd(self.TEXT))
        mnu.addAction("Image", lambda : self.onAdd(self.IMAGE))
        mnu.addAction("Time", lambda : self.onAdd(self.TIME))
        btn.setMenu(mnu)
        btn.setStyleSheet("::menu-indicator{ image: none; }")
        return btn

    def addObject(self, params):
        type = params['type']
        if type == 'Text':
            obj_item = self.addTextAnnotation()
            self.setObjectParams(obj_item, params)
        elif type == 'Image':
            obj_item = self.addImageAnnotation()
            self.setObjectParams(obj_item, params)
        elif type == 'Time':
            obj_item = self.addTimeAnnotation()
            self.setObjectParams(obj_item, params)

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
        self.WindowResult.append(ann)
        self.WindowResult.update()
        return item

    def addImageAnnotation(self):
        item = self.addGroup(self.PARAMS_IMAGE, spanned = False)
        params = self.itemParams(item)
        item.setText("[image]")

        map = annotations.AnnotationImage.MAP
        kwargs = common.remap(params, map)
        ann = chigger.annotations.ImageAnnotation(**kwargs)
        item.setData((ann[0], map))
        self.WindowResult.append(ann)
        self.WindowResult.update()
        return item

    def addTimeAnnotation(self):
        item = self.addGroup(self.PARAMS_TIME, spanned = False)
        params = self.itemParams(item)
        item.setText("[time]")

        map = annotations.AnnotationTime.MAP
        kwargs = common.remap(params, map)
        kwargs['text'] = common.formatTimeStr(kwargs['format'], common.t)
        ann = chigger.annotations.TextAnnotation(**kwargs)
        item.setData((ann[0], map))
        self.WindowResult.append(ann)
        self.WindowResult.update()
        return item

    def onTimeChanged(self, time):
        self.updateTimeAnnotations()

    def onTimeUnitChanged(self, time):
        self.updateTimeAnnotations()

    def updateTimeAnnotations(self):
        for row in range(self.Model.rowCount()):
            item = self.Model.item(row, 0)
            if item.text() == '[time]':
                ann, map = item.data()
                # TODO: get this from the parameter
                format_str = None
                text = common.formatTimeStr(format_str, common.t)
                ann.setOption('text', text)
        self.WindowResult.update()
