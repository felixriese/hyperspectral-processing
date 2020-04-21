HydReSGeo Dataset
===================

.. role:: bash(code)
   :language: bash

.. role:: python(code)
   :language: python3

The HydReSGeo dataset is published in [HydReSGeo]_. In the following, the
file structure is described and the files in :bash:`rs/masks/` are summarized.


File structure
---------------

.. code:: bash

    ├── gpr
    │   ├── field_A
    │   │   ├── plot_A_2017-08-15T11:03:21+02.00.sgy
    │   │   └── ...
    │   └── ...
    ├── hyd
    │   ├── TDR.csv
    │   ├── bromide.csv
    │   ├── coresamples.csv
    │   ├── irrigation_protocol.txt
    │   ├── read_in_hydro_data.ipynb
    │   ├── sensor_pos.txt
    │   └── tensio.csv
    ├── rs
    │   ├── fieldspec.csv
    │   ├── hyp
    │   │   ├── 20170815_hyp_meas1
    │   │   │   ├── Auto000.cub
    │   │   │   ├── Auto000.cue
    │   │   │   ├── Auto000.hdr
    │   │   │   ├── Auto000.jpg
    │   │   │   ├── Auto000_PAN.tiff
    │   │   │   ├── Auto000_highres.hdr
    │   │   │   └── ...
    │   │   └── ...
    │   ├── lwir
    │   │   ├── ir_export_20170815_P0000004_000_12-23-22.csv
    │   │   └── ...
    │   └── masks
    │       ├── hyp_masks.csv
    │       ├── ignore_hyp_datapoints.csv
    │       ├── ignore_hyp_fields.csv
    │       ├── ignore_hyp_measurements.csv
    │       ├── meta_IR.txt
    │       ├── positions_IR.csv
    │       └── positions_hyp_lowres.csv
    ├── rs_masked
    └── site



File descriptions
----------------------

The file descriptions for the geophysical files (:bash:`gpr`), the hydrological
files (:bash:`hyd`), the remote sensing files (:bash:`rs/fieldspec.csv`,
:bash:`rs/hyp`, and :bash:`rs/lwir`), and the site files (:bash:`site`) are
described in [HydReSGeo]_.

Overall, we divide the hyperspectral data into folders, which include images
(= files = datapoints), which consist of different zones (= measurement
fields). In the following, the files in :bash:`rs/masks/` are described.

:bash:`hyp_masks.csv`
^^^^^^^^^^^^^^^^^^^^^^^

This file includes information about four wodden bars which are included in the
measurement area and should be masked. The columns are:

- :bash:`measurement`: Measurement folder name in the format
  :bash:`YYYYmmDD_meas[1-9]`.
- :bash:`start_row`, :bash:`end_row`, :bash:`start_col`, :bash:`end_col`: Start
  and end rows and columns for the mask.
- :bash:`bar[1-4]_p[1-2]_[x,y]`, :bash:`bar[1-4]_height`: Information about the
  geometry of the wodden bar. This is used in `ProcessEnviFile
  <ProcessEnviFile.rst>`_.

:bash:`ignore_hyp_datapoints.csv`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This file includes information about which hyperspectral images (datapoints)
need to be excluded for various reasons. The columns are:

- :bash:`measurement`: Measurement folder name in the format
  :bash:`YYYYmmDD_meas[1-9]`.
- :bash:`filenumber`: Number of the hyperspectral image in the respective
  measurement folder.

:bash:`ignore_hyp_fields.csv`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This file includes information about the zones/fields to be ignored in each
hyperspectral image due to several reasons: a GPR measurement within that field
at the same time, the irrigation platform, or a person walking through the
image. The columns are:

- :bash:`measurement`: Measurement folder name in the format
  :bash:`YYYYmmDD_meas[1-9]`.
- :bash:`filenumber`: Number of the hyperspectral image in the respective
  measurement folder.
- :bash:`zone`: Zone/field which needs to be ignored within the respective
  file. For the HydReSGeo dataset, eight zones are defined. They are numerated
  either as A1, A2, B1, B2, C1, C2, D1, and D4, or as zone1 to zone8 for
  technical reasons.

:bash:`ignore_hyp_measurements.csv`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This file includes information about which measurement folders to be ignored.
The column is:

- :bash:`measurement`: Measurement folder name in the format
  :bash:`YYYYmmDD_meas[1-9]`.

:bash:`meta_IR.csv`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This file is not important for this repository (for now) and can be ignored.

:bash:`positions_hyp_lowres.csv`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This file includes information about the eight different measurement zones
of the HydReSGeo dataset as well as the spectralon (= white reference) with
respect to the hyperspectral images. The columns are:

- :bash:`measurement`: Measurement folder name in the format
  :bash:`YYYYmmDD_meas[1-9]`.
- :bash:`spec_row_start`, :bash:`spec_row_end`, :bash:`spec_col_start`, and
  :bash:`spec_col_end`: Start and end rows and columns for the spectralon.
- :bash:`zone[1-8]_[row/column]_[start/end]`:  Start and end rows and columns
  for the eight measurement zones.

:bash:`positions_IR.csv`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This file includes information about the eight different measurement zones
of the HydReSGeo dataset with respect to the LWIR data. The columns are:

- :bash:`measurement`: Measurement folder name in the format
  :bash:`YYYYmmDD_meas[1-9]`.
- :bash:`zone[1-8]_[row/column]_[start/end]`:  Start and end rows and columns
  for the eight measurement zones.

Opening the CSV files
------------------------

The CSV files can be opened in :bash:`python3` with :bash:`pandas`:

.. code:: python3

      import pandas as pd

      df = pd.read_csv("hyp_masks.csv", sep="\s+")

References
-----------

.. [HydReSGeo] S. Keller, F. M. Riese, N. Allroggen, and C. Jackisch,
   "HydReSGeo: Field experiment dataset of surface-subsurface infiltration
   dynamics acquired by hydrological, remote sensing, and geophysical
   measurement techniques," GFZ Data Services, 2020.
   `DOI:10.5880/fidgeo.2020.015 <https://doi.org/10.5880/fidgeo.2020.015>`_
