Testing
=======

Tests are located in ``tests`` dir.


Commands
--------


To run tests:

.. code-block:: bash

  $ python -m unittest discover -s tests -v


To generate code coverage:

.. code-block:: bash

  $ coverage run -m unittest discover -s tests -v
  $ coverage html

Open ``htmlcov/index.html`` in your browser.
