import vtk
from PyQt5 import QtCore, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class MeshWindow(QtWidgets.QMainWindow):
    """
    Window for displaying the mesh
    """

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

        self._frame = QtWidgets.QFrame(self)
        self._vtk_widget = QVTKRenderWindowInteractor(self._frame)

        self._vtk_renderer = vtk.vtkRenderer()
        self._vtk_widget.GetRenderWindow().AddRenderer(self._vtk_renderer)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._vtk_widget)

        self._frame.setLayout(self._layout)

        self.setCentralWidget(self._frame)
        self.setWindowTitle("Mesh")

        self._vtk_render_window = self._vtk_widget.GetRenderWindow()
        self._vtk_interactor = self._vtk_render_window.GetInteractor()

        self._vtk_interactor.SetInteractorStyle(vtk.vtkInteractorStyleImage())

        # TODO: set background from preferences/templates
        self._vtk_renderer.SetGradientBackground(True)
        self._vtk_renderer.SetBackground([0.2, 0.2, 0.2])
        self._vtk_renderer.SetBackground2([0.4, 0.4, 0.4])
        # set anti-aliasing on
        self._vtk_renderer.SetUseFXAA(True)
        self._vtk_render_window.SetMultiSamples(1)

        self._vtk_widget.AddObserver('StartInteractionEvent',
                                     self.onStartInteraction)
        self._vtk_widget.AddObserver('EndInteractionEvent',
                                     self.onEndInteraction)

        self._vtk_interactor.Initialize()
        self._vtk_interactor.Start()

        self.show()

    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.plugin.updateMenuBar()
        return super().event(event)

    def onStartInteraction(self, obj, event):
        pass

    def onEndInteraction(self, obj, event):
        pass
