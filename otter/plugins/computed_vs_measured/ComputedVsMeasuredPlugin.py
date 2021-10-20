"""
ComputedVsMeasuredPlugin.py
"""

from otter.plugins.Plugin import Plugin
from otter.assets import Assets
from otter.plugins.computed_vs_measured.ComputedVsMeasuredWindow \
    import ComputedVsMeasuredWindow


class ComputedVsMeasuredPlugin(Plugin):
    """
    Plug-in for plotting computed vs measured data
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.window = None

    @staticmethod
    def name():
        return "Computed vs. Measured"

    @staticmethod
    def icon():
        return Assets().icons['graph']

    def onCreate(self):
        self.window = ComputedVsMeasuredWindow(self)
        if self.parent is not None and hasattr(self.parent, 'window_menu'):
            if hasattr(self.window, 'menuBar'):
                self.window.menuBar().addMenu(self.parent.window_menu)
        self.registerWindow(self.window)

    def onClose(self):
        self.window.close()
