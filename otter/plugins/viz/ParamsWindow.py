from PyQt5 import QtWidgets, QtCore


class ParamsWindow(QtWidgets.QScrollArea):
    """
    Window for entering parameters
    """

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

        layout = self.setupWidgets()

        w = QtWidgets.QWidget()
        w.setLayout(layout)
        self.setWidget(w)
        self.setWindowTitle("Parameters")
        self.setMinimumWidth(350)
        self.setWidgetResizable(True)
        self.setWindowFlags(QtCore.Qt.Tool)

        geom = self.plugin.settings.value("info/geometry")
        default_size = QtCore.QSize(350, 700)
        if geom is None:
            self.resize(default_size)
        else:
            if not self.restoreGeometry(geom):
                self.resize(default_size)

        self.show()

    def setupWidgets(self):
        layout = QtWidgets.QVBoxLayout()
        return layout

    def event(self, event):
        """
        Event callback
        """
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

    def closeEvent(self, event):
        self.plugin.settings.setValue("info/geometry", self.saveGeometry())
        event.accept()
