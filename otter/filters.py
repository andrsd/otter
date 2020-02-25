import chigger

def buildFilter(filter):
    """
    Builds a chigger filter
    """
    type = filter.pop('type')

    if type == 'plane-clip':
        return chigger.filters.PlaneClipper(**filter)
    elif type == 'box-clip':
        return chigger.filters.BoxClipper(**filter)
    elif type == 'transform':
        return chigger.filters.TransformFilter(**filter)
    else:
        return None
