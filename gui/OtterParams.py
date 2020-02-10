from PyQt5 import QtCore, QtWidgets, QtGui

class OtterParamDelegate(QtWidgets.QStyledItemDelegate):
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
            value = model.data(index, QtCore.Qt.EditRole)
            data.setEditorData(editor, value)
        else:
            super(OtterParamDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        data = model.itemFromIndex(index).data()
        if isinstance(data, OtterParamBase):
            value = data.value(editor)
            model.setData(index, value, QtCore.Qt.EditRole)
        else:
            super(OtterParamDelegate, self).setModelData(editor, model, index)

    def updateEditorGeometry(self, editor, option, index):
        model = index.model()
        data = model.itemFromIndex(index).data()
        if isinstance(data, OtterParamBase):
            data.setGeometry(editor, option.rect)
        else:
            super(OtterParamDelegate, self).updateEditorGeometry(editor, option, index)


class OtterParamBase(object):
    """
    Base class for Otter parameter delegates
    """
    def __init__(self):
        pass


class OtterParamOptions(OtterParamBase):
    """
    Delegate for selecting options via QtWidgets.QComboBox
    """

    def __init__(self, options):
        super(OtterParamOptions, self).__init__()
        self.options = options

    def createEditor(self, parent):
        editor = QtWidgets.QComboBox(parent)
        for opt in self.options:
            editor.addItem(opt)
        return editor

    def setEditorData(self, editor, value):
        editor.setCurrentIndex(editor.findText(value))

    def value(self, editor):
        return editor.currentText()

    def setGeometry(self, editor, rect):
        rect.setTop(rect.top() - 2)
        rect.setBottom(rect.bottom() + 3)
        editor.setGeometry(rect)


class OtterParamLineEdit(OtterParamBase):
    def __init__(self, type, limits = None):
        super(OtterParamLineEdit, self).__init__()
        self.type = type
        self.limits = limits

    def createEditor(self, parent):
        editor = QtWidgets.QLineEdit(parent)
        if self.limits != None:
            if self.type == 'int':
                validator = QtGui.QIntValidator()
                if self.limits[0] != None:
                    validator.setBottom(self.limits[0])
                if self.limits[1] != None:
                    validator.setTop(self.limits[1])
                editor.setValidator(validator)
            elif self.type == 'float':
                validator = QtGui.QDoubleValidator()
                if self.limits[0] != None:
                    validator.setBottom(self.limits[0])
                if self.limits[1] != None:
                    validator.setTop(self.limits[1])
                editor.setValidator(validator)
            elif self.type == 'str':
                validator = QtGui.QRegExpValidator(QtCore.QRegExp(self.limits))
                editor.setValidator(validator)
            else:
                pass

        return editor

    def setEditorData(self, editor, value):
        editor.setText(value)

    def value(self, editor):
        return editor.text()

    def setGeometry(self, editor, rect):
        editor.setGeometry(rect)


class OtterParamFilePicker(OtterParamBase):
    def __init__(self, load_save):
        super(OtterParamFilePicker, self).__init__()
        self.type = load_save
        self.editor = None

    def createEditor(self, parent):
        btn = QtWidgets.QPushButton("...")
        btn.setMaximumWidth(20)
        btn.clicked.connect(self.onFileSelect)

        editor = QtWidgets.QLineEdit(parent)

        layout = QtWidgets.QHBoxLayout()
        layout.addStretch()
        layout.addWidget(btn)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        editor.setLayout(layout)
        self.editor = editor

        return editor

    def setEditorData(self, editor, value):
        editor.setText(value)

    def value(self, editor):
        return editor.text()

    def setGeometry(self, editor, rect):
        editor.setGeometry(rect)

    def onFileSelect(self):
        if self.type == 'open':
            file_names = QtWidgets.QFileDialog.getOpenFileName(None, 'Select a File')
            if file_names[0]:
                self.editor.setText(file_names[0])
        elif self.type == 'save':
            file_names = QtWidgets.QFileDialog.getSaveFileName(None, 'Select a File')
            if file_names[0]:
                self.editor.setText(file_names[0])
        else:
            print("Unknow type in OtterParamFilePicker.")
