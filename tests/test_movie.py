import unittest
import otter
import os

cwd = os.path.dirname(__file__)

class TestApp(unittest.TestCase):

    def test_movie(self):
        viewports = [
            {
                'type': 'ExodusResult',
                'name': 'a',
                'variable': 'u',
                'file': os.path.join(cwd, 'diffusion_1.e'),
                'title': 'Title1',
                'camera': {
                    'view-up': [0, 0, 0],
                    'focal-point': [1, 0, 0],
                    'position': [0, 0, 0]
                }
            }
        ]

        colorbars = [
        ]

        annotations = [
        ]

        movie = {
            'duration': 1.0,
            'file': os.path.join(cwd, 'movie.mov'),
            'size': [1280, 720],
            'times': [0, 0.1],
            'time-unit': 'sec',
            'viewports': viewports,
            'colorbars': colorbars,
            'annotations': annotations
        }

        if 'TRAVIS_CI' not in os.environ:
            otter.render(movie)

    def test_missing_star_in_frame_param(self):
        viewports = [
        ]

        colorbars = [
        ]

        annotations = [
        ]

        movie = {
            'duration': 1.0,
            'file': os.path.join(cwd, 'movie.mov'),
            'frame': 'frame.png',
            'size': [1280, 720],
            'times': [0.],
            'time-unit': 'sec',
            'viewports': viewports,
            'colorbars': colorbars,
            'annotations': annotations
        }

        with self.assertRaises(SystemExit):
            otter.render(movie)
