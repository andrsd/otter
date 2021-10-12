import os
from unittest.mock import MagicMock, patch
from PyQt5 import QtGui


@patch('otter.ProjectTypeDialog.ProjectTypeDialog.loadPlugin')
def test_find_plugins(load_mock, main_window):
    root = os.path.dirname(__file__)
    plugin_dir = os.path.join(root, 'assets', 'plugins')

    main_window.setPluginsDir(plugin_dir)
    main_window.project_type_dlg.findPlugins()
    assert load_mock.call_count == 2


def test_plugin_by_type(main_window):
    plugin1 = MagicMock()

    prj_dlg = main_window.project_type_dlg
    prj_dlg.plugin_map['plugin1'] = plugin1
    assert main_window.project_type_dlg.getPluginByType('plugin1') is plugin1
    assert main_window.project_type_dlg.getPluginByType('plugin2') is None


def test_add_project_types(main_window):
    prj_dlg = main_window.project_type_dlg

    plugin1 = MagicMock()
    plugin1.icon.return_value = QtGui.QIcon()
    plugin1.name.return_value = "plugin1_name"

    prj_dlg.plugins.append(plugin1)
    prj_dlg.plugin_map['plugin1'] = plugin1

    prj_dlg.addProjectTypes()

    assert prj_dlg.model.rowCount() == 1
    si = prj_dlg.model.item(0)
    assert isinstance(si.icon(), QtGui.QIcon)
    assert si.text() == "plugin1_name"


@patch('otter.ProjectTypeDialog.ProjectTypeDialog.accept')
def test_on_create(accept_mock, main_window):
    prj_dlg = main_window.project_type_dlg

    plugin1 = MagicMock()
    plugin1.icon.return_value = QtGui.QIcon()
    plugin1.name.return_value = "plugin1_name"

    prj_dlg.plugins.append(plugin1)
    prj_dlg.plugin_map['plugin1'] = plugin1
    prj_dlg.addProjectTypes()

    item = prj_dlg.model.item(0)
    index = prj_dlg.model.indexFromItem(item)
    prj_dlg.list_view.setCurrentIndex(index)

    prj_dlg.onCreate()
    accept_mock.assert_called_once()


def test_load_plugin(main_window):
    root = os.path.dirname(__file__)
    plugin_dir = os.path.join(root, 'assets', 'plugins', 'plugin1')

    # main_window.setPluginsDir(plugin_dir)
    # main_window.project_type_dlg.findPlugins()
    prj_dlg = main_window.project_type_dlg
    prj_dlg.loadPlugin(plugin_dir)
