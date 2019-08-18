import vtk
from chigger.observers.ChiggerObserver import ChiggerObserver
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot

class OtterWindowModifiedObserver(ChiggerObserver, QObject):
    """
    Class for observing window changes
    """

    resized = pyqtSignal(int, int)

    @staticmethod
    def getOptions():
        opt = ChiggerObserver.getOptions()
        return opt

    def __init__(self, **kwargs):
        super(OtterWindowModifiedObserver, self).__init__(vtk.vtkCommand.ModifiedEvent, **kwargs)

    def addObserver(self, event, vtkinteractor):
        self.size = self._window.getVTKWindow().GetSize()
        return vtkinteractor.AddObserver(event, self._callback)

    def update(self, **kwargs):
        """
        Update the window object.
        """
        super(OtterWindowModifiedObserver, self).update(**kwargs)
        if self._window.needsUpdate():
            self._window.update()

    def _callback(self, obj, event): #pylint: disable=unused-argument
        """
        The function to be called by the RenderWindow.

        Inputs:
            obj, event: Required by VTK.
        """
        sz = self._window.getVTKWindow().GetSize()
        if self.size != sz:
            self.size = sz
            self.resized.emit(sz[0], sz[1])
