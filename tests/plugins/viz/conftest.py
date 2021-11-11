import pytest


@pytest.fixture
def viz_plugin(qtbot):
    from otter.plugins.viz.VizPlugin import VizPlugin
    plugin = VizPlugin(None)
    yield plugin
