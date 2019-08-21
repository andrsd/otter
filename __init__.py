#

import os
import sys
import re
import chigger
import common
import viewports
import colorbars
import annotations

size = {
    '720p' : [1280, 720],
    '1080p' : [1920, 1080]
}

def render(obj):
    """
    Render an image or a movie
    """

    if 'times' in obj:
        movie(obj)
    else:
        image(obj)


def image(image):
    """
    Renders a single image
    """

    IMAGE_MAP = {}

    common.checkMandatoryArgs(['size'], image)

    if 't' in image:
        common.t = image['t']
        common.timestep = None
    if 'time-unit' in image:
        common.setTimeUnit(image['time-unit'])

    items, results = _buildResults(image)

    args = common.remap(image, IMAGE_MAP)
    args['chigger'] = True
    if 'output' in image:
        args['offscreen'] = True
    window = chigger.RenderWindow(*results, **args)

    if 'output' in image:
        window.write(image['output'])
    else:
        window.start()


def movie(movie):
    """
    Renders a movie
    """

    MOVIE_MAP = {}

    common.checkMandatoryArgs(['size', 'file', 'duration', 'location', 'frame'], movie)

    if 'time-unit' in movie:
        common.setTimeUnit(movie['time-unit'])
    common.times = movie.pop('times')
    common.t = 0
    common.timestep = None
    location = movie.pop('location')
    frame = movie.pop('frame')

    if not os.path.isdir(location):
        raise SystemExit("Directory {} does not exists.".format(location))

    if frame.find('*') != -1:
        filename = frame.replace("*", "{:04d}")
    else:
        raise SystemExit("The 'frame' parameter needs to contain '*'.")

    items, results = _buildResults(movie)

    args = common.remap(movie, MOVIE_MAP)
    args['chigger'] = True
    args['offscreen'] = True
    window = chigger.RenderWindow(*results, **args)

    i = 0
    for t in common.times:
        print '\x1b[2K\rTime: {} ({} of {})'.format(t, i + 1, len(common.times)),
        sys.stdout.flush()

        for item in items:
            item.update(t)

        window.write("{}/{}".format(location, filename).format(i))
        i = i + 1
    print

    chigger.utils.img2mov(
        '{}/{}'.format(location, frame),
        movie['file'],
        duration = movie['duration'],
        num_threads = 12,
        overwrite = True)

    for f in os.listdir(location):
        if re.search(frame, f):
            os.remove(os.path.join(location, f))


def _buildResults(obj):
    """
    Build chigger result objects from the viewports, colorbars and annotations
    """

    items = []
    if 'viewports' in obj:
        items += viewports.process(obj['viewports'])
    if 'colorbars' in obj:
        items += colorbars.process(obj['colorbars'])
    if 'annotations' in obj:
        items += annotations.process(obj['annotations'])

    results = []
    for i in items:
        results.append(i.result())

    return items, results
