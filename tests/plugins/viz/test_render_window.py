import pytest
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets, QtCore
from otter.plugins.viz.RenderWindow import RenderWindow


@pytest.fixture
def render_window(qtbot, viz_plugin):
    wnd = RenderWindow(viz_plugin)
    qtbot.addWidget(wnd)
    yield wnd


def test_init(render_window):
    assert isinstance(render_window, QtWidgets.QMainWindow)


@patch('PyQt5.QtWidgets.QMainWindow.event')
def test_event_activate_window(event_mock, render_window):
    e = MagicMock()
    e.type.return_value = QtCore.QEvent.WindowActivate

    plugin = MagicMock()
    render_window.plugin = plugin
    render_window.event(e)
    plugin.updateMenuBar.assert_called_once()


def test_update_window_title(render_window):
    render_window._file_name = None
    render_window.updateWindowTitle()
    assert render_window.windowTitle() == "Result"

    render_window._file_name = "/a/b.c"
    render_window.updateWindowTitle()
    assert render_window.windowTitle() == "Result \u2014 b.c"
