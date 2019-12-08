#!/usr/bin/env python

import sys, os
import signal
import importlib.util

"""
Check that all packages we are using are present. If not, let users know.
"""
def checkRequirements():
    stop = False

    # check system packages
    modules = [ 'PyQt5', 'vtk', 'numpy', 'bisect']
    not_found_modules = []
    for m in modules:
        if importlib.util.find_spec(m) == None:
            not_found_modules.append(m)

    if len(not_found_modules) > 0:
        print("The following modules were not found: {}. "
            "This may be fixed by installing them either via 'pip' or 'conda'.".format(", ".join(not_found_modules)))
        stop = True

    # check MOOSE packages
    moose_modules = ['mooseutils', 'chigger']
    not_found_modules = []
    for m in moose_modules:
        if importlib.util.find_spec(m) == None:
            not_found_modules.append(m)

    if len(not_found_modules) > 0:
        print("The following modules were not found: {}. "
            "This may be fixed by setting MOOSE_DIR environment variable.".format(", ".join(not_found_modules)))
        stop = True

    if stop:
        exit(1)

"""
Run the main application
"""
def main(args):
    global otter_dir

    checkRequirements()
    # these might not work until the path is set
    from PyQt5 import QtWidgets, QtGui
    from gui.OtterMainWindow import OtterMainWindow

    qapp = QtWidgets.QApplication(args)
    icon_path = os.path.join(otter_dir, "icons", "otter.png")
    qapp.setWindowIcon(QtGui.QIcon(icon_path))

    main_win = OtterMainWindow()
    main_win.show()

    return qapp.exec_()


"""
Run otter GUI
"""
def run_otter():
    global otter_dir

    otter_dir = os.path.dirname(os.path.realpath(__file__))
    moose_dir = os.environ.get("MOOSE_DIR", None)
    if moose_dir == None:
        # we assume that THM is always a submodule of an application
        app_dir = os.path.dirname(otter_dir)
        moose_dir = os.path.join(app_dir, "moose")
    chigger_dir = os.path.join(moose_dir, "python", "chigger")

    sys.path.append(os.path.join(moose_dir, "python"))
    sys.path.append(chigger_dir)
    sys.path.append(otter_dir)

    sys.exit(main(sys.argv))

if __name__ == '__main__':
    run_otter()
