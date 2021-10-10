import sys
import signal
from PyQt5 import QtWidgets, QtCore
from mesh_inspector.MeshInspectorPlugin import MeshInspectorPlugin


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


class PluginApp(QtWidgets.QApplication):

    def __init__(self, plugin, argv):
        super().__init__(argv)
        self._plugin = plugin

    def event(self, e):
        if e.type() == QtCore.QEvent.Close:
            self._plugin.close()
        return super().event(e)


def main():
    QtCore.QCoreApplication.setAttribute(
        QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    plugin = MeshInspectorPlugin()
    app = PluginApp(plugin, sys.argv)
    app.setQuitOnLastWindowClosed(True)

    signal.signal(signal.SIGINT, handle_sigint)
    plugin.create()

    # Repeatedly run python-noop to give the interpreter time to
    # handle signals
    safe_timer(50, lambda: None)

    app.exec()

    del app


if __name__ == '__main__':
    main()
