import vtk

# array of times for which we produce plots over time and movies
times = None
t = None
timestep = -1

# for using different time units
time_unit = 1
time_unit_str = 'seconds'

# map for remapping axis arguments
AXIS_MAP = {
    'axis-visible': 'axis_visible',
    'font-size': 'font_size',
    'font-color': 'font_color',
    'grid-color': 'grid_color',
    'labels-visible': 'labels_visible',
    'range': 'lim',
    'num-ticks': 'num_ticks',
    'ticks-visible': 'ticks_visible',
    'scale': 'axis_scale'
}

LEGEND_MAP = {
    'halign': 'horizontal_alignment',
    'valign': 'vertical_alignment',
    'position': 'point',
    'label-color': 'label_color',
    'label-font-size': 'label_font_size',
    'border-color': 'border_color',
    'border-opacity': 'border_opacity',
    'border-width': 'border_width'
}

def remapPlotAxis(args):
    return remap(args, AXIS_MAP)

def remap(args, map):
    remapped_args = {}
    for p in args:
        if p in map:
            remapped_args[map[p]] = args[p]
        else:
            remapped_args[p] = args[p]
    return remapped_args

def setTimeUnit(unit):
    """
    Method for setting a time unit

    Args:
        unit = ['sec', 'min', 'hour', 'day']
    """
    global time_unit
    global time_unit_str

    if unit == 'sec':
        time_unit = 1.
        time_unit_str = 'seconds'
    elif unit == 'min':
        time_unit = 1. / 60
        time_unit_str = 'minutes'
    elif unit == 'hour':
        time_unit = 1. / 3600
        time_unit_str = 'hours'
    elif unit == 'day':
        time_unit = 1. / 86400
        time_unit_str = 'days'
    else:
        raise SystemExit("Unsupported 'time-unit' specified.")

def formatTimeStr(format_str, time):
    global time_unit
    global time_unit_str

    if format_str == None:
        return 'Time: {:1.2f} {}'.format(time * time_unit, time_unit_str)
    else:
        return 'Time: {} {}'.format(format_str, time_unit_str).format(time * time_unit)

def buildCamera(args):
    """
    Build a VTK camera object
    """
    view_up = args.pop('view-up')
    position = args.pop('position')
    focal_point = args.pop('focal-point')

    camera = vtk.vtkCamera()
    camera.SetViewUp(view_up[0], view_up[1], view_up[2])
    camera.SetPosition(position[0], position[1], position[2])
    camera.SetFocalPoint(focal_point[0], focal_point[1], focal_point[2])
    return camera

def checkMandatoryArgs(args, data):
    for arg in args:
        if arg not in data:
            raise SystemExit("No '{}' defined in '{}' viewport.".format(arg, __name__))


class LinearInterpolation:
    """
    Fairly simple (and also stupid) linear interpolation class that behaves like a callable funtion
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __call__(self, x):
        if x <= self.x[0]:
            return self.y[0]
        if x >= self.x[len(self.x) - 1]:
            return self.y[len(self.y) - 1]

        for i in range(len(self.x) - 1):
            if (x >= self.x[i]) and (x < self.x[i + 1]):
                return self.y[i] + (self.y[i + 1] - self.y[i]) * (x - self.x[i]) / (self.x[i + 1] - self.x[i]);
