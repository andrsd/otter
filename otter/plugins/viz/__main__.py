import sys
import signal
import argparse
from PyQt5 import QtWidgets, QtCore
from otter.assets import Assets
from otter.plugins.viz.VizPlugin import VizPlugin

parser = argparse.ArgumentParser(description='Visualizer')
parser.add_argument(
    'file',
    metavar='file',
    type=str,
    nargs='?',
    help='File to open')
args = parser.parse_args()


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


def main():
    QtCore.QCoreApplication.setAttribute(
        QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    signal.signal(signal.SIGINT, handle_sigint)

    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    app.setWindowIcon(Assets().icons['app'])

    plugin = VizPlugin(None)
    plugin.create()
    # Repeatedly run python-noop to give the interpreter time to
    # handle signals
    safe_timer(50, lambda: None)

    if args.file is not None:
        plugin.loadFile(args.file)
    app.exec()


if __name__ == '__main__':
    main()
