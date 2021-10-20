import pytest


@pytest.fixture
def csvplotter_plugin(qtbot):
    from otter.plugins.csvplotter.CSVPlotterPlugin import CSVPlotterPlugin
    plugin = CSVPlotterPlugin(None)
    yield plugin
