import pytest


@pytest.fixture
def movie_plugin(qtbot):
    from otter.plugins.movie.MoviePlugin import MoviePlugin
    plugin = MoviePlugin(None)
    yield plugin
