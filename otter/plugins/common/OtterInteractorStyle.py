import vtk
from PyQt5 import QtCore


class OtterInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, widget):
        super().__init__()
        self._widget = widget
        self._last_mouse_pos = None
        self._left_button_down = False

        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonPress)
        self.AddObserver("LeftButtonReleaseEvent", self.onLeftButtonRelease)
        self.AddObserver("MouseMoveEvent", self.onMouseMove)

    def onLeftButtonPress(self, interactor_style, event):
        self._left_button_down = True
        interactor = interactor_style.GetInteractor()
        click_pos = interactor.GetEventPosition()
        pt = QtCore.QPoint(click_pos[0], click_pos[1])
        self._last_mouse_pos = pt

    def onLeftButtonRelease(self, interactor_style, event):
        self._left_button_down = False
        interactor = interactor_style.GetInteractor()
        click_pos = interactor.GetEventPosition()
        pt = QtCore.QPoint(click_pos[0], click_pos[1])

        if self._last_mouse_pos == pt:
            self._widget.onClicked(pt)

    def onMouseMove(self, interactor_style, event):
        interactor = interactor_style.GetInteractor()
        if self._left_button_down:
            if interactor.GetShiftKey():
                # do pan
                pass
            else:
                # do rotate
                pass
