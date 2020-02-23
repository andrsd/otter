import os
import unittest
from otter import common
from otter import viewports
from otter import colorbars

cwd = os.path.dirname(__file__)

class TestApp(unittest.TestCase):

    def test_colorbar1(self):
        common.t = 2
        src = {
            'type': 'ExodusResult',
            'name': 'a',
            'variable': 'var',
            'file': os.path.join(cwd, 'mug.e'),
            'title': 'Title',
            'camera': {
                'view-up': [0, 0, 0],
                'focal-point': [1, 0, 0],
                'position': [0, 0, 0]
            }
        }
        vp = viewports.ViewportExodusResult(src)
        vp.result()._setInitialOptions()

        src = {
            'num-colors': 20,
            'width': 0.5,
            'primary': {
                'result': 'a'
            }
        }
        cb = colorbars.ColorBar(src)
        cb.result()._setInitialOptions()

        opts = cb.result().options()
        self.assertEqual(opts['width'], 0.5)

        cb.update(10.)

    def test_colorbar2(self):
        common.t = 2
        src = {
            'type': 'ExodusResult',
            'name': 'a',
            'variable': 'var',
            'file': os.path.join(cwd, 'mug.e'),
            'title': 'Title1',
            'camera': {
                'view-up': [0, 0, 0],
                'focal-point': [1, 0, 0],
                'position': [0, 0, 0]
            }
        }
        vp1 = viewports.ViewportExodusResult(src)
        vp1.result()._setInitialOptions()

        src = {
            'type': 'ExodusResult',
            'name': 'b',
            'variable': 'var',
            'file': os.path.join(cwd, 'mug.e'),
            'title': 'Title2',
            'camera': {
                'view-up': [0, 0, 0],
                'focal-point': [1, 0, 0],
                'position': [0, 0, 0]
            }
        }
        vp2 = viewports.ViewportExodusResult(src)
        vp2.result()._setInitialOptions()

        src = {
            'num-colors': 20,
            'length': 1,
            'primary': {
                'result': 'a'
            },
            'secondary': {
                'result': 'b'
            }
        }
        cb = colorbars.ColorBar(src)
        cb.result()._setInitialOptions()

        opts = cb.result().options()
        self.assertEqual(opts['length'], 1)

        cb.update(10.)

    def test_missing_axis(self):
        common.t = 2
        src = {
            'num-colors': 20
        }
        with self.assertRaises(SystemExit):
            cb = colorbars.ColorBar(src)

    def test_missing_result_param(self):
        common.t = 2
        src = {
            'num-colors': 20,
            'primary': {
            },
        }
        with self.assertRaises(SystemExit):
            cb = colorbars.ColorBar(src)

    def test_non_existent_result(self):
        common.t = 2
        src = {
            'num-colors': 20,
            'primary': {
                'result': 'doesnt-exist'
            },
        }
        with self.assertRaises(SystemExit):
            cb = colorbars.ColorBar(src)

    def test_build_color_bar(self):
        common.t = 2
        src = [
            {
                'type': 'ExodusResult',
                'name': 'a',
                'variable': 'var',
                'file': os.path.join(cwd, 'mug.e'),
                'title': 'Title1',
                'camera': {
                    'view-up': [0, 0, 0],
                    'focal-point': [1, 0, 0],
                    'position': [0, 0, 0]
                }
            }
        ]
        objs = viewports.process(src)

        cb = [
            {
                'num-colors': 20,
                'primary': {
                    'result': 'a'
                }
            }
        ]

        objs = colorbars.process(cb)
        self.assertEqual(isinstance(objs[0], colorbars.ColorBar), True)


if __name__ == '__main__':
    unittest.main()
