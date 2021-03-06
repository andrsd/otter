#

VERSION = 1.0
COPYRIGHT = u"Copyright © 2020, David Andrš, All Rights Reserved"

import os
import sys
import re
import chigger
import tempfile
import time
import datetime

from . import config
from . import common
from . import viewports
from . import colorbars
from . import annotations

__testing__ = 'TRAVIS_CI' in os.environ

size = {
    '720p' : [1280, 720],
    '1080p' : [1920, 1080]
}

def render(obj):
    """
    Render an image or a movie
    """

    if 'duration' in obj:
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
    if 'layer' not in image:
        args['layer'] = 0
    if 'file' in image:
        args['offscreen'] = True
    window = chigger.RenderWindow(*results, **args)

    if 'file' in image:
        if not __testing__:
            window.write(image['file'])
            print("Wrote image into '{}'".format(image['file']))
    else:
        window.start()


def movie(movie):
    """
    Renders a movie
    """

    MOVIE_MAP = {}

    common.checkMandatoryArgs(['size', 'file', 'duration'], movie)

    if 'time-unit' in movie:
        common.setTimeUnit(movie['time-unit'])
    common.t = 0
    common.timestep = None

    if 'location' in movie:
        location = movie.pop('location')
        cleanup_dir = False
    else:
        location = tempfile.mkdtemp()
        cleanup_dir = True

    if 'frame' in movie:
        frame = movie.pop('frame')
    else:
        frame = 'frame_*.png'

    if not os.path.isdir(location):
        raise SystemExit("Directory {} does not exists.".format(location))

    if frame.find('*') != -1:
        filename = frame.replace("*", "{:04d}")
    else:
        raise SystemExit("The 'frame' parameter needs to contain '*'.")

    items, results = _buildResults(movie)

    # if 'times' are explicitly specified in the movie object, use those
    if 'times' in movie:
        common.times = movie.pop('times')
    if common.times == None or len(common.times) == 0:
        raise SystemExit("No times were specifed for rendering the movie.")

    args = common.remap(movie, MOVIE_MAP)
    args['chigger'] = True
    args['offscreen'] = True
    if 'layer' not in movie:
        args['layer'] = 0
    window = chigger.RenderWindow(*results, **args)

    t0 = time.time()
    time_remaining = 'unknown'
    pb_len = 65
    total = len(common.times)
    for i, t in enumerate(common.times):
        percent = ("{0:.2f}").format(100 * ((i + 1) / float(total)))
        filled_length = int(pb_len * i // (total - 1))
        bar = '#' * filled_length + ' ' * (pb_len - filled_length)
        print('\x1b[2K\r{}/{}: |{}| {}% complete, time remaining {}'.format(i + 1, total, bar, percent, time_remaining), end=' ')
        sys.stdout.flush()

        for item in items:
            item.update(t)

        if not __testing__:
            window.write("{}/{}".format(location, filename).format(i))
        t1 = time.time()
        avg_time_per_frame = (t1 - t0) / (i + 1)
        time_remaining = str(datetime.timedelta(seconds = round((total - i - 1) * avg_time_per_frame)))
    print()

    if not __testing__:
        chigger.utils.img2mov(
            '{}/{}'.format(location, frame),
            movie['file'],
            duration = movie['duration'],
            num_threads = 12,
            overwrite = True)

    filename_re = frame.replace("*", ".*")
    for f in os.listdir(location):
        if re.search(filename_re, f):
            os.remove(os.path.join(location, f))
    if cleanup_dir:
        os.removedirs(location)


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
