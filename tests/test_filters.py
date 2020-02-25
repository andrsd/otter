import unittest
from otter import common
from otter import filters
from otter import viewports
import chigger
import os

cwd = os.path.dirname(__file__)

class TestApp(unittest.TestCase):

    def test_build_plane_clip(self):
        filter = {
            'type': 'plane-clip'
        }

        obj = filters.buildFilter(filter)
        self.assertEqual(isinstance(obj, chigger.filters.PlaneClipper), True)

    def test_build_box_clip(self):
        filter = {
            'type': 'box-clip'
        }

        obj = filters.buildFilter(filter)
        self.assertEqual(isinstance(obj, chigger.filters.BoxClipper), True)

    def test_build_transform(self):
        filter = {
            'type': 'transform'
        }

        obj = filters.buildFilter(filter)
        self.assertEqual(isinstance(obj, chigger.filters.TransformFilter), True)

    def test_build_unknown(self):
        filter = {
            'type': 'asfd'
        }

        obj = filters.buildFilter(filter)
        self.assertEqual(obj, None)

    def test_plane_clip(self):
        plane_clip = {
            'type': 'plane-clip'
        }

        vp = [
            {
                'type': 'ExodusResult',
                'name': 'a',
                'variable': 'var',
                'file': os.path.join(cwd, 'mug.e'),
                'title': 'Title',
                'camera': {
                    'view-up': [0, 0, 0],
                    'focal-point': [1, 0, 0],
                    'position': [0, 0, 0]
                },
                'filters': [
                    plane_clip
                ]
            }
        ]

        obj = viewports.process(vp)


if __name__ == '__main__':
    unittest.main()
