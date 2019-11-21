import chigger
from . import common


class AnnotationText(object):
    """
    Text annotation object
    """
    MAP = {
        'font-size': 'font_size',
        'halign': 'justification',
        'valign': 'vertical_justification',
        'color': 'text_color',
        'opacity': 'text_opacity',
        'shadow': 'text_shadow'
    }

    def __init__(self, annotation):
        kwargs = common.remap(annotation, self.MAP)
        self.text = chigger.annotations.TextAnnotation(**kwargs);

    def result(self):
        return self.text

    def update(self, time):
        pass


class AnnotationTime(AnnotationText):
    """
    Time annotation object
    """

    def __init__(self, annotation):
        if 'format' in annotation:
            self.format_str = annotation.pop('format')
        else:
            self.format_str = '{:1.2f}'
        annotation['text'] = self.getTimeText(common.t)
        super(AnnotationTime, self).__init__(annotation)

    def update(self, time):
        self.text.setOptions(text = self.getTimeText(time))

    def getTimeText(self, time):
        return common.formatTimeStr(self.format_str, time)



class AnnotationImage(object):
    """
    Image annotation object
    """
    MAP = {
        'file': 'filename',
        'halign': 'horizontal_alignment',
        'valign': 'vertical_alignment'
    }

    def __init__(self, annotation):
        kwargs = common.remap(annotation, self.MAP)
        self.image = chigger.annotations.ImageAnnotation(**kwargs)

    def result(self):
        return self.image

    def update(self, time):
        pass


def __buildAnnotation(annotation):
    """
    Take an annotation structure and build an object from it
    """
    cls_name = 'Annotation' + annotation['type']
    if cls_name in globals():
        cls = globals()[cls_name]
        del annotation['type']
        return cls(annotation)
    else:
        return None


def process(annotations):
    """
    Go over the annotation array and build individual objects
    """
    objs = []
    for annotation in annotations:
        if 'type' in annotation:
            obj = __buildAnnotation(annotation)
            if obj != None:
                objs.append(obj)
        else:
            print("No 'type' defined in annotation. Skipping...")
    return objs
