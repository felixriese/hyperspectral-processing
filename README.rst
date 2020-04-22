.. image:: https://api.codacy.com/project/badge/Grade/94144b07a2114b7b8777ddec80485fe9
    :target: https://www.codacy.com/manual/felixriese/hyperspectral-processing?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=felixriese/hyperspectral-processing&amp;utm_campaign=Badge_Grade
    :alt: Codacy
.. image:: https://travis-ci.org/felixriese/hyperspectral-processing.svg?branch=master
    :target: https://travis-ci.org/felixriese/hyperspectral-processing
    :alt: Travis CI
.. image:: https://codecov.io/gh/felixriese/hyperspectral-processing/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/felixriese/hyperspectral-processing
    :alt: Codecov
.. image:: https://readthedocs.org/projects/hyperspectral-processing/badge/?version=latest
    :target: https://hyperspectral-processing.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Hyperspectral Processing Scripts for the HydReSGeo Dataset
============================================================

This repository includes the processing scripts of the HydReSGeo dataset
for the hyperspectral, LWIR, and soil moisture data.

:License:
    `3-Clause BSD license <LICENSE>`_

:Author:
    `Felix M. Riese <mailto:github@felixriese.de>`_

:Requirements:
    Python 3 with these `packages <requirements.txt>`_

:Citation:
    see `Citation`_ and in the `bibtex <bibliography.bib>`_ file

:Documentation:
    `Documentation <https://hyperspectral-processing.readthedocs.io/en/latest/>`_

Sensors
--------

- **Hyperspectral sensors:** Cubert UHD 285 (VNIR), FLIR Tau2 640 (LWIR), ASD FieldSpec 4 Sensors (VNIR & SWIR)
- **Hydrological sensor:** IMKO Pico32 (TDR)

Exemplary notebooks
--------------------

- `Example_Plots.ipynb <notebooks/Example_Plots.ipynb>`_
- `Process_HydReSGeo_Dataset.ipynb <notebooks/Process_HydReSGeo_Dataset.ipynb>`_

Citation
---------------------------------------

**Code:**

[1] F. M. Riese, "Hyperspectral Processing Scripts for HydReSGeo Dataset,"
Zenodo, 2020. `DOI:10.5281/zenodo.3706418 <https://doi.org/10.5281/zenodo.3706418>`_

.. code:: bibtex

    @misc{riese2020hyperspectral,
        author = {Riese, Felix~M.},
        title = {{Hyperspectral Processing Scripts for the HydReSGeo Dataset}},
        year = {2020},
        DOI = {10.5281/zenodo.3706418},
        publisher = {Zenodo},
        howpublished = {\href{https://doi.org/10.5281/zenodo.3706418}{doi.org/10.5281/zenodo.3706418}}
    }

**Dataset:**

[2] S. Keller, F. M. Riese, N. Allroggen, and C. Jackisch, "HydReSGeo: Field
experiment dataset of surface-subsurface infiltration dynamics acquired by
hydrological, remote sensing, and geophysical measurement techniques," GFZ Data
Services, 2020. `DOI:10.5880/fidgeo.2020.015 <https://doi.org/10.5880/fidgeo.2020.015>`_

.. code:: bibtex

    @misc{keller2020hydresgeo,
        author = {Keller, Sina and Riese, Felix~M. and Allroggen, Niklas and
                  Jackisch, Conrad},
        title = {{HydReSGeo: Field experiment dataset of surface-subsurface
                  infiltration dynamics acquired by hydrological, remote
                  sensing, and geophysical measurement techniques}},
        year = {2020},
        publisher = {GFZ Data Services},
        DOI = {10.5880/fidgeo.2020.015},
    }

Code is Supplementary Material to
---------------------------------------

[3] S. Keller, F. M. Riese, N. Allroggen, C. Jackisch, and S. Hinz, “Modeling
subsurface soil moisture based on hyperspectral data: First results of a
multilateral field campaign,” in Tagungsband der 37. Wissenschaftlich-
Technische Jahrestagung der DGPF e.V., vol. 27, Munich, Germany, 2018, pp.
34–48. `Link <https://www.dgpf.de/src/tagung/jt2018/proceedings/proceedings/papers/07_PFGK18_Keller_et_al.pdf>`_

[4] S. Keller, F. M. Riese, J. Stötzer, P. M. Maier, and S. Hinz, “Developing
a machine learning framework for estimating soil moisture with VNIR
hyperspectral data,” ISPRS Annals of Photogrammetry, Remote Sensing and
Spatial Information Sciences, vol. IV-1, pp. 101–108, 2018.
`DOI:10.5194/isprs-annals-IV-1-101-2018 <https://doi.org/10.5194/isprs-annals-IV-1-101-2018>`_

[5] F. M. Riese and S. Keller, “Fusion of hyperspectral and ground penetrating
radar data to estimate soil moisture,” in 2018 9th Workshop on Hyperspectral
Image and Signal Processing: Evolution in Remote Sensing (WHISPERS), Amsterdam,
Netherlands, 2018, pp. 1–5. `DOI:10.1109/WHISPERS.2018.8747076 <https://arxiv.org/abs/1804.05273>`_

[6] S. Keller, Fusion hyperspektraler, LWIR- und Bodenradar-Daten mit
maschinellen Lernverfahren zur Bodenfeuchteschätzung, 5th ed. Wichmann, Berlin,
2019, p. 217–250.
