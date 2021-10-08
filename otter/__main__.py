import sys
import os
import signal
from PyQt5 import QtWidgets, QtCore
from otter import consts
from otter.MainWindow import MainWindow
from otter.assets import Assets


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


def handle_uncaught_exception(exc_type, exc, traceback):
    print('Unhandled exception', exc_type, exc, traceback)
    QtWidgets.QApplication.quit()


sys.excepthook = handle_uncaught_exception


def main():
    home_dir = QtCore.QStandardPaths.writableLocation(
        QtCore.QStandardPaths.HomeLocation)
    os.chdir(home_dir)

    QtCore.QCoreApplication.setOrganizationName("David Andrs")
    QtCore.QCoreApplication.setOrganizationDomain("name.andrs")
    QtCore.QCoreApplication.setApplicationName(consts.APP_NAME)

    QtCore.QCoreApplication.setAttribute(
        QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    qapp = QtWidgets.QApplication(sys.argv)
    qapp.setQuitOnLastWindowClosed(False)
    qapp.setWindowIcon(Assets().icons['app'])
    qapp.setQuitOnLastWindowClosed(False)

    otter_dir = os.path.dirname(os.path.realpath(__file__))

    window = MainWindow()
    signal.signal(signal.SIGINT, handle_sigint)
    window.setPluginsDir(os.path.join(otter_dir, "plugins"))
    window.loadPlugins()
    window.show()

    # Repeatedly run python-noop to give the interpreter time to
    # handle signals
    safe_timer(50, lambda: None)

    qapp.exec()


if __name__ == '__main__':
    main()
