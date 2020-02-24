Deploy AppBundle for Mac OS X
=============================

This page describes how to build and deploy and App bundle for MacOS X.

Setup environment
-----------------

.. code-block:: bash

  $ virtualenv venv
  $ . venv/bin/activate
  $ pip install -r requirements.txt


Mac OS X: Build icns
--------------------

.. code-block:: bash

  $ mkdir icon.iconset
  $ sips -z 512 512 otter.png --out icon.iconset/icon_512x512.png
  $ iconutil -c icns icon.iconset
  $ rm -rf icon.iconset

Build the bundle
----------------

.. code-block:: bash

  $ python setup.py py2app

Fix the install manually
------------------------

.. code-block:: bash

  $ cp /path/to/libffi.6.dylib /path/to/Otter.app/Contents/Frameworks/


Note: ``libffi.6.dylib`` can sit either on the system or in miniconda dir


NOTES
-----

- if package dependencies change, generate a new ``requirements.txt`` by running:

  .. code-block:: bash

    $ pip freeze > requirements.txt

Resources
---------

.. [py2app] https://py2app.readthedocs.io/en/latest/
.. [metachris] https://www.metachris.com/2015/11/create-standalone-mac-os-x-applications-with-python-and-py2app/
