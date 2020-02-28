from PyQt5 import QtCore, QtWidgets, QtGui

def toPython(value):
    """
    Convert 'value' to a python "object"
    """

    if isinstance(value, bool):
        return value
    elif len(value) == 0:
        return None
    elif value[0] == '[' and value[-1] == ']':
        value = value[1:-1]
        if len(value) > 0:
            str_array = [x.strip() for x in value.split(',')]
            arr = []
            for val in str_array:
                try:
                    tmp = int(val)
                    arr.append(tmp)
                except ValueError:
                    arr.append(float(val))
            return arr
        else:
            return []
    elif value[0] == '(' and value[-1] == ')':
        value = value[1:-1]
        if len(value) > 0:
            str_array = [x.strip() for x in value.split(',')]
            arr = []
            for val in str_array:
                try:
                    tmp = int(val)
                    arr.append(tmp)
                except ValueError:
                    arr.append(float(val))
            return arr
        else:
            return []
    else:
        try:
            return int(value)
        except ValueError:
            return value


class OtterLineEdit(QtWidgets.QLineEdit):

    def __init__(self, parent, tree_view):
        super(OtterLineEdit, self).__init__(parent)
        self._tree_view = tree_view

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Up:
            self._tree_view.commitData(self)
            self._tree_view.closeEditor(self, QtWidgets.QAbstractItemDelegate.EditPreviousItem)

        if e.key() == QtCore.Qt.Key_Down:
            self._tree_view.commitData(self)
            self._tree_view.closeEditor(self, QtWidgets.QAbstractItemDelegate.EditNextItem)

        super(OtterLineEdit, self).keyPressEvent(e)


class OtterParamDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent):
        super(OtterParamDelegate, self).__init__(parent)
        self._tree_view = parent

    def createEditor(self, parent, option, index):
        model = index.model()
        data = model.itemFromIndex(index).data()
        if isinstance(data, OtterParamBase):
            return data.createEditor(parent, self._tree_view)
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

    def createEditor(self, parent, tree_view):
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

    def createEditor(self, parent, tree_view):
        editor = OtterLineEdit(parent, tree_view)
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

    def createEditor(self, parent, tree_view):
        btn = QtWidgets.QPushButton("...")
        btn.setMaximumWidth(20)
        btn.clicked.connect(self.onFileSelect)

        editor = OtterLineEdit(parent, tree_view)

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
