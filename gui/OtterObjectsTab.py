#!/usr/bin/env python2

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu

class OtterObjectsTab(QWidget):

    VIEWPORTS = 0
    COLORBARS = 1
    ANNOTATIONS = 2

    VIEWPORT_EXODUS = 0
    VIEWPORT_RELAP7_RESULT = 1
    VIEWPORT_PLOT_OVER_TIME = 2
    VIEWPORT_VPP_PLOT = 3

    ANN_TEXT = 0
    ANN_IMAGE = 1
    ANN_TIME = 2

    def __init__(self, parent, type):
        super(OtterObjectsTab, self).__init__(parent)

        self.type = type

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 3)
        self.setLayout(layout)

        btn = self.buildAddButton()
        layout.addWidget(btn)

        self.ctlObjects = QTreeView(self)
        layout.addWidget(self.ctlObjects)

    def name(self):
        if self.type == self.VIEWPORTS:
            return "VPs"
        elif self.type == self.COLORBARS:
            return "CBs"
        elif self.type == self.ANNOTATIONS:
            return "ANs"
        else:
            raise SystemExit("Unknown type of OtterObjectsTab")

    def buildAddButton(self):
        if self.type == self.VIEWPORTS:
            return self.buildAddViewport()
        elif self.type == self.COLORBARS:
            return self.buildAddColorbars()
        elif self.type == self.ANNOTATIONS:
            return self.buildAddAnnotations()
        else:
            raise SystemExit("Unknown type of OtterObjectsTab")

    def buildAddViewport(self):
        btn = QPushButton("Add", self)
        mnu = QMenu("Add", self)
        mnu.addAction("Exodus result", lambda : self.onAddViewport(self.VIEWPORT_EXODUS))
        mnu.addAction("RELAP-7 result", lambda : self.onAddViewport(self.VIEWPORT_RELAP7_RESULT))
        mnu.addAction("Plot over time", lambda : self.onAddViewport(self.VIEWPORT_PLOT_OVER_TIME))
        mnu.addAction("VPP Plot", lambda : self.onAddViewport(self.VIEWPORT_VPP_PLOT))
        btn.setMenu(mnu)
        return btn

    def buildAddColorbars(self):
        btn = QPushButton("Add", self)
        btn.clicked.connect(self.onAddColorBar)
        return btn

    def buildAddAnnotations(self):
        btn = QPushButton("Add", self)
        mnu = QMenu("Add", self)
        mnu.addAction("Text", lambda : self.onAddAnnotation(self.ANN_TEXT))
        mnu.addAction("Image", lambda : self.onAddAnnotation(self.ANN_IMAGE))
        mnu.addAction("Time", lambda : self.onAddAnnotation(self.ANN_TIME))
        btn.setMenu(mnu)
        return btn



    def onAddViewport(self, type):
        print "Add viewport", type
        pass

    def onAddColorBar(self):
        print "Add colorbar"
        pass

    def onAddAnnotation(self, type):
        print "Add annotation", type
        pass
