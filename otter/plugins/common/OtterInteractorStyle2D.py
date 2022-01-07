import vtk
from otter.plugins.common.OtterInteractorInterface import \
    OtterInteractorInterface


class OtterInteractorStyle2D(vtk.vtkInteractorStyleImage,
                             OtterInteractorInterface):

    def __init__(self, widget):
        vtk.vtkInteractorStyleImage.__init__(self)
        OtterInteractorInterface.__init__(self, widget)

    def onLeftButtonPress(self, interactor_style, event):
        super().onLeftButtonPress(interactor_style, event)
        super().OnLeftButtonDown()

    def onLeftButtonRelease(self, interactor_style, event):
        super().onLeftButtonRelease(interactor_style, event)
        super().OnLeftButtonUp()
