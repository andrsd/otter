import pytest


@pytest.fixture
def main_window(qtbot):
    from otter.MainWindow import MainWindow
    main = MainWindow()
    qtbot.addWidget(main)
    yield main
