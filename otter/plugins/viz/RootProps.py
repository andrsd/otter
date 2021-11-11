from otter.plugins.viz.PropsBase import PropsBase


class RootProps(PropsBase):
    """
    Properties page to display when root is selected
    """

    def __init__(self, renderer, parent=None):
        super().__init__(parent)
        self._vtk_renderer = renderer
        self.setupWidgets()

        self._vtk_renderer.SetGradientBackground(True)
        self._vtk_renderer.SetBackground([0.321, 0.3411, 0.4313])
        self._vtk_renderer.SetBackground2([0.321, 0.3411, 0.4313])

    def setupWidgets(self):
        self._layout.addStretch()
