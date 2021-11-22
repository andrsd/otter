from unittest.mock import patch
from PyQt5 import QtGui
from otter.plugins.viz.VizPlugin import VizPlugin


def test_init(viz_plugin):
    assert viz_plugin._render_window is None


def test_name():
    assert VizPlugin.name() == "Viz"


def test_icon():
    assert isinstance(VizPlugin.icon(), QtGui.QIcon)


@patch('otter.plugins.Plugin.Plugin.registerWindow')
def test_on_create(reg_wnd, viz_plugin):
    viz_plugin.onCreate()
    assert reg_wnd.call_count == 1
