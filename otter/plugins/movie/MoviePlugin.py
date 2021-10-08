"""
MoviePlugin.py
"""

from ChiggerPluginBase import ChiggerPluginBase
from otter.assets import Assets


class MoviePlugin(ChiggerPluginBase):
    """
    Plugin for chigger movies
    """

    def __init__(self, parent):
        super().__init__(parent)

    @staticmethod
    def name():
        """
        Name of the plug-in
        """
        return "Movie"

    @staticmethod
    def icon():
        """
        Icon of the plug-in
        """
        return Assets().icons['movie']
