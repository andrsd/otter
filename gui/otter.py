#!/usr/bin/env python

import sys, os
import signal

def main(args):
    # these might not work until the path is set
    from PyQt5.QtWidgets import QApplication
    from OtterMainWindow import OtterMainWindow

    qapp = QApplication(args)
    main_win = OtterMainWindow()
    main_win.show()

    return qapp.exec_()

def run_otter():
    my_dir = os.path.dirname(os.path.realpath(__file__))
    otter_dir = os.path.dirname(my_dir)
    moose_dir = os.environ.get("MOOSE_DIR", None)
    if moose_dir == None:
        # we assume that THM is always a submodule of an application
        app_dir = os.path.dirname(otter_dir)
        moose_dir = os.path.join(app_dir, "moose")
    chigger_dir = os.path.join(moose_dir, "python", "chigger")

    sys.path.append(os.path.join(moose_dir, "python"))
    sys.path.append(chigger_dir)

    sys.exit(main(sys.argv))

if __name__ == '__main__':
    run_otter()
