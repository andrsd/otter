from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QItemDelegate


class OtterParamDelegate(QItemDelegate):
    def __init__(self, parent):
        super(OtterParamDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        model = index.model()
        data = model.itemFromIndex(index).data()
        if isinstance(data, OtterParamBase):
            return data.createEditor(parent)
        else:
            return super(OtterParamDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        model = index.model()
        data = model.itemFromIndex(index).data()
        if isinstance(data, OtterParamBase):
            value = model.data(index, Qt.EditRole)
            data.setEditorData(editor, value)
        else:
            return super(OtterParamDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        data = model.itemFromIndex(index).data()
        if isinstance(data, OtterParamBase):
            value = data.setModelData(editor)
            model.setData(index, value, Qt.EditRole)
        else:
            return super(OtterParamDelegate, self).setModelData(editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        model = index.model()
        data = model.itemFromIndex(index).data()
        if isinstance(data, OtterParamBase):
            data.setGeometry(editor, option.rect)
        else:
            return super(OtterParamDelegate, self).updateEditorGeometry(editor, option, index)


class OtterParamBase(object):
    """
    Base class for Otter parameter delegates
    """
    def __init__(self):
        pass


class OtterParamOptions(OtterParamBase):
    """
    Delegate for selecting options via QComboBox
    """

    def __init__(self, options):
        super(OtterParamOptions, self).__init__()
        self.options = options

    def createEditor(self, parent):
        editor = QComboBox(parent)
        for opt in self.options:
            editor.addItem(opt)
        return editor

    def setEditorData(self, editor, value):
        editor.setCurrentIndex(editor.findText(value))

    def setModelData(self, editor):
        return editor.currentText()

    def setGeometry(self, editor, rect):
        rect.setTop(rect.top() - 2)
        rect.setBottom(rect.bottom() + 3)
        return editor.setGeometry(rect)
