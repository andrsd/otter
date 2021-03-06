import vtk
import chigger
from . import config, filters, common
import mooseutils
import bisect


OBJECTS = {}

class Viewport(object):
    """
    Base class for viewports
    """

    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        """
        To access parameters via object['parameter_name']
        """
        return self.data[key]

    def result(self):
        """
        Return the chigger result object
        """
        return None

    def update(self, time):
        """
        Update the viewport to reflect time 'time'
        """
        pass

    def times(self):
        """
        Return times of the simulation time steps. None if times are not supported.
        """
        return None


class ViewportExodusResult(Viewport):
    """
    Exodus result
    """
    MAP = {
        'blocks': 'block',
    }

    def __init__(self, viewport):
        super(ViewportExodusResult, self).__init__(viewport)

        if 'viewport' not in viewport:
            viewport['viewport'] = [0, 0, 1, 1]
        common.checkMandatoryArgs(['name', 'variable', 'file', 'camera'], viewport)

        self.name = viewport.pop('name')
        self.camera = common.buildCamera(viewport.pop('camera'))

        self.exodus_file = viewport.pop('file')
        self.exodus_reader = chigger.exodus.ExodusReader(
            self.exodus_file,
            variables = [viewport['variable']],
            time = common.t,
            timestep = common.timestep)

        if 'cmap' not in viewport:
            viewport['cmap'] = 'rainbow'

        args = common.remap(viewport, self.MAP)
        args['camera'] = self.camera

        if 'filters' in viewport:
            items = viewport['filters']
            self.filters = []
            for item in items:
                filter = filters.buildFilter(item)
                if filter != None:
                    self.filters.append(filter)
            args['filters'] = self.filters

        self.exodus_result = chigger.exodus.ExodusResult(self.exodus_reader, **args)
        OBJECTS[self.name] = self

    def result(self):
        return self.exodus_result

    def update(self, time):
        self.exodus_reader.setOptions(time = time, timestep = None)

    def times(self):
        return self.exodus_reader.getTimes()

class ViewportVPPPlot(Viewport):
    """
    Vector postprocessor plot

    Currently this has to be tied to an Exodus file, so that we know how time maps to timesteps
    """
    LINE_MAP = {
    }

    def __init__(self, viewport):
        super(ViewportVPPPlot, self).__init__(viewport)

        self._clr_idx = 0

        common.checkMandatoryArgs(['csv-file', 'variables', 'viewport'], viewport)

        self.csv_file = viewport.pop('csv-file')
        self.data = mooseutils.VectorPostprocessorReader(self.csv_file)

        if 'x-axis' in viewport:
            xaxis = viewport['x-axis']
            if 'scale' in xaxis:
                self.xscale = xaxis.pop('scale')
            else:
                self.xscale = 1.
        else:
            self.xscale = 1.

        if 'y-axis' in viewport:
            yaxis = viewport['y-axis']
            if 'scale' in yaxis:
                self.yscale = yaxis.pop('scale')
            else:
                self.yscale = 1.
        else:
            self.yscale = 1.

        self.variables = viewport.pop('variables')
        self.lines = []
        idx = self._getTimeIndex(common.t)
        for v in self.variables:
            if 'color' not in v:
                v['color'] = common.COLORS[self._clr_idx % len(common.COLORS)]
                self._clr_idx = self._clr_idx + 1
            args = common.remap(v, self.LINE_MAP)
            var_name = args.pop('name')
            args['append'] = False
            line = chigger.graphs.Line(**args)

            self.data.update(time = idx)
            x = self.data['arc_length'].multiply(self.xscale).tolist()
            y = self.data[var_name].multiply(self.yscale).tolist()

            line.setOptions(x = x, y = y)
            self.lines.append(line)

        self.graph = chigger.graphs.Graph(*self.lines, viewport = viewport['viewport'])

        if 'legend' in viewport:
            legend = viewport['legend']
            args = common.remap(legend, common.LEGEND_MAP)
            self.graph.setOptions('legend', **args)

        if 'x-axis' in viewport:
            xaxis = viewport['x-axis']
            args = common.remapPlotAxis(xaxis)
            self.graph.setOptions('xaxis', **args)

        if 'y-axis' in viewport:
            yaxis = viewport['y-axis']
            args = common.remapPlotAxis(yaxis)
            self.graph.setOptions('yaxis', **args)

    def result(self):
        return self.graph

    def update(self, time):
        idx = self._getTimeIndex(time)

        for v, line in zip(self.variables, self.lines):
            var_name = v['name']
            self.data.update(time = idx)
            x = self.data['arc_length'].multiply(self.xscale).tolist()
            y = self.data[var_name].multiply(self.yscale).tolist()
            line.setOptions(x = x, y = y)

    def _getTimeIndex(self, time):
        n = len(common.times)
        idx = bisect.bisect_right(common.times, time) - 1
        if idx < 0:
            idx = 0
        elif idx > n:
            idx = -1
        return idx


class ViewportPlotOverTime(Viewport):
    """
    Plot over time
    """

    MAP = {
        'x-axis': 'xaxis',
        'y-axis': 'yaxis'
    }

    def __init__(self, viewport):
        super(ViewportPlotOverTime, self).__init__(viewport)

        self._clr_idx = 0

        if 'viewport' not in viewport:
            viewport['viewport'] = [0, 0, 1, 1]
        common.checkMandatoryArgs(['variables'], viewport)

        # if v['file'] is CSV
        self.csv = mooseutils.PostprocessorReader(viewport['file'])

        # remap global time to local time (i.e this plot's time)
        data_x = self.csv['time'].tolist()
        if common.times is None:
            self.times = [i * common.time_unit for i in data_x]
        else:
            self.times = []
            for t in common.times:
                self.times.append(t * common.time_unit)

        # Minimum and maximum value determined from the read data. Used if 'range' for y-axis is not specified
        self.min_val = 0
        self.max_val = 0

        self.lines = []
        self.values = []
        for var in viewport['variables']:
            if 'color' not in var:
                var['color'] = common.COLORS[self._clr_idx % len(common.COLORS)]
                self._clr_idx = self._clr_idx + 1

            if 'scale' in var:
                scale = var.pop('scale')
            else:
                scale = 1.

            var_name = var.pop('name')
            data_y = self.csv[var_name].multiply(scale).tolist()

            if common.times is None:
                vals = data_y
            else:
                vals = []
                linipol = common.LinearInterpolation(data_x, data_y)
                for t in common.times:
                    v = linipol(t)
                    vals.append(v)
            self.values.append(vals)

            self.min_val = min(self.min_val, min(vals))
            self.max_val = max(self.max_val, max(vals))

            line = chigger.graphs.Line(x_data = self.times, y_data = vals, append = False, **var)
            self.lines.append(line)

        self.graph = chigger.graphs.Graph(*self.lines, viewport = viewport['viewport'])

        if 'x-axis' in viewport:
            xaxis = viewport['x-axis']
            if 'range' not in xaxis:
                xaxis['range'] = [round(self.times[0], 1), round(self.times[-1], 1)]
            xaxis_args = common.remapPlotAxis(xaxis)
            self.graph.setOptions('xaxis', **xaxis_args)

        if 'y-axis' in viewport:
            yaxis = viewport['y-axis']
            if 'range' not in yaxis:
                yaxis['range'] = [round(self.min_val, 1), round(self.max_val, 1)]
            yaxis_args = common.remapPlotAxis(yaxis)
            self.graph.setOptions('yaxis', **yaxis_args)

    def result(self):
        return self.graph

    def update(self, time):
        n = self.times.index(time * common.time_unit)
        for i, ln in enumerate(self.lines):
            ln.setOptions(x = self.times[:n], y = self.values[i][:n])


def _buildViewport(viewport):
    """
    Take a viewport structure and build a chigger object from it
    """
    cls_name = 'Viewport' + viewport['type']
    if cls_name in globals():
        cls = globals()[cls_name]
        del viewport['type']
        return cls(viewport)
    else:
        return None


def process(viewports):
    """
    Process the viewports
    """

    objs = []
    for viewport in viewports:
        if 'type' in viewport:
            obj = _buildViewport(viewport)
            if obj != None:
                objs.append(obj)

                times = obj.times()
                if times != None and common.times == None:
                    common.times = times
        else:
            print("No 'type' defined in viewport. Skipping...")
    return objs
