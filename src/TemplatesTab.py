from PyQt5 import QtWidgets, QtCore
from OListView import OListView

"""
List of recent file that show on the MainWindow
"""
class TemplatesTab(QtWidgets.QWidget):

    def __init__(self, parent):
        super(TemplatesTab, self).__init__(parent)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 0)

        self.template_list = OListView(self)
        self.template_list.setEmptyMessage("No templates")
        self.template_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        main_layout.addWidget(self.template_list)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.new_button = QtWidgets.QPushButton("New", self)
        self.new_button.setContentsMargins(0, 0, 10, 0)
        button_layout.addWidget(self.new_button)

        button_layout.addStretch()

        self.open_button = QtWidgets.QPushButton("Open", self)
        button_layout.addWidget(self.open_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.new_button.clicked.connect(self.onNew)
        self.open_button.clicked.connect(self.onOpen)

        self.updateWidgets()

    def updateWidgets(self):
        if len(self.template_list.selectedIndexes()) == 1:
            self.open_button.setEnabled()
        else:
            self.open_button.setEnabled(False)

    def onNew(self):
        pass

    def onOpen(self):
        pass
