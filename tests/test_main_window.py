import os
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets


def test_file_new_action(main_window, qtbot):
    assert isinstance(main_window._new_action, QtWidgets.QAction)
    main_window._new_action.trigger()
    qtbot.waitExposed(main_window.project_type_dlg)
    assert main_window.project_type_dlg.isVisible()


@patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
@patch('otter.MainWindow.MainWindow.openFile')
def test_file_open_action(open_file_mock, file_dlg_mock, main_window):
    """
    Test that open file action works
    """
    root = os.path.dirname(__file__)
    file_name = os.path.join(root, 'assets', 'empty.otter')
    file_dlg_mock.return_value = (file_name, None)
    main_window.onOpenFile()
    open_file_mock.assert_called_once()


def test_open_file(main_window):
    """
    Test that opening a file works
    """
    empty_plugin = MagicMock()

    prj_type_dlg_mock = MagicMock()
    prj_type_dlg_mock.getPluginByType.return_value = empty_plugin

    main_window.project_type_dlg = prj_type_dlg_mock

    root = os.path.dirname(__file__)
    file_name = os.path.join(root, 'assets', 'empty_params.otter')
    main_window.openFile(file_name)

    empty_plugin.create.assert_called_once()
    empty_plugin.setupFromYml.assert_called_once()


@patch('PyQt5.QtWidgets.QMessageBox.information')
def test_open_file_not_otter(info_mock, main_window):
    """
    Opening YML file that was is not a otter file
    """
    root = os.path.dirname(__file__)
    file_name = os.path.join(root, 'assets', 'not_otter.otter')
    main_window.openFile(file_name)
    info_mock.assert_called_once()


@patch('PyQt5.QtWidgets.QMessageBox.information')
def test_open_file_empty(info_mock, main_window):
    """
    Opening an empty YML file
    """
    root = os.path.dirname(__file__)
    file_name = os.path.join(root, 'assets', 'null.otter')
    main_window.openFile(file_name)
    info_mock.assert_called_once()


@patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
def test_file_open_with_no_filename(file_dlg_mock, main_window):
    file_dlg_mock.return_value = (None, None)
    main_window.onOpenFile()


def test_create_project(main_window):
    """
    Test that plugin is create when onCreateProject is called
    """
    empty_plugin = MagicMock()

    prj_type_dlg_mock = MagicMock()
    prj_type_dlg_mock.result.return_value = QtWidgets.QDialog.Accepted
    prj_type_dlg_mock.plugin = empty_plugin

    main_window.project_type_dlg = prj_type_dlg_mock
    main_window.onCreateProject()
    empty_plugin.create.assert_called_once()


def test_close_file(main_window):
    """
    Test closing a file
    """
    plugin = MagicMock()

    main_window.plugin = plugin
    main_window.onCloseFile()

    plugin.close.assert_called_once()
    plugin.showMenu.assert_called_once_with(False)


def test_save_file_without_plugin(main_window):
    """
    Test 'save file' with no plugin
    """
    main_window.plugin = None
    main_window.onSaveFile()


@patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
@patch('otter.MainWindow.MainWindow.writeYml')
def test_save_file_with_plugin_no_name(
        write_yml_mock, file_dlg_mock, main_window):
    """
    Test 'save file' with a plugin
    """
    file_name = 'some_file_name.yml'
    file_dlg_mock.return_value = (file_name, None)

    plugin = MagicMock()
    plugin.getFileName.return_value = None
    main_window.plugin = plugin
    main_window.onSaveFile()
    write_yml_mock.assert_called_once_with(file_name)


@patch('otter.MainWindow.MainWindow.writeYml')
def test_save_file_with_plugin_with_name(write_yml_mock, main_window):
    """
    Test 'save file' with a plugin
    """
    file_name = 'some_file_name.yml'

    plugin = MagicMock()
    plugin.getFileName.return_value = file_name
    main_window.plugin = plugin
    main_window.onSaveFile()
    write_yml_mock.assert_called_once_with(file_name)


def test_save_file_as_without_plugin(main_window):
    """
    Test 'save file as' with no plugin
    """
    main_window.plugin = None
    main_window.onSaveFileAs()


@patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
@patch('otter.MainWindow.MainWindow.writeYml')
def test_save_file_as_with_plugin(write_yml_mock, file_dlg_mock, main_window):
    """
    Test 'save file as' with a plugin
    """
    file_name = 'some_file_name.yml'
    file_dlg_mock.return_value = (file_name, None)

    main_window.plugin = MagicMock()

    main_window.onSaveFileAs()
    write_yml_mock.assert_called_once_with(file_name)


def test_on_minimize_with_plugin(main_window):
    plugin = MagicMock()
    main_window.plugin = plugin
    main_window.onMinimize()
    plugin.minimize.assert_called_once()


@patch('otter.MainWindow.MainWindow.showMinimized')
def test_on_minimize_without_plugin(minimize_mock, main_window):
    main_window.plugin = None
    main_window.onMinimize()
    minimize_mock.assert_called_once()


def test_bring_all_to_front_with_plugin(main_window):
    plugin = MagicMock()
    main_window.plugin = plugin
    main_window.onBringAllToFront()
    plugin.bringAllToFront.assert_called_once()


@patch('otter.MainWindow.MainWindow.showNormal')
def test_bring_all_to_front_without_plugin(show_normal_mock, main_window):
    main_window.plugin = None
    main_window.onBringAllToFront()
    show_normal_mock.assert_called_once()


@patch('otter.MainWindow.MainWindow.showNormal')
@patch('otter.MainWindow.MainWindow.activateWindow')
@patch('otter.MainWindow.MainWindow.updateMenuBar')
def test_show_main_window(show_normal_mock,
                          activate_window_mock,
                          update_menu_bar_mock,
                          main_window):
    main_window.onShowMainWindow()
    show_normal_mock.assert_called_once()
    activate_window_mock.assert_called_once()
    update_menu_bar_mock.assert_called_once()


@patch('otter.MainWindow.MainWindow.openFile')
@patch('otter.MainWindow.MainWindow.sender')
def test_open_recent_file(sender_mock, open_file_mock, main_window):
    main_window.onOpenRecentFile()
    open_file_mock.assert_called_once()


@patch('otter.MainWindow.MainWindow.buildRecentFilesMenu')
def test_clear_recent_files(build_mock, main_window):
    main_window.recent_files = ['1', '2']
    main_window.recent_tab = MagicMock()
    main_window.onClearRecentFiles()
    assert len(main_window.recent_files) == 0
    build_mock.assert_called_once()
    main_window.recent_tab.clear.assert_called_once()


def test_add_to_recent_file_repeatedly(main_window):
    """
    Test adding the same file twice
    """
    main_window.addToRecentFiles('file1')
    main_window.addToRecentFiles('file1')
    assert len(main_window.recent_files) == 1


def test_add_to_recent_file_a_lot(main_window):
    """
    Test adding more then MAX_RECENT_FILES files
    """
    for i in range(main_window.MAX_RECENT_FILES + 1):
        main_window.addToRecentFiles('file' + str(i))
    assert len(main_window.recent_files) == main_window.MAX_RECENT_FILES


def test_set_plugins_dir(main_window):
    dir_name = 'some_dir'
    main_window.project_type_dlg = MagicMock()
    main_window.setPluginsDir(dir_name)
    assert main_window.project_type_dlg.plugins_dir == dir_name


def test_load_plugins(main_window):
    main_window.project_type_dlg = MagicMock()
    main_window.loadPlugins()
    main_window.project_type_dlg.findPlugins.assert_called_once()
    main_window.project_type_dlg.addProjectTypes.assert_called_once()
    main_window.project_type_dlg.updateControls.assert_called_once()
