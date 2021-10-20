from unittest.mock import patch
from PyQt5 import QtGui
from otter.plugins.movie.MoviePlugin import MoviePlugin


def test_init(movie_plugin):
    assert movie_plugin._params_window is None
    assert movie_plugin._result_window is None


def test_name():
    assert MoviePlugin.name() == "Movie"


def test_icon():
    assert isinstance(MoviePlugin.icon(), QtGui.QIcon)


@patch('otter.plugins.Plugin.Plugin.registerWindow')
def test_on_create(reg_wnd, movie_plugin):
    movie_plugin.onCreate()
    assert reg_wnd.call_count == 2
