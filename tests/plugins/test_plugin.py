from PyQt5 import QtWidgets
from unittest.mock import MagicMock, Mock, patch
from otter.plugins.Plugin import Plugin


def test_name():
    assert Plugin.name() is None


def test_icon():
    assert Plugin.icon() is None


def test_ctor():
    parent = MagicMock()
    plugin = Plugin(parent)
    assert plugin.file_name is None
    assert len(plugin.windows) == 0
    assert len(plugin.menus) == 0
    assert len(plugin.actions) == 0
    assert len(plugin._show_window.keys()) == 0
    assert len(plugin._menu_map.keys()) == 0


def test_file_name():
    file_name = 'file1'
    parent = MagicMock()
    plugin = Plugin(parent)
    plugin.setFileName(file_name)
    assert plugin.getFileName() == file_name


def test_params():
    parent = MagicMock()
    plugin = Plugin(parent)
    assert len(plugin.params()) == 0


def test_register_window(main_window):
    plugin = Plugin(main_window)
    window = QtWidgets.QWidget()
    plugin.registerWindow(window)

    assert window in plugin._show_window


@patch('otter.plugins.Plugin.Plugin.showMenu')
@patch('otter.plugins.Plugin.Plugin.onCreate')
@patch('otter.plugins.Plugin.Plugin.showWindow')
def test_create(show_window_mock, on_create_mock, show_menu_mock, main_window):
    plugin = Plugin(main_window)
    plugin.create()
    on_create_mock.assert_called_once_with()
    show_window_mock.assert_called_once_with()


def test_show_menu(main_window):
    plugin = Plugin(main_window)
    plugin.menus = [MagicMock()]
    plugin.actions = [MagicMock()]
    plugin.showMenu(True)

    plugin.menus[0].menuAction().setVisible.assert_called_once_with(True)
    plugin.actions[0].setVisible.assert_called_once_with(True)


def test_close():
    parent = MagicMock()
    plugin = Plugin(parent)
    window = MagicMock()
    action = MagicMock()
    plugin._show_window = {window: action}
    plugin.close()

    window.close.assert_called_once()
    parent.action_group_windows.removeAction.assert_called_once_with(action)
    assert len(plugin.windows) == 0
    assert len(plugin._show_window.keys()) == 0


def test_minimize():
    parent = MagicMock()
    plugin = Plugin(parent)
    window = MagicMock()
    plugin.windows = [window]

    plugin.minimize()
    window.showMinimized.assert_called_once()


def test_bring_all_to_front():
    parent = MagicMock()
    plugin = Plugin(parent)
    window = MagicMock()
    plugin.windows = [window]

    plugin.bringAllToFront()
    window.showNormal.assert_called_once()


def test_show_window():
    parent = MagicMock()
    plugin = Plugin(parent)
    window = MagicMock()
    plugin.windows = [window]

    plugin.showWindow()
    window.show.assert_called_once()


def test_set_window_visible():
    parent = MagicMock()
    plugin = Plugin(parent)
    window = MagicMock()
    action = MagicMock()
    plugin._show_window = {window: action}
    menu = MagicMock()
    plugin.menus = [menu]
    plugin.setWindowVisible(True)

    action.setVisible.assert_called_once_with(True)
    menu.menuAction().setVisible.assert_called_once_with(True)


@patch('otter.plugins.Plugin.Plugin.updateMenuBar')
def test_on_show_window(update_menubar_mock):
    parent = MagicMock()
    plugin = Plugin(parent)
    window = MagicMock()

    plugin.onShowWindow(window)

    window.showNormal.assert_called_once()
    window.activateWindow.assert_called_once()
    window.raise_.assert_called_once()
    update_menubar_mock.assert_called_once()


def test_get_menu_with_menubar():
    parent = MagicMock()
    parent.menubar.menus = {'file': 'menu'}
    plugin = Plugin(parent)
    assert plugin.getMenu('file') == 'menu'


def test_get_menu_without_menubar():
    parent = Mock(menubar=None)
    plugin = Plugin(parent)
    plugin._menu_map['file'] = 'menu'
    assert plugin.getMenu('file') == 'menu'


def test_get_menu_without_menubar_2():
    class MB:
        def addMenu(self, text):
            return 'menu'

    parent = Mock(menubar=MB())
    plugin = Plugin(parent)
    assert plugin.getMenu('file') == 'menu'


def test_add_menu():
    parent = MagicMock()
    plugin = Plugin(parent)

    menu = MagicMock()
    new_menu = plugin.addMenu(menu, 'text')

    assert plugin.menus.index(new_menu) == 0
    new_menu.menuAction().setVisible.assert_called_once_with(False)


def test_add_separator():
    parent = MagicMock()
    plugin = Plugin(parent)

    menu = MagicMock()
    action = plugin.addMenuSeparator(menu)

    assert plugin.actions.index(action) == 0


def test_add_menu_action():
    def method(a):
        pass

    parent = MagicMock()
    plugin = Plugin(parent)

    menu = MagicMock()
    menu.addAction.return_value = MagicMock()
    action = plugin.addMenuAction(menu, 'str', method, 1234)

    menu.addAction.assert_called_once_with('str', method, 1234)
    action.setVisible.assert_called_once_with(False)
    assert plugin.actions.index(action) == 0


@patch('PyQt5.QtWidgets.QApplication.activeWindow')
def test_update_menubar(active_win_mock):
    active_win_mock.return_value = 'win'

    action = MagicMock()

    parent = MagicMock()
    plugin = Plugin(parent)
    plugin._show_window['win'] = action

    plugin.updateMenuBar()

    action.setChecked.assert_called_once_with(True)
