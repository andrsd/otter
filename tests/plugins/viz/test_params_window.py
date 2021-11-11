import pytest
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets, QtCore
from otter.plugins.viz.ParamsWindow import ParamsWindow


@pytest.fixture
def params_window(qtbot, movie_plugin):
    wnd = ParamsWindow(movie_plugin)
    qtbot.addWidget(wnd)
    yield wnd


def test_init(params_window):
    assert isinstance(params_window, QtWidgets.QScrollArea)


@patch('PyQt5.QtWidgets.QScrollArea.event')
def test_event_activate_window(event_mock, params_window):
    e = MagicMock()
    e.type.return_value = QtCore.QEvent.WindowActivate

    plugin = MagicMock()
    params_window.plugin = plugin
    params_window.event(e)
    plugin.updateMenuBar.assert_called_once()
