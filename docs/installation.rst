Installation
====================

.. role:: bash(code)
   :language: bash

.. role:: python(code)
   :language: python3

Dependencies
------------

Install Python 3, e.g. via `Anaconda <https://www.anaconda.com>`_.

Install the required packages with conda:

.. code:: bash

    conda install --file requirements.txt

Or install the required packages with pip:

.. code:: bash

    pip install -r requirements.txt

Install latest development version
----------------------------------

The module does not need to be installed. It can be run directly from the
downloaded folder. If you want to easily import it into your code, try:

.. code:: bash

    git clone https://github.com/felixriese/hyperspectral-processing.git
    cd hyperspectral-processing/
    python setup.py install

And to import:

.. code:: python3

    import hprocessing
