import sys
import signal
from PyQt5 import QtWidgets, QtCore
from .MeshInspectorPlugin import MeshInspectorPlugin


def safe_timer(timeout, func, *args, **kwargs):
    """Create a timer that is safe against garbage collection and
    overlapping calls.
    See: http://ralsina.me/weblog/posts/BB974.html
    """
    def timer_event():
        try:
            func(*args, **kwargs)
        finally:
            QtCore.QTimer.singleShot(timeout, timer_event)
    QtCore.QTimer.singleShot(timeout, timer_event)


def handle_sigint(signum, frame):
    QtWidgets.QApplication.quit()


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.menubar = QtWidgets.QMenuBar(self)
        self.plugin = None

    def closeEvent(self, event):
        self.plugin.close()
        event.accept()


def main():
    QtCore.QCoreApplication.setAttribute(
        QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    signal.signal(signal.SIGINT, handle_sigint)

    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    window = MainWindow()
    plugin = MeshInspectorPlugin(window)
    window.plugin = plugin
    plugin.create()
    # Repeatedly run python-noop to give the interpreter time to
    # handle signals
    safe_timer(50, lambda: None)

    app.exec()

    del app


if __name__ == '__main__':
    main()
