from PyQt5 import QtCore, QtWidgets
import chigger
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

VTK_MAJOR_VERSION = vtk.vtkVersion.GetVTKMajorVersion()

class RetinaQVTKRenderWindowInteractor(QVTKRenderWindowInteractor):
    """
    Currently VTK7.1 and Qt5 do not work correctly on retina displays:
    http://public.kitware.com/pipermail/vtk-developers/2017-February/034738.html

    However, creating a custom resizeEvent method and wrapping the QVTKRenderWindowInteractor object
    in a QtWidgets.QFrame allowed it to work for now. The idea for this wrapping came from:
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


class OtterResultWindow(QtWidgets.QMainWindow):

    resized = QtCore.pyqtSignal(int, int)

    def __init__(self, parent = None):
        super(OtterResultWindow, self).__init__(parent)

        self.Frame = QtWidgets.QFrame()
        self.Layout = QtWidgets.QVBoxLayout()
        self.Layout.setContentsMargins(0, 0, 0, 0)

        if VTK_MAJOR_VERSION < 8:
            self.vtk_widget = RetinaQVTKRenderWindowInteractor(self.Frame)
        else:
            self.vtk_widget = QVTKRenderWindowInteractor(self.Frame)
        self.vtk_window = self.vtk_widget.GetRenderWindow()
        self.Layout.addWidget(self.vtk_widget)

        args = {}
        args['vtkinteractor'] = self.vtk_widget
        args['vtkwindow'] = self.vtk_window
        args['layer'] = 0
        self.chigger_window = chigger.RenderWindow(*[], **args)

        self.Frame.setLayout(self.Layout)
        self.setCentralWidget(self.Frame)
        self.setWindowTitle("Result")
        self.show()

        self.chigger_window.update()

    def setParam(self, name, param):
        self.chigger_window.setOption(name, param)
        self.chigger_window.update()

    def update(self):
        self.chigger_window.update()

    def append(self, chigger_object):
        self.chigger_window.append(chigger_object)

    def remove(self, chigger_object):
        # NOTE: cannot use RenderWindow.remove(), becuase it handles only results
        self.chigger_window.setNeedsUpdate(True)
        vtk_renderer = chigger_object._vtkrenderer
        vtk_actor = chigger_object._vtkactor
        vtk_renderer.RemoveActor(vtk_actor)
        if self.vtk_window.HasRenderer(vtk_renderer):
            self.vtk_window.RemoveRenderer(vtk_renderer)
        if chigger_object in self.chigger_window._results:
            self.chigger_window._results.remove(chigger_object)

    def write(self, file_name):
        self.chigger_window.write(file_name)

    def event(self, event):
        if (event.type() == QtCore.QEvent.WindowActivate):
            self.parentWidget().updateMenuBar()
        return super(OtterResultWindow, self).event(event);

    def resizeEvent(self, event):
        self.resized.emit(event.size().width(), event.size().height())
        return super(OtterResultWindow, self).resizeEvent(event)
