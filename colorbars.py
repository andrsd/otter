import chigger
from . import common
from . import viewports

class ColorBar(object):
    """
    Color bar object
    """
    COLORBAR_MAP = {
        'origin': 'colorbar_origin',
        'num-colors': 'cmap_num_colors',
        'range': 'cmap_range',
        'axis1': 'primary',
        'axis2': 'secondary'
    }

    def __init__(self, colorbar):
        if 'primary' in colorbar:
            self.primary = colorbar.pop('primary')
        else:
            self.primary = None
        if 'secondary' in colorbar:
            self.secondary = colorbar.pop('secondary')
        else:
            self.secondary = None

        if self.primary == None and self.secondary == None:
            raise SystemExit("No 'primary' or 'secondary' specified in colorbar.")

        self.results = []
        self._processResult(self.primary, 'primary')
        self._processResult(self.secondary, 'secondary')

        args = common.remap(colorbar, self.COLORBAR_MAP)
        self.cbar = chigger.exodus.ExodusColorBar(*self.results, **args)
        if self.primary != None:
            args = common.remap(self.primary, common.AXIS_MAP)
            self.cbar.setOptions('primary', **args)
        if self.secondary != None:
            args = common.remap(self.secondary, common.AXIS_MAP)
            self.cbar.setOptions('secondary', **args)

    def _processResult(self, axis, txt):
        if axis != None:
            if 'result' not in axis:
                raise SystemExit("No 'result' specified in '{}' colorbar.".format(txt))
            name = axis['result']
            if name not in viewports.OBJECTS:
                raise SystemExit("No viewport with name '{}'.".format(name))
            obj = viewports.OBJECTS[name]
            # if not title was provided, take it from the linked result
            if 'title' not in axis:
                axis['title'] = obj['title']
            self.results.append(obj.result())

    def result(self):
        return self.cbar

    def update(self, time):
        pass

def process(colorbars):
    """
    Process the colorbars
    """
    objs = []
    for colorbar in colorbars:
        obj = ColorBar(colorbar)
        objs.append(obj)
    return objs
