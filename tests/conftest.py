import pytest


@pytest.fixture
def main_window(qtbot):
    """
    Returns an instance of MainWindow
    """
    from otter.MainWindow import MainWindow
    main = MainWindow()
    qtbot.addWidget(main)
    yield main
