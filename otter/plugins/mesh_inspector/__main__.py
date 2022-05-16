import sys
import signal
import argparse
from PyQt5 import QtWidgets, QtCore
from otter.assets import Assets
from otter.plugins.mesh_inspector.MeshInspectorPlugin import \
    MeshInspectorPlugin

parser = argparse.ArgumentParser(description='Mesh inspector')
parser.add_argument(
    'mesh_file',
    metavar='file',
    type=str,
    nargs='?',
    help='Mesh file to display')
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

    plugin = MeshInspectorPlugin(None)
    plugin.create()
    # Repeatedly run python-noop to give the interpreter time to
    # handle signals
    safe_timer(50, lambda: None)

    if args.mesh_file is not None:
        plugin.loadFile(args.mesh_file)
    app.exec()


if __name__ == '__main__':
    main()
