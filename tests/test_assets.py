from PyQt5 import QtGui
from otter.assets import Assets


def test_singleton():
    assert Assets() is Assets()

    for key in Assets().icons:
        assert Assets().icons[key] is Assets().icons[key]


def test():
    for key in Assets().icons:
        assert isinstance(Assets().icons[key], QtGui.QIcon)
