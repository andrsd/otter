#

import os
import sys
import chigger
import relap7
import numpy
import common
import viewports
import colorbars
import annotations


def render(obj):
    """
    Render a frame or a movie
    """

    if 'times' in obj:
        movie(obj)
    else:
        frame(obj)


def frame(frame):
    """
    Renders a single frame
    """
    common.checkMandatoryArgs(['size', 't'], frame)

    if 't' in frame:
        common.t = frame['t']
        common.timestep = None
    if 'time-unit' in frame:
        common.setTimeUnit(frame['time-unit'])

    items, results = _buildResults(frame)

    window = chigger.RenderWindow(
        *results,
        size = frame['size'],
        chigger = True)

    if 'output' in frame:
        window.write(frame['output'])
    else:
        window.start()


def movie(movie):
    """
    Renders a movie
    """
    common.checkMandatoryArgs(['size', 'file', 'duration', 'location', 'frame'], movie)

    if 'time-unit' in movie:
        common.setTimeUnit(movie['time-unit'])
    common.times = movie.pop('times')
    common.t = 0
    location = movie.pop('location')
    frame = movie.pop('frame')

    if not os.path.isdir(location):
        raise SystemExit("Directory {} does not exists.".format(location))

    if frame.find('*') != -1:
        filename = frame.replace("*", "{:04d}")
    else:
        raise SystemExit("The 'frame' parameter needs to contain '*'.")

    items, results = _buildResults(movie)

    window = chigger.RenderWindow(
        *results,
        size = movie['size'],
        chigger = True)

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
        '{}/{}'.format(location, movie['file']),
        duration = movie['duration'],
        num_threads = 12)


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
