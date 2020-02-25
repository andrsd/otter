Object Parameters
==================

Image
-----

.. code-block:: python

  image = {
    'size': [ float, float],
    't', float,
    'time-unit': {'sec', 'min', 'hour', 'day'},
    'output': str,
    'background': [float, float, float],
    'gradient_background': bool,
    'background2': [float, float, float],
    'viewports': list,
    'colorbars': list,
    'annotations': list
  }

:size: *width* and *height* of the image - either on screen of the physical size of the rendered image.

:t: simulation time the image is rendered for.

:time-unit: Time unit -- used globally. For example, time annotation will pick this value.

:output: If specified, render into a file, otherwise render on screen in an interactive window.

:background: An array of three numbers between ``0`` and ``1`` where each entry represents red, green and blue component.

:gradient_background: If ``True``, then the ``background2`` parameter is used and a linear background is rendered.

:background2: Used if ``gradient_background`` is True.

:viewports: List of :ref:`viewports`.

:colorbars: List of :ref:`colorbar` s.

:annotations: List of :ref:`annotations`.

Movie
-----

.. code-block:: python

  movie = {
    'duration': float,
    'file': str,
    'size': [1280, 720],
    'times': [],
    'time-unit': 'min',
    'background': [float, float, float],
    'gradient_background': bool,
    'background2': [float, float, float],
    'viewports': list,
    'colorbars': list,
    'annotations': list
  }

:duration: Duration in seconds of the final rendered movie.

:file: File name of the final movie.

:size: *width* and *height* of the movie.

:times: List of times for which we render the images. If not specified, time steps from the result file will be used.

:time-unit: Time unit -- used globally. For example, time annotation will pick this value.

:background: An array of three numbers between ``0`` and ``1`` where each entry represents red, green and blue component.

:gradient_background: If ``True``, then the ``background2`` parameter is used and a linear background is rendered.

:background2: Used if ``gradient_background`` is True.

:viewports: List of ``viewport`` s.

:colorbars: List of ``colorbar`` s.

:annotations: List of ``annotation`` s.

:frame: Optional. File name mask of rendered images.

:location: Optional. Location where the images are rendered. By default rendering happens in some temp location determined by the operation system.


.. _viewports:

Viewports
---------

Exodus Result
^^^^^^^^^^^^^

.. code-block:: python

  vp = {
    'type': 'ExodusResult',
  }


Plot Over Line
^^^^^^^^^^^^^^

.. code-block:: python

  vp = {
    'type': 'PlotOverLine',
  }


Vector Postprocessor Plot
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  text = {
    'type': 'VPPPlot',
  }


.. _colorbar:

Colorbar
--------

.. code-block:: python

  colorbar = {
    'location': { 'left' | 'top' | 'right' | 'bottom' },
    'origin': [float, float],
    'viewport': [float, float, float, float],
    'layer': int,
    'width': float,
    'length': float,
    'primary': axis,
    'secondary': axis,
  }

:location: Location of the numbers relative to the color bar.
:origin: Position of the color bar in the viewport.
:viewport: *left*, *bottom*, *right* and *top* of the viewport where this color bar is displayed.
:layer: Layer number.
:width: Width of the color bar relative to viewport.
:length: Length of the color bar relative to viewport.
:primary: Primary axis of the color bar.
:secondary: *Optional*. Secondary axis of the color bar.


.. _annotations:

Annotations
-----------

Text
^^^^

.. code-block:: python

  text = {
    'position': [float, float],
    'opacity': float,
    'color': [float, float, float],
    'shadow': bool,
    'halign': {'left' | 'center' | 'right'},
    'valign': {'bottom' | 'middle' | 'top'},
    'text': str,
    'font-size': float
  }

:position: The text position within the viewport, in relative coordinates.

:opacity: Set the text opacity.

:color: The text color.

:shadow: Toggle text shadow.

:halign: Set the font justification.

:valign: The vertical text justification.

:text: The text to display.

:font-size: The text font size.


Image
^^^^^

.. code-block:: python

  text = {
    'position': [float, float],
    'width': float,
    'halign': {'left' | 'center' | 'right'},
    'valign': {'bottom' | 'middle' | 'top'},
    'opacity': float,
    'scale': float,
    'file': str,
  }

:position: The position of the image center within the viewport, in relative coordinates.

:width: The logo width as a fraction of the window width, this is ignored if 'scale' option is set.

:halign: The position horizontal position alignment.

:valign: The position vertical position alignment.

:opacity: Set the image opacity.

:scale: The scale of the image. By default the image is scaled by the width.

:file: The PNG file to read, this can be absolute or relative path to a PNG or just the name of a PNG located in the ``chigger/logos`` directory.


Time
^^^^

.. code-block:: python

  time = {
    'position': [float, float],
    'opacity': float,
    'color': [float, float, float],
    'shadow': bool,
    'halign': {'left' | 'center' | 'right'},
    'valign': {'bottom' | 'middle' | 'top'},
    'text': str,
    'font-size': float,
    'format': str
  }

:position: The text position within the viewport, in relative coordinates.

:opacity: Set the text opacity.

:color: The text color.

:shadow: Toggle text shadow.

:halign: Set the font justification.

:valign: The vertical text justification.

:text: The text to display.

:font-size: The text font size.

:format: Formatting string for the time


.. _filters:

Filters
-------

Transform
^^^^^^^^^

.. code-block:: python

  transform = {
    'scale': [float, float, float]
  }

:scale: Scaling factor for x, y and z direction.


Plane Clip
^^^^^^^^^^

.. code-block:: python

  plane_clip = {
    'origin': [float, float, float],
    'normal': [float, float, float],
    'inside_out': bool
  }

:origin: The origin of the clipping plane.

:normal: The outward normal of the clipping plane.

:inside_out: When True the clipping criteria is reversed.


Box Clip
^^^^^^^^

.. code-block:: python

  plane_clip = {
    'lower': [float, float, float],
    'upper': [float, float, float],
    'inside_out': bool
  }

:lower: The lower corner of the clipping box.

:upper: The upper corner of the clipping box.

:inside_out: When True the clipping criteria is reversed.


.. _axis:

Axis
----

.. code-block:: python

  axis = {
    'num-ticks': int,
    'range': [float, float],
    'font-size': int,
    'font-color': [float, float, float],
    'title': str,
    'grid': bool,
    'grid-color': [float, float, float],
    'precision': int,
    'notation': { 'standard' | 'scientific' | 'fixed' | 'printf'},
    'ticks-visible': bool,
    'axis-visible': bool,
    'labels-visible': bool,
    'scale': float
  }

:num-ticks: The number of tick marks to place on the axis.
:range: The axis extents.
:font-size: The axis title and label font sizes, in points.
:font-color: The color of the axis, ticks, and labels.
:title: The axis label.
.. :title_font_size: The axis title font size, in points.
:grid: Show/hide the grid lines for this axis.
:grid-color: The color for the grid lines.
:precision: The axis numeric precision.
:notation: The type of notation, leave empty to let VTK decide. Can be 'standard', 'scientific', 'fixed', 'printf'.
:ticks-visible: Control visibility of tickmarks on colorbar axis.
.. :tick_font_size: The axis tick label font size, in points.
:axis-visible: Control visibility of axis line on colorbar axis.
.. :axis_position: Set the axis position (left, right, top, bottom).
.. :axis_point1: Starting location of axis, in absolute viewport coordinates.
.. :axis_point2: Ending location of axis, in absolute viewport coordinates.
.. :axis_scale: The axis scaling factor.
.. :axis_factor: Offset the axis by adding a factor.
.. :axis_opacity: The axis opacity.
.. :zero_tol: Tolerance for considering limits to be the same.
:labels-visible: Control visibility of the numeric labels.
:scale: Scale factor for the axis. Useful for changing units. For example, to go from *meters* to *centimeters* set this to *1e2*.

.. _camera:

Camera
------

.. code-block:: python

  camera = {
    'view-up': [float, float, float],
    'position': [float, float, float],
    'focal-point': [float, float, float]
  }

:view-up: ???
:position: The position of the camera.
:focal-point: The the focal point of the camera.
