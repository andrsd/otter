import unittest
from otter import common

class TestApp(unittest.TestCase):

    def test_remap_plot_axis(self):
        args = {
            'axis-visible': 'axis-visible',
            'font-size': 'font-size',
            'font-color': 'font-color',
            'grid-color': 'grid-color',
            'labels-visible': 'labels-visible',
            'range': 'range',
            'num-ticks': 'num-ticks',
            'ticks-visible': 'ticks-visible'
        }
        remapped_args = common.remapPlotAxis(args)
        self.assertEqual(remapped_args['axis_visible'], "axis-visible")
        self.assertEqual(remapped_args['font_size'], "font-size")
        self.assertEqual(remapped_args['font_color'], "font-color")
        self.assertEqual(remapped_args['grid_color'], "grid-color")
        self.assertEqual(remapped_args['labels_visible'], "labels-visible")
        self.assertEqual(remapped_args['lim'], "range")
        self.assertEqual(remapped_args['num_ticks'], "num-ticks")
        self.assertEqual(remapped_args['ticks_visible'], "ticks-visible")

    def test_remap(self):
        args = {
            'bad-file': 'bad_file.ext',
            'file': 'file.ext'
        }
        map = {
            'bad-file': 'bad_file'
        }
        remapped_args = common.remap(args, map)
        self.assertEqual(remapped_args['bad_file'], "bad_file.ext")
        self.assertEqual(remapped_args['file'], "file.ext")

    def test_set_time_unit(self):
        common.setTimeUnit('sec')
        self.assertEqual(common.time_unit, 1.)
        self.assertEqual(common.time_unit_str, 'seconds')

        common.setTimeUnit('min')
        self.assertEqual(common.time_unit, 1. / 60.)
        self.assertEqual(common.time_unit_str, 'minutes')

        common.setTimeUnit('hour')
        self.assertEqual(common.time_unit, 1. / 3600.)
        self.assertEqual(common.time_unit_str, 'hours')

        common.setTimeUnit('day')
        self.assertEqual(common.time_unit, 1. / 86400.)
        self.assertEqual(common.time_unit_str, 'days')

        with self.assertRaises(SystemExit):
            common.setTimeUnit('asdf')

    def test_format_time_str(self):
        self.assertEqual(common.formatTimeStr(None, 90.), "Time: 90.00 seconds")
        self.assertEqual(common.formatTimeStr('{:1.0f}', 1.4), "Time: 1 seconds")

    def test_build_camera(self):
        args = {
            'view-up': [1, 0, 0],
            'position': [1, 2, 3],
            'focal-point': [0, 0, 2]
        }
        camera = common.buildCamera(args)
        self.assertEqual(camera.GetViewUp(), (1., 0., 0.))
        self.assertEqual(camera.GetPosition(), (1., 2., 3.))
        self.assertEqual(camera.GetFocalPoint(), (0., 0., 2.))

    def test_check_mandatory_args_ok(self):
        args = ['file']
        data = ['file']
        common.checkMandatoryArgs(args, data)
        pass

    def test_check_mandatory_args_fail(self):
        args = ['file']
        data = ['common']
        with self.assertRaises(SystemExit):
            common.checkMandatoryArgs(args, data)


if __name__ == '__main__':
    unittest.main()
