Input file
==========

The basic structure of the input file is:

.. code-block:: python

  import otter

  viewports = [
    ...
  ]

  colorbars = [
    ...
  ]

  annotations = [
    ...
  ]

  obj = {
    ...
    'viewports': viewports,
    'colorbars': colorbars,
    'annotations': annotations
  }

  if __name__ == '__main__':
      otter.render(obj)


- The input file is an actual python file and can be used like that, i.e. it can be executed and it will produce the output file.

- ``viewports`` is a list of dictionaries and it specifies areas with results. Each entry specifies a single area.

- ``colorbars`` is a list of dictionaries and it specifies result's color bars. Typically for some result with a mesh. Each entry specifies one color bar.

- ``annotations`` is a list dictionaries and it specifies things like text, images, or time annotation. Each entry specifies one annotation.

- ``obj`` can be either an image or a movie.  The type is determined by listed parameters.

- As previously stated, each entry in ``viewports``, ``colorbars`` and ``annotations`` is a dictionary where the key is the name of a parameter and the value is its value.  Values can be of different types like ``int``, ``float``, ``list``, etc.
