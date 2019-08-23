from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QFrame
from PyQt5.QtCore import QEvent, pyqtSignal, pyqtSlot
import chigger
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class RetinaQVTKRenderWindowInteractor(QVTKRenderWindowInteractor):
    """
    Currently VTK7.1 and Qt5 do not work correctly on retina displays:
    http://public.kitware.com/pipermail/vtk-developers/2017-February/034738.html

    However, creating a custom resizeEvent method and wrapping the QVTKRenderWindowInteractor object
    in a QFrame allowed it to work for now. The idea for this wrapping came from:
        https://github.com/siudej/Eigenvalues/blob/master/qvtk.py
    """
    def resizeEvent(self, event):
        """
        Double the size on retina displays.
        This is not the right way to do it, but this works for framed widgets.
        We also need to modify all mouse events to adjust the interactor's
        center (e.g. for joystick mode).
        """
        super(RetinaQVTKRenderWindowInteractor, self).resizeEvent(event)

        ratio = self.devicePixelRatio()
        w = self.width()
        h = self.height()
        if (self.parent() is not None) and (w <= self.parent().width()):
            self.resize(ratio*self.size())
        self.GetRenderWindow().SetSize(ratio*w, ratio*h)
        self.GetRenderWindow().GetInteractor().SetSize(ratio*w, ratio*h)
        self.GetRenderWindow().GetInteractor().ConfigureEvent()
        self.update()


class OtterResultWindow(QMainWindow):

    resized = pyqtSignal(int, int)

    def __init__(self, parent = None):
        super(OtterResultWindow, self).__init__(parent)

        self.frame = QFrame()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.vtkWidget = RetinaQVTKRenderWindowInteractor(self.frame)
        self.layout.addWidget(self.vtkWidget)

        args = {}
        args['vtkinteractor'] = self.vtkWidget
        args['vtkwindow'] = self.vtkWidget.GetRenderWindow()
        self.chiggerWindow = chigger.RenderWindow(*[], **args)

        self.frame.setLayout(self.layout)
        self.setCentralWidget(self.frame)
        self.setWindowTitle("Result")
        self.show()

        self.chiggerWindow.update()

    def setParam(self, name, param):
        self.chiggerWindow.setOption(name, param)
        self.chiggerWindow.update()

    def update(self):
        self.chiggerWindow.update()

    def append(self, chigger_object):
        self.chiggerWindow.append(chigger_object)

    def event(self, event):
        if (event.type() == QEvent.WindowActivate):
            self.parentWidget().updateMenuBar()
        return super(OtterResultWindow, self).event(event);

    def resizeEvent(self, event):
        self.resized.emit(event.size().width(), event.size().height())
        return super(OtterResultWindow, self).resizeEvent(event)
