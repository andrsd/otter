from PyQt5 import QtWidgets, QtCore

"""
List of recent file that show on the MainWindow
"""
class TemplatesTab(QtWidgets.QWidget):

    def __init__(self, parent):
        super(TemplatesTab, self).__init__(parent)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 0)

        self.TemplateList = QtWidgets.QListView(self)
        self.TemplateList.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        main_layout.addWidget(self.TemplateList)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.NewButton = QtWidgets.QPushButton("New", self)
        self.NewButton.setContentsMargins(0, 0, 10, 0)
        button_layout.addWidget(self.NewButton)

        button_layout.addStretch()

        self.OpenButton = QtWidgets.QPushButton("Open", self)
        button_layout.addWidget(self.OpenButton)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.NewButton.clicked.connect(self.onNew)
        self.OpenButton.clicked.connect(self.onOpen)

        self.updateWidgets()

    def updateWidgets(self):
        if len(self.TemplateList.selectedIndexes()) == 1:
            self.OpenButton.setEnabled()
        else:
            self.OpenButton.setEnabled(False)

    def onNew(self):
        pass

    def onOpen(self):
        pass
