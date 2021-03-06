"""
Otter
"""
# pylint: disable=invalid-name

import sys
import os
import argparse
import signal
import importlib.util
import consts

# pylint: disable=invalid-name
otter_dir = None

def check_requirements():
    """
    Check that all packages we are using are present. If not, let users know.
    """
    stop = False

    # check system packages
    modules = [ 'PyQt5', 'vtk', 'numpy', 'bisect', "yaml"]
    not_found_modules = []
    for m in modules:
        if importlib.util.find_spec(m) is None:
            not_found_modules.append(m)

    if len(not_found_modules) > 0:
        print("The following modules were not found: {}. "
            "This may be fixed by installing them either "
            "via 'pip' or 'conda'.".format(", ".join(not_found_modules)))
        stop = True

    # check MOOSE packages
    moose_modules = ['mooseutils', 'chigger']
    not_found_modules = []
    for m in moose_modules:
        if importlib.util.find_spec(m) is None:
            not_found_modules.append(m)

    if len(not_found_modules) > 0:
        print("The following modules were not found: {}. "
            "This may be fixed by setting MOOSE_DIR environment "
            "variable.".format(", ".join(not_found_modules)))
        stop = True

    if stop:
        sys.exit(1)

def set_paths():
    """
    Set paths required for running
    """
    # pylint: disable=global-statement
    global otter_dir

    otter_dir = os.path.dirname(os.path.realpath(__file__))
    moose_dir = os.environ.get("MOOSE_DIR", None)
    if moose_dir is None:
        app_dir = os.path.dirname(otter_dir)
        moose_dir = os.path.join(app_dir, "moose")
    chigger_dir = os.path.join(moose_dir, "python", "chigger")

    sys.path.append(os.path.join(moose_dir, "python"))
    sys.path.append(chigger_dir)
    sys.path.append(otter_dir)


def run():
    """
    Run the application
    """
    # pylint: disable=global-statement
    global otter_dir

    parser = argparse.ArgumentParser(
        description = 'GUI for MOOSE\'s chigger.'
    )
    parser.add_argument(
        'file',
        nargs = '?',
        default = None,
        help = 'Load python script generated by Otter'
    )
    parser.add_argument(
        '--version',
        action = 'version',
        version = 'otter {}'.format(consts.VERSION))
    unused_args = parser.parse_args()

    # ----

    check_requirements()

    # pylint: disable=import-outside-toplevel
    from PyQt5 import QtWidgets, QtGui, QtCore
    from MainWindow import MainWindow

    QtCore.QCoreApplication.setOrganizationName("David Andrs")
    QtCore.QCoreApplication.setOrganizationDomain("name.andrs")
    QtCore.QCoreApplication.setApplicationName("Otter")

    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    qapp = QtWidgets.QApplication(sys.argv)
    icon_path = os.path.join(otter_dir, "icons", "otter.svg")
    qapp.setWindowIcon(QtGui.QIcon(icon_path))
    qapp.setQuitOnLastWindowClosed(False)

    home_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.HomeLocation)
    os.chdir(home_dir)

    window = MainWindow()
    window.setPluginsDir(os.path.join(otter_dir, "plugins"))
    window.loadPlugins()
    window.show()

    sys.exit(qapp.exec_())

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    set_paths()
    run()
