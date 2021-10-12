import os
from unittest.mock import patch
from otter.RecentFilesTab import RecentFilesTab


@patch('otter.MainWindow.MainWindow.onNewFile')
def test_on_new(new_file_mock, main_window):
    rft = RecentFilesTab(main_window)
    rft.onNew()
    new_file_mock.assert_called_once()


@patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
@patch('otter.MainWindow.MainWindow.openFile')
def test_on_browse_documents(open_file_mock, file_dlg_mock, main_window):
    file_dlg_mock.return_value = ('file', None)

    rft = RecentFilesTab(main_window)
    rft.onBrowseDocuments()

    open_file_mock.assert_called_once_with('file')


@patch('otter.MainWindow.MainWindow.openFile')
def test_on_open(open_file_mock, main_window):
    root = os.path.dirname(__file__)
    file_name = os.path.join(root, 'assets', 'empty_params.otter')

    rft = RecentFilesTab(main_window)
    rft.addFileItem(file_name)

    item = rft.model.item(0)
    index = rft.model.indexFromItem(item)
    rft.file_list.setCurrentIndex(index)

    rft.onOpen()

    open_file_mock.assert_called_once_with(item.data())


def test_on_clear(main_window):
    rft = RecentFilesTab(main_window)
    rft.clear()
    assert rft.model.rowCount() == 0 and rft.model.columnCount() == 0
