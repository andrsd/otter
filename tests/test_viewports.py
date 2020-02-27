import os
import unittest
from otter import common
from otter import viewports

cwd = os.path.dirname(__file__)

class TestApp(unittest.TestCase):

    def test_viewport(self):
        src = {
            'asdf': 'zxcv'
        }
        viewport = viewports.Viewport(src)

        viewport.update(1.)

        self.assertEqual(viewport['asdf'], 'zxcv')
        self.assertEqual(viewport.result(), None)

    def test_exodus_result(self):
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
        result = vp.result()
        result._setInitialOptions()

        opts = result.options()
        self.assertEqual(opts['variable'], 'var')

        vp.update(0.)

    def test_plot_over_time(self):
        T_var = {
            'name': 'T',
            'width': 1
        }

        p_var = {
            'name': 'p',
            'color': [0.3, 0.2, 0.1],
            'width': 1,
            'scale': 1e6
        }

        common.t = 2
        src = {
            'type': 'PlotOverTime',
            'name': 'a',
            'variables': [
                T_var,
                p_var
            ],
            'file': os.path.join(cwd, 'T.csv'),
            'title': 'Title',
            'x-axis': {
                'range': [0, 1],
                'num-ticks': 5
            },
            'y-axis': {
                'range': [0, 1],
                'num-ticks': 3
            }
        }
        vp = viewports.ViewportPlotOverTime(src)
        result = vp.result()
        result._setInitialOptions()

        opts = result.options()

        vp.update(0.)

    def test_plot_over_time_auto_scale(self):
        T_var = {
            'name': 'T',
            'color': [0.1, 0.2, 0.3],
            'width': 1
        }

        common.t = 2
        src = {
            'type': 'PlotOverTime',
            'name': 'a',
            'variables': [
                T_var
            ],
            'file': os.path.join(cwd, 'T.csv'),
            'title': 'Title',
            'x-axis': {
                'num-ticks': 5
            },
            'y-axis': {
                'num-ticks': 3
            }
        }
        vp = viewports.ViewportPlotOverTime(src)
        result = vp.result()
        result._setInitialOptions()

        opts = result.options()

    def test_vpp_plot(self):
        T_var = {
            'name': 'T',
            'width': 6,
            'color': [0, 0.5, 1],
            'label': 'temp'
        }

        common.t = 2
        src = {
            'type': 'VPPPlot',
            'name': 'a',
            'variables': [
                T_var
            ],
            'exodus-file': os.path.join(cwd, 'diffusion_1.e'),
            'csv-file': os.path.join(cwd, 'vpp1*csv'),
            'title': 'Title',
            'viewport': [0, 0, 1, 1]
        }
        vp = viewports.ViewportVPPPlot(src)
        result = vp.result()
        result._setInitialOptions()

        opts = result.options()

        vp.update(0.1)

    def test_vpp_plot_scaled_axis(self):
        xaxis = {
            'title': 'Length [cm]',
            'scale': 1e2
        }

        yaxis = {
            'title': 'T',
            'scale': 1.
        }

        T_var = {
            'name': 'T',
            'label': 'temp'
        }

        common.t = 2
        src = {
            'type': 'VPPPlot',
            'name': 'a',
            'variables': [
                T_var
            ],
            'exodus-file': os.path.join(cwd, 'diffusion_1.e'),
            'csv-file': os.path.join(cwd, 'vpp1*csv'),
            'title': 'Title',
            'viewport': [0, 0, 1, 1],
            'x-axis': xaxis,
            'y-axis': yaxis
        }
        vp = viewports.ViewportVPPPlot(src)
        result = vp.result()
        result._setInitialOptions()

    def test_vpp_plot_legend(self):
        legend = {
            'label-font-size': 40
        }

        T_var = {
            'name': 'T',
            'label': 'temp'
        }

        common.t = 2
        src = {
            'type': 'VPPPlot',
            'name': 'a',
            'variables': [
                T_var
            ],
            'exodus-file': os.path.join(cwd, 'diffusion_1.e'),
            'csv-file': os.path.join(cwd, 'vpp1*csv'),
            'title': 'Title',
            'viewport': [0, 0, 1, 1],
            'legend': legend
        }
        vp = viewports.ViewportVPPPlot(src)
        result = vp.result()
        result._setInitialOptions()

    def test_build_exodus_result(self):
        vp = [
            {
                'type': 'ExodusResult',
                'name': 'a',
                'variable': 'var',
                'file': os.path.join(cwd, 'diffusion_1.e'),
                'title': 'Title',
                'camera': {
                    'view-up': [0, 0, 0],
                    'focal-point': [1, 0, 0],
                    'position': [0, 0, 0]
                }
            }
        ]

        objs = viewports.process(vp)
        self.assertEqual(isinstance(objs[0], viewports.ViewportExodusResult), True)

    def test_build_unknown_type(self):
        vp = [
            {
                'type': 'ASDF'
            }
        ]

        objs = viewports.process(vp)
        self.assertEqual(objs, [])

    def test_missing_type(self):
        vp = [
            {
            }
        ]

        objs = viewports.process(vp)
        self.assertEqual(objs, [])

if __name__ == '__main__':
    unittest.main()
