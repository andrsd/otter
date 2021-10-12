from PyQt5 import QtWidgets


def test_file_new_action(main_window, qtbot):
    assert isinstance(main_window._new_action, QtWidgets.QAction)
    main_window._new_action.trigger()
    qtbot.waitExposed(main_window.project_type_dlg)
    assert main_window.project_type_dlg.isVisible()
