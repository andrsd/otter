import vtk
from PyQt5 import QtCore, QtGui


class OtterInteractorStyle2D(vtk.vtkInteractorStyleImage):

    def __init__(self, widget):
        super().__init__()
        self._widget = widget
        self._last_mouse_pos = None
        self._left_button_down = False

        self.AddObserver("LeftButtonPressEvent", self.onLeftButtonPress)
        self.AddObserver("LeftButtonReleaseEvent", self.onLeftButtonRelease)
        # self.AddObserver("KeyReleaseEvent", self.onKeyReleased, 1000)
        self.AddObserver("KeyPressEvent", self.onKeyPress)
        self.AddObserver("KeyReleaseEvent", self.onKeyRelease)
        self.AddObserver("CharEvent", self.onChar)

    def onLeftButtonPress(self, interactor_style, event):
        self._left_button_down = True
        interactor = interactor_style.GetInteractor()
        click_pos = interactor.GetEventPosition()
        pt = QtCore.QPoint(click_pos[0], click_pos[1])
        self._last_mouse_pos = pt
        super().OnLeftButtonDown()

    def onLeftButtonRelease(self, interactor_style, event):
        self._left_button_down = False
        interactor = interactor_style.GetInteractor()
        click_pos = interactor.GetEventPosition()
        pt = QtCore.QPoint(click_pos[0], click_pos[1])
        if self._last_mouse_pos == pt:
            self._widget.onClicked(pt)
        super().OnLeftButtonUp()

    def onKeyPress(self, interactor_style, event):
        interactor = interactor_style.GetInteractor()
        key = interactor.GetKeyCode()
        seq = QtGui.QKeySequence(key)
        # FIXME: get the modifiers from interactor
        mods = QtCore.Qt.NoModifier
        if len(seq) > 0:
            e = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, seq[0], mods)
            QtCore.QCoreApplication.postEvent(self._widget, e)

    def onKeyRelease(self, interactor_style, event):
        # interactor = interactor_style.GetInteractor()
        pass

    def onChar(self, interactor_style, event):
        # interactor = interactor_style.GetInteractor()
        pass
