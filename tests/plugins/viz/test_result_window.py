import pytest
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets, QtCore
from otter.plugins.viz.ResultWindow import ResultWindow


@pytest.fixture
def result_window(qtbot, movie_plugin):
    wnd = ResultWindow(movie_plugin)
    qtbot.addWidget(wnd)
    yield wnd


def test_init(result_window):
    assert isinstance(result_window, QtWidgets.QMainWindow)


@patch('PyQt5.QtWidgets.QMainWindow.event')
def test_event_activate_window(event_mock, result_window):
    e = MagicMock()
    e.type.return_value = QtCore.QEvent.WindowActivate

    plugin = MagicMock()
    result_window.plugin = plugin
    result_window.event(e)
    plugin.updateMenuBar.assert_called_once()


def test_update_window_title(result_window):
    result_window._file_name = None
    result_window.updateWindowTitle()
    assert result_window.windowTitle() == "Result"

    result_window._file_name = "/a/b.c"
    result_window.updateWindowTitle()
    assert result_window.windowTitle() == "Result \u2014 b.c"
