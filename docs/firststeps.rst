First Steps
====================


.. role:: bash(code)
   :language: bash

.. role:: python(code)
   :language: python3

Process the HydReSGeo Dataset
-----------------------------

The first steps can be found in this `Process_HydReSGeo_Dataset.ipynb
<https://github.com/felixriese/hyperspectral-processing/blob/master/notebooks/Process_HydReSGeo_Dataset.ipynb>`_.

First, import the modules. Afterwards, run the automatic processing function
:bash:`processHydReSGeoDataset()` with the paths which need to be adapted to
your local paths. In the config file, the necessary paths and options need to
be set.

.. code:: python3

    from hprocessing.ProcessFullDataset import processHydReSGeoDataset

    output_df = processHydReSGeoDataset(
        config_path="config/HydReSGeo.ini",
        data_directory="data/HydReSGeo/")

The pandas DataFrame :bash:`output_df` includes all processed data.

Example Plots
-------------

Exemplary plots can be found in this `Example_Plots.ipynb
<https://github.com/felixriese/hyperspectral-processing/blob/master/notebooks/Example_Plots.ipynb>`_.

.. todo:: Add exemplary plots.
