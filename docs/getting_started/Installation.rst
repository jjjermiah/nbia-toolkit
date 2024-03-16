Installation
____________

`nbiatoolkit` is currently under development and is not guaranteed to be stable.
Please refer to the `1.0.0 Stable Release Milestone <https://github.com/jjjermiah/nbia-toolkit/milestone/1>`_
for the roadmap to the first stable release.

PyPi Installation
~~~~~~~~~~~~~~~~~

The easiest way to install `nbiatoolkit` is to use `pip` to install it from the
`Python Package Index (PyPi) <https://pypi.org/project/nbiatoolkit/>`_.

.. code-block:: console

    $ pip install nbiatoolkit

***NOTE: It is recommended that you install the package in a conda or virtual environment.***

Conda Installation
~~~~~~~~~~~~~~~~~~

Though the package is not available on conda, you can create a conda environment and install the package using pip:

.. code-block:: console

    $ conda create -n nbia python=3.12
    $ conda activate nbia
    $ pip install nbiatoolkit

Virtual Environment Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you prefer to use a virtual environment, you can create one and install the package using pip:

.. code-block:: console

    $ python3 -m venv nbia
    $ source nbia/bin/activate
    $ pip install nbiatoolkit
