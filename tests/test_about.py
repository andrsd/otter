from PyQt5 import QtWidgets
from otter import consts
from otter.AboutDialog import AboutDialog


def test_open_about_dialog(main_window):
    assert main_window.about_dlg is None
    main_window.onAbout()
    assert isinstance(main_window.about_dlg, AboutDialog)


def test_about_dialog(main_window):
    dlg = AboutDialog(main_window)
    assert isinstance(dlg.icon, QtWidgets.QLabel)
    assert isinstance(dlg.title, QtWidgets.QLabel)
    assert dlg.title.text() == consts.APP_NAME
    assert isinstance(dlg.layout, QtWidgets.QVBoxLayout)
