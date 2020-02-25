import unittest
import otter
import os

cwd = os.path.dirname(__file__)

class TestApp(unittest.TestCase):

    def test_image(self):
        viewports = [
        ]

        colorbars = [
        ]

        annotations = [
        ]

        image = {
            'size': [400, 300],
            'background': [0.0, 0.0, 0.0],
            't': '0.0',
            'time-unit': 'sec',
            'output': os.path.join(cwd, 'image.png'),
            'viewports': viewports,
            'colorbars': colorbars,
            'annotations': annotations
        }

        otter.render(image)
