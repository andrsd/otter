#!/usr/bin/env python2

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeView, QMenu
from OtterObjectsTab import OtterObjectsTab

class OtterViewportsTab(OtterObjectsTab):

    EXODUS = 0
    RELAP7_RESULT = 1
    PLOT_OVER_TIME = 2
    VPP_PLOT = 3

    def __init__(self, parent):
        super(OtterViewportsTab, self).__init__(parent)

    def name(self):
        return "VPs"

    def buildAddButton(self):
        btn = QPushButton("Add", self)
        mnu = QMenu("Add", self)
        mnu.addAction("Exodus result", lambda : self.onAdd(self.EXODUS))
        mnu.addAction("RELAP-7 result", lambda : self.onAdd(self.RELAP7_RESULT))
        mnu.addAction("Plot over time", lambda : self.onAdd(self.PLOT_OVER_TIME))
        mnu.addAction("VPP Plot", lambda : self.onAdd(self.VPP_PLOT))
        btn.setMenu(mnu)
        return btn

    def onAdd(self, type):
        pass

    def toText(self):
        str = ""
        str += "viewports = [\n"
        str += "]\n"

        return str
